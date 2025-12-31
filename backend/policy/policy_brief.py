from typing import Dict, Any, List

class PolicyBriefGenerator:
    def __init__(self):
        # Responsibility Mapper: Maps issues to ministries
        self.responsibility_map = {
            "infrastructure": "Ministry of Road Transport and Highways",
            "education": "Ministry of Education",
            "environment": "Ministry of Environment, Forest and Climate Change",
            "payment": "Ministry of Finance / RBI",
            "digital": "MeitY",
            "health": "Ministry of Health and Family Welfare",
            "water": "Ministry of Jal Shakti"
        }

    def generate_brief(self, summary: Dict[str, Any], top_issues: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a policy brief based on current dashboard state.
        """
        # 1. Executive Summary
        risk =Summary(summary)
        
        # 2. Key Actions
        actions = []
        if risk['level'] in ["High", "Critical"]:
            actions.append("Immediate: Deploy strategic comms to address rising volatility.")
            actions.append("Immediate: Verify coordinated amplification vectors.")
        else:
            actions.append("Monitor: Maintain surveillance on emerging issues.")

        # 3. Responsible Institutions
        institutions = set()
        for issue in top_issues:
            # Simple keyword matching for demo
            text = issue['label'].lower() + " " + " ".join(issue['top_keywords'])
            for key, ministry in self.responsibility_map.items():
                if key in text:
                    institutions.add(ministry)
        
        if not institutions:
            institutions.add("Prime Minister's Office (General Oversight)")

        return {
            "executive_summary": f"National discourse risk is currently {risk['level']} (Score: {risk['score']}). Trust Index is {summary['trust_index']}. Primary drivers are {risk['drivers']}.",
            "recommended_actions": actions,
            "responsible_ministries": list(institutions),
            "generated_at": str(datetime.now())
        }

from datetime import datetime
def Summary(summary):
   return summary['escalation_risk']
