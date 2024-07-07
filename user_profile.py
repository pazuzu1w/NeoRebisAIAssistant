import json
from pathlib import Path

class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self.preferences = {}
        self.topics = {}
        self.profile_path = Path(f"profiles/{user_id}.json")
        self.load_profile()

    def load_profile(self):
        if self.profile_path.exists():
            with open(self.profile_path, 'r') as f:
                data = json.load(f)
                self.preferences = data.get('preferences', {})
                self.topics = data.get('topics', {})

    def save_profile(self):
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump({
                'preferences': self.preferences,
                'topics': self.topics
            }, f)

    def update_preference(self, key, value):
        self.preferences[key] = value
        self.save_profile()

    def update_topic(self, topic, importance):
        self.topics[topic] = importance
        self.save_profile()

    def get_preference(self, key, default=None):
        return self.preferences.get(key, default)

    def get_top_topics(self, n=5):
        return sorted(self.topics.items(), key=lambda x: x[1], reverse=True)[:n]