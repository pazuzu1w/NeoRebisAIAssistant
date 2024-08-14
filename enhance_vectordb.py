import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import BartForConditionalGeneration, BartTokenizer
from summa import summarizer
from sklearn.cluster import KMeans
import threading
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class EnhancedVectorDatabase:
    _local = threading.local()



    def __init__(self, db_path='enhanced_chatbot.db'):
        self.db_path = os.path.abspath(db_path)
        logger.info(f"Database path: {self.db_path}")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.bart_model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')
        self.bart_tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

    def semantic_search(self, query, k=5):
        query_embedding = self.model.encode([query])[0]

        # Fetch all stored embeddings and their corresponding content
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT embedding, text FROM messages')
        stored_embeddings = []
        stored_content = []

        for row in cursor.fetchall():
            stored_embeddings.append(np.frombuffer(row[0], dtype=np.float32))
            stored_content.append(row[1])

        stored_embeddings = np.array(stored_embeddings)

        # Calculate cosine similarities
        similarities = cosine_similarity([query_embedding], stored_embeddings)[0]

        # Get top k results
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        results = [
            {"similarity": float(similarities[i]), "content": stored_content[i]}
            for i in top_k_indices
        ]

        return results


    def get_connection(self):
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self.create_tables()
        return self._local.conn

    def create_tables(self):
        cursor = self.get_connection().cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                embedding BLOB NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversation_summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                summary TEXT NOT NULL,
                embedding BLOB NOT NULL,
                start_time DATETIME NOT NULL,
                end_time DATETIME NOT NULL
            )
        ''')
        self.get_connection().commit()
    def add_message(self, text):
        embedding = self.model.encode([text])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO messages (text, embedding) VALUES (?, ?)',
                       (text, embedding.tobytes()))
        self.get_connection().commit()

    def create_conversation_summary(self, max_messages=100):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT text, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?', (max_messages,))
        messages = cursor.fetchall()
        default_summary = "No messages to summarize"
        if not messages:
            return  default_summary

        # Combine messages into a single text
        conversation_text = " ".join([msg[0] for msg in messages])

        # Use BART to create a summary
        inputs = self.bart_tokenizer([conversation_text], max_length=1024, return_tensors='pt', truncation=True)
        summary_ids = self.bart_model.generate(inputs['input_ids'], num_beams=4, max_length=150, early_stopping=True)
        summary = self.bart_tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        # Get start and end times
        start_time = messages[-1][1]  # Oldest message
        end_time = messages[0][1]  # Newest message

        # Store the summary
        self.add_conversation_summary(summary, start_time, end_time)

        return summary

    def add_conversation_summary(self, summary, start_time, end_time):
        embedding = self.model.encode([summary])[0]
        cursor = self.get_connection().cursor()
        cursor.execute(
            'INSERT INTO conversation_summaries (summary, embedding, start_time, end_time) VALUES (?, ?, ?, ?)',
            (summary, embedding.tobytes(), start_time, end_time))
        self.get_connection().commit()

    def get_latest_conversation_summary(self):
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT summary FROM conversation_summaries ORDER BY end_time DESC LIMIT 1')
        result = cursor.fetchone()
        return result[0] if result else None

    def create_summary(self, messages, method="tfidf", num_sentences=5):
        if method == "tfidf":
            return self.create_summary_tfidf(messages, num_sentences)
        elif method == "textrank":
            return self.create_summary_text_rank(messages, num_sentences)
        elif method == "bart":
            return self.create_summary_bart(messages, num_sentences)
        elif method == "clustering":
            return self.create_summary_clustering(messages, num_sentences)
        else:
            raise ValueError("Unsupported summarization method")

    def create_summary_tfidf(self, messages, num_sentences=3):
        text = " ".join(messages)
        sentences = text.split('. ')
        vectorizer = TfidfVectorizer().fit_transform(sentences)
        vectors = vectorizer.toarray()
        cosine_matrix = cosine_similarity(vectors)
        scores = cosine_matrix.sum(axis=1)
        ranked_sentences = [sentences[i] for i in np.argsort(scores, axis=0)[::-1]]
        summary = ". ".join(ranked_sentences[:num_sentences])
        return summary

    def create_summary_text_rank(self, messages, num_sentences=3):
        text = " ".join(messages)
        summary = summarizer.summarize(text, words=50)
        return summary

    def create_summary_bart(self, messages, num_sentences=3):
        model_name = 'facebook/bart-large-cnn'
        model = BartForConditionalGeneration.from_pretrained(model_name)
        tokenizer = BartTokenizer.from_pretrained(model_name)
        text = " ".join(messages)
        inputs = tokenizer([text], max_length=1024, return_tensors='pt', truncation=True)
        summary_ids = model.generate(inputs['input_ids'], num_beams=4, max_length=1024, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        return summary

    def create_summary_clustering(self, messages, num_sentences=5):
        text = " ".join(messages)
        sentences = text.split('. ')
        vectorizer = TfidfVectorizer().fit_transform(sentences)
        vectors = vectorizer.toarray()
        kmeans = KMeans(n_clusters=num_sentences, random_state=0).fit(vectors)
        cluster_centers = kmeans.cluster_centers_
        closest = np.argsort(cosine_similarity(cluster_centers, vectors), axis=1)
        summary = ". ".join([sentences[i] for i in closest[:, -1]])
        return summary

    def search_similar(self, query, top_k=5):
        query_embedding = self.model.encode([query])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, text, embedding FROM messages ORDER BY timestamp DESC LIMIT 1000')
        results = []
        for row in cursor.fetchall():
            db_embedding = np.frombuffer(row[2], dtype=np.float32)
            similarity = cosine_similarity([query_embedding], [db_embedding])[0][0]
            results.append((row[0], row[1], similarity))
        results.sort(key=lambda x: x[2], reverse=True)
        logger.info(f"Found {len(results)} similar messages")
        print(results[:top_k])
        return results[:top_k]

    def add_summary(self, summary, start_time, end_time):
        embedding = self.model.encode([summary])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO summaries (summary, embedding, start_time, end_time) VALUES (?, ?, ?, ?)',
                       (summary, embedding.tobytes(), start_time, end_time))
        self.get_connection().commit()

    def get_relevant_summaries(self, query, top_k=3):
        query_embedding = self.model.encode([query])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, summary, embedding FROM summaries')
        results = []
        for row in cursor.fetchall():
            db_embedding = np.frombuffer(row[2], dtype=np.float32)
            similarity = cosine_similarity([query_embedding], [db_embedding])[0][0]
            results.append((row[0], row[1], similarity))
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn
