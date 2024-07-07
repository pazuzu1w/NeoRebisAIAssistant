import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import threading
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDatabase:
    _local = threading.local()

    def __init__(self, db_path='chatbot.db'):
        self.db_path = os.path.abspath(db_path)
        logger.info(f"Database path: {self.db_path}")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_connection(self):
        if not hasattr(self._local, 'conn'):
            logger.info(f"Creating new connection to {self.db_path}")
            self._local.conn = sqlite3.connect(self.db_path)
            self.create_table()
        return self._local.conn

    def create_table(self):
        cursor = self.get_connection().cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text TEXT NOT NULL,
                embedding BLOB NOT NULL
            )
        ''')
        self.get_connection().commit()
        logger.info("Table 'messages' created or already exists")

    def add_message(self, text):
        embedding = self.model.encode([text])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('INSERT INTO messages (text, embedding) VALUES (?, ?)',
                       (text, embedding.tobytes()))
        self.get_connection().commit()
        logger.info(f"Added message: {text[:20]}...")

    def search_similar(self, query, top_k=5):
        query_embedding = self.model.encode([query])[0]
        cursor = self.get_connection().cursor()
        cursor.execute('SELECT id, text, embedding FROM messages')
        results = []
        for row in cursor.fetchall():
            db_embedding = np.frombuffer(row[2], dtype=np.float32)
            similarity = np.dot(query_embedding, db_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(db_embedding))
            results.append((row[0], row[1], similarity))
        results.sort(key=lambda x: x[2], reverse=True)
        logger.info(f"Found {len(results)} similar messages")
        return results[:top_k]

    def close(self):
        if hasattr(self._local, 'conn'):
            self._local.conn.close()
            del self._local.conn
            logger.info("Closed database connection")

    def check_db_file(self):
        if os.path.exists(self.db_path):
            logger.info(f"Database file exists at {self.db_path}")
            return True
        else:
            logger.warning(f"Database file does not exist at {self.db_path}")
            return False