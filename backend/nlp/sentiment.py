from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Dict, Any

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes text and returns sentiment scores.
        """
        if not text:
            return {"compound": 0.0, "pos": 0.0, "neu": 0.0, "neg": 0.0, "label": "neutral"}

        scores = self.analyzer.polarity_scores(text)
        compound = scores['compound']

        if compound >= 0.05:
            label = "positive"
        elif compound <= -0.05:
            label = "negative"
        else:
            label = "neutral"

        return {
            "compound": compound,
            "pos": scores['pos'],
            "neu": scores['neu'],
            "neg": scores['neg'],
            "label": label
        }
