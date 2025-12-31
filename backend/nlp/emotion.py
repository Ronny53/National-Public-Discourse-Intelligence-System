from typing import Dict, List
import re

class EmotionAnalyzer:
    def __init__(self):
        # A small, hackathon-friendly lexicon for demonstration
        # In a real policy system, we would use the NRC Emotion Lexicon (25k words)
        self.lexicon = {
            "anger": ["hate", "angry", "rage", "furious", "mad", "stupid", "idiot", "destroy", "kill", "fight", "violenc", "protest", "riot"],
            "fear": ["scared", "afraid", "fear", "threat", "danger", "risk", "panic", "worry", "concern", "crisis", "crash", "collapse"],
            "joy": ["happy", "good", "great", "excellent", "love", "win", "success", "growth", "profit", "best", "develop", "progress"],
            "sadness": ["sad", "grief", "loss", "fail", "poor", "bad", "depress", "pain", "hurt", "suffer", "died", "dead"],
            "trust": ["believe", "faith", "support", "trust", "honest", "fact", "true", "agree", "confirm", "official", "government"]
        }

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Returns a probability-like distribution of emotions based on keyword density.
        """
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        total_words = len(words)
        
        if total_words == 0:
            return {emotion: 0.0 for emotion in self.lexicon}

        scores = {emotion: 0 for emotion in self.lexicon}
        
        for word in words:
            for emotion, keywords in self.lexicon.items():
                # Simple prefix matching for robustness (e.g., "violenc" matches "violence", "violent")
                for kw in keywords:
                    if word.startswith(kw):
                        scores[emotion] += 1
                        break

        # Normalize to 0-1 range based on density? Or just raw counts?
        # Let's return relative dominance.
        total_hits = sum(scores.values())
        if total_hits == 0:
            # If no keywords found, maybe return all zeros or uniform? 
            # All zeros implies "neutral" / "no detected emotion"
            return {emotion: 0.0 for emotion in self.lexicon}

        # Return distribution
        return {k: round(v / total_hits, 2) for k, v in scores.items()}
