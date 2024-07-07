class PersonalityTraits:
    def __init__(self):
        self.traits = {
            "formality": 0.5,  # 0: very casual, 1: very formal
            "humor": 0.5,      # 0: always serious, 1: very humorous
            "empathy": 0.5,    # 0: matter-of-fact, 1: very empathetic
            "creativity": 0.5, # 0: straightforward, 1: very creative
            "assertiveness": 0.5, # 0: passive, 1: very assertive
        }

    def set_trait(self, trait, value):
        if trait in self.traits and 0 <= value <= 1:
            self.traits[trait] = value

    def get_trait(self, trait):
        return self.traits.get(trait, 0.5)

    def get_personality_prompt(self):
        prompts = [
            f"Be {'very formal' if self.traits['formality'] > 0.7 else 'casual' if self.traits['formality'] < 0.3 else 'moderately formal'} in your responses.",
            f"{'Use humor frequently' if self.traits['humor'] > 0.7 else 'Be mostly serious' if self.traits['humor'] < 0.3 else 'Use occasional humor'} in your interactions.",
            f"{'Show strong empathy' if self.traits['empathy'] > 0.7 else 'Be matter-of-fact' if self.traits['empathy'] < 0.3 else 'Show moderate empathy'} in your responses.",
            f"{'Be highly creative' if self.traits['creativity'] > 0.7 else 'Be straightforward' if self.traits['creativity'] < 0.3 else 'Be moderately creative'} in your answers.",
            f"{'Be very assertive' if self.traits['assertiveness'] > 0.7 else 'Be gentle and passive' if self.traits['assertiveness'] < 0.3 else 'Be moderately assertive'} in your communication."
        ]
        return " ".join(prompts)

class PersonalityManager:
    def __init__(self):
        self.personality = PersonalityTraits()

    def update_personality(self, trait, value):
        self.personality.set_trait(trait, value)

    def get_personality_prompt(self):
        return self.personality.get_personality_prompt()