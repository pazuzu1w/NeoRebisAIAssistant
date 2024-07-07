import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import threading
import logging

logger = logging.getLogger(__name__)

class EnhancedVectorDatabase:
    _local = threading.local()

    def __init__(self, db_path='enhanced_chatbot.db'):
        self.db_path = db_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

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
        self.get_connection().commit()

    def add_message(self, text):
        embedding = self.model.encode([text])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO messages (text, embedding) VALUES (?, ?)',
                       (text, embedding.tobytes()))
        self.get_connection().commit()

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