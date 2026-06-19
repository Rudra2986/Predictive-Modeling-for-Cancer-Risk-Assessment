import re

class AssessmentGuidanceService:
    def __init__(self):
        # List of approved field and parameter guide responses
        self.guidance_topics = [
            {
                "patterns": [
                    r"smoking\s+(score|habits|index)",
                    r"what\s+should\s+i\s+enter\s+for\s+smoking",
                    r"smoking\s+intensity",
                    r"smoking\s+frequency"
                ],
                "response": (
                    "Enter a value that best represents the patient's smoking habits. "
                    "Higher values indicate greater smoking exposure."
                )
            },
            {
                "patterns": [
                    r"alcohol\s+(consumption|use|habits|index)",
                    r"what\s+does\s+alcohol\s+consumption\s+mean"
                ],
                "response": (
                    "This field measures the patient's alcohol usage level. "
                    "Higher values represent more frequent or greater alcohol consumption."
                )
            },
            {
                "patterns": [
                    r"family\s+history",
                    r"what\s+should\s+i\s+enter\s+for\s+family\s+history",
                    r"what\s+does\s+family\s+history\s+mean"
                ],
                "response": (
                    "Family history refers to whether close biological relatives have had cancer "
                    "or related conditions. Enter the value that best matches the patient's history."
                )
            },
            {
                "patterns": [
                    r"physical\s+activity",
                    r"what\s+is\s+physical\s+activity\s+level"
                ],
                "response": (
                    "Physical activity level represents how active the patient is during daily life "
                    "and exercise. Higher values indicate greater activity levels."
                )
            },
            {
                "patterns": [
                    r"air\s+pollution",
                    r"what\s+does\s+air\s+pollution\s+exposure\s+mean"
                ],
                "response": (
                    "This field estimates long-term exposure to polluted air environments. "
                    "Higher values indicate greater environmental exposure."
                )
            },
            {
                "patterns": [
                    r"obesity\s+profile\s+index",
                    r"obesity\s+index",
                    r"what\s+is\s+obesity\s+profile\s+index",
                    r"what\s+does\s+obesity\s+profile\s+mean"
                ],
                "response": (
                    "The Obesity Profile Index is a factor used in the assessment to estimate "
                    "obesity-related risk. Higher values indicate a greater obesity-related "
                    "contribution to overall risk."
                )
            },
            {
                "patterns": [
                    r"confidence\s+score",
                    r"explain\s+confidence\s+score",
                    r"what\s+does\s+confidence\s+score\s+mean"
                ],
                "response": (
                    "The confidence score represents the model's calculated mathematical probability "
                    "of the predicted risk level based on the clinical variables provided."
                )
            },
            {
                "patterns": [
                    r"shap\s+explainability",
                    r"what\s+is\s+shap",
                    r"shap\s+values?",
                    r"shapley"
                ],
                "response": (
                    "SHAP (SHapley Additive exPlanations) values measure the individual mathematical "
                    "contribution of each patient factor (such as diet, smoking, or family history) "
                    "to the final risk level prediction."
                )
            },
            {
                "patterns": [
                    r"what\s+does\s+this\s+field\s+mean",
                    r"field\s+descriptions?",
                    r"explain\s+fields?"
                ],
                "response": (
                    "Please select any field on the Risk Assessment form to view its description. "
                    "Each input expects a value based on the patient's clinical measurements or lifestyle habits."
                )
            }
        ]

    def get_guidance_response(self, message: str) -> str:
        """
        Scans the user query and returns the appropriate approved assessment guidance response.
        If no matches are found, returns an empty string.
        """
        clean_msg = message.strip().lower()
        for topic in self.guidance_topics:
            for pattern in topic["patterns"]:
                if re.search(pattern, clean_msg):
                    return topic["response"]
        return ""

# Instantiate global service instance
assessment_guidance_service = AssessmentGuidanceService()
