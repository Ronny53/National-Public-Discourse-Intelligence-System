from typing import List, Dict, Any

class EscalationRisk:
    def __init__(self):
        pass

    def calculate(self, 
                  sentiments: List[dict], 
                  emotions: Dict[str, float], 
                  burst_score: float, 
                  volume: int) -> Dict[str, Any]:
        """
        Calculates 0-100 Risk Score.
        """
        if not sentiments:
            return {"score": 0.0, "level": "Low"}

        # Factor 1: Negativity
        neg_ratio = sum(1 for s in sentiments if s['label'] == 'negative') / len(sentiments)
        
        # Factor 2: High Arousal Emotions (Anger + Fear)
        # emotion dict is {emotion: density}
        arousal_score = emotions.get('anger', 0) + emotions.get('fear', 0)
        # Normalize: assumes max density sum rarely exceeds 0.5-0.6 in normal text
        arousal_score = min(arousal_score * 2, 1.0) 

        # Factor 3: Burstiness (0-1)
        # Already passed in 0-1

        # Weighted calculation
        # Risk = Negativity (30%) + Arousal (30%) + Burst (40%)
        risk_val = (neg_ratio * 0.3) + (arousal_score * 0.3) + (burst_score * 0.4)
        
        score = round(risk_val * 100, 1)
        
        if score < 30:
            level = "Low"
        elif score < 60:
            level = "Moderate"
        elif score < 85:
            level = "High"
        else:
            level = "Critical"

        return {
            "score": score,
            "level": level,
            "drivers": {
                "negativity": round(neg_ratio, 2),
                "arousal": round(arousal_score, 2),
                "momentum": round(burst_score, 2)
            }
        }
