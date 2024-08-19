import json
import redis
import hashlib
import logging

from utils.utils import check_filesystem

class RedisHelper:
    def __init__(self, host: str, port: int, db: int):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def save_to_redis(self, pdf_id: str, pdf_data: dict):
        try:
            self.redis_client.set(pdf_id, json.dumps(pdf_data))
            return True
        except redis.RedisError:
            return False

    @staticmethod
    def generate_question_hash(question: str) -> str:
        return hashlib.sha256(question.encode()).hexdigest()

    def get_cached_answer(self, pdf_id: str, question: str):
        try:
            question_hash = self.generate_question_hash(question)
            key = f"{pdf_id}:{question_hash}"
            return self.redis_client.get(key)
        except redis.exceptions.ConnectionError:
            logging.warning("Failed to connect to Redis. Api call will be made")
            return None

    def cache_answer(self, pdf_id: str, question: str, answer: str):
        try:
            question_hash = self.generate_question_hash(question)
            key = f"{pdf_id}:{question_hash}"
            self.redis_client.set(key, answer) # Cache for 24 hours
        except redis.exceptions.ConnectionError:
            logging.warning("Failed to connect to Redis. Answer will not be cached")

    def get_pdf_data(self, pdf_id: str):
        pdf_data = None
        try:
            pdf_data_json = self.redis_client.get(pdf_id)
            if pdf_data_json:
                pdf_data = json.loads(pdf_data_json)
        except redis.RedisError:
            logging.warning("Failed to connect to Redis. Trying to load from filesystem")

        if not pdf_data:
            pdf_data = check_filesystem(pdf_id)

        return pdf_data
