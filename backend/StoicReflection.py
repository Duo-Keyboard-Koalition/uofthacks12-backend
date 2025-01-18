class StoicReflection:
    def __init__(self):
        self.control = {}
        self.virtue = {}
        self.emotional_resilience = {}
        self.broader_context = {}

    def set_control(self, situation, is_within_control):
        """Set whether a situation is within your control."""
        self.control[situation] = is_within_control

    def evaluate_virtue(self, action, virtue):
        """Evaluate if an action aligns with your virtues."""
        self.virtue[action] = virtue

    def reflect_on_emotion(self, emotion, situation):
        """Reflect on an emotion in relation to a situation."""
        self.emotional_resilience[emotion] = {
            'situation': situation,
            'rational_thought': f"How can I view this emotion rationally?"
        }

    def broaden_context(self, situation):
        """Provide a broader perspective on a situation."""
        return f"Consider how small this situation is in the grand scheme of life."

    def self_reflection_questions(self):
        """Return self-reflection questions for personal growth."""
        questions = [
            "Am I following my morals?",
            "Am I open to myself?",
            "Am I living in the moment?"
        ]
        return questions


# Example Usage
stoic_reflection = StoicReflection()

# Set control examples
stoic_reflection.set_control("Job loss", False)
stoic_reflection.set_control("Response to criticism", True)

# Evaluate virtue examples
stoic_reflection.evaluate_virtue("Helping a friend", "Compassion")
stoic_reflection.evaluate_virtue("Staying honest", "Integrity")

# Reflect on emotions
stoic_reflection.reflect_on_emotion("Anxiety", "Upcoming presentation")
stoic_reflection.reflect_on_emotion("Sadness", "Loss of a loved one")

# Broaden context example
context_message = stoic_reflection.broaden_context("Feeling overwhelmed")
print(context_message)

# Self-reflection questions
questions = stoic_reflection.self_reflection_questions()
for question in questions:
    print(question)
