import json
from pathlib import Path

class UserProfile:
    def __init__(self, user_id):
        self.user_id = user_id
        self. first_name = {}
        self.last_name = {}
        self.alias = {}
        self.bio = {}
        self.core_values = {}
        self.primary_motivations = {}
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
                self.first_name = data.get('first_name', {})
                self.last_name = data.get('last_name', {})
                self.alias = data.get('alias', {})
                self.bio = data.get('bio', {})
                self.core_values = data.get('core_values', {})
                self.primary_motivations = data.get('primary_motivations', {})


    def save_profile(self):
        self.profile_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.profile_path, 'w') as f:
            json.dump({
                'preferences': self.preferences,
                'topics': self.topics,
                'first_name': self.first_name,
                'last_name': self.last_name,
                'alias': self.alias,
                'bio': self.bio,
                'core_values': self.core_values,
                'primary_motivations': self.primary_motivations

            }, f)

    def update_preference(self, key, value):
        self.preferences[key] = value
        self.save_profile()

    def update_topic(self, topic, importance):
        self.topics[topic] = importance
        self.save_profile()

    def update_first_name(self, key, value):
        self.first_name[key] = value
        self.save_profile()


    def update_last_name(self, key, value):
        self.last_name[key] = value
        self.save_profile()


    def update_alias(self, key, value):
        self.alias[key] = value
        self.save_profile()


    def update_bio(self, key, value):
        self.bio[key] = value
        self.save_profile()


    def update_core_values(self, core_value , importance):
        self.core_values[core_value] = importance
        self.save_profile()


    def update_primary_motivations(self, primary_motivation, importance):
        self.primary_motivations[primary_motivation] = importance
        self.save_profile()


    def get_preference(self, key, default=None):
        return self.preferences.get(key, default)


    def get_top_topics(self, n=5):
        return sorted(self.topics.items(), key=lambda x: x[1], reverse=True)[:n]


    def get_first_name(self, key, default=None):
        return self.first_name.get(key, default)


    def get_last_name(self, key, default=None):
        return self.last_name.get(key, default)


    def get_alias(self, key, default=None):
        return self.alias.get(key, default)



    def get_bio(self, key, default=None):
        return self.bio.get(key, default)

    def get_core_values(self, n=5):
        return sorted(self.core_values.items(), key=lambda x: x[1], reverse=True)[:n]


    def get_primary_motivations(self, n=5):
        return sorted(self.primary_motivations.items(), key=lambda x: x[1], reverse=True)[:n]
