class PlatformHelpService:
    def __init__(self):
        # Synonym groups for PLATFORM_HELP questions
        self.history_aliases = [
            "history", "my history", "view history", "show history",
            "prediction history", "assessment history", "previous assessments"
        ]
        self.assessment_aliases = [
            "run assessment", "start assessment", "new assessment",
            "take assessment", "perform assessment", "begin assessment",
            "assessment page", "where is the assessment page", "where is the run assessment page"
        ]
        self.dashboard_aliases = [
            "dashboard", "access dashboard", "view dashboard"
        ]

    def get_help_response(self, message: str) -> str:
        """
        Scans the user query and returns the appropriate approved platform help response.
        If no matches are found, returns an empty string.
        """
        # Normalize whitespace and case
        clean_msg = " ".join(message.strip().lower().split())

        # Check assessment aliases first:
        for alias in self.assessment_aliases:
            if alias in clean_msg:
                return (
                    "You can start a new assessment by opening the Risk Assessment section from "
                    "the navigation menu and completing the required patient information."
                )
                
        # Check history aliases / dashboard aliases:
        for alias in self.history_aliases + self.dashboard_aliases:
            if alias in clean_msg:
                return (
                    "Open the Dashboard section and review your Prediction History to view "
                    "previous assessments and results."
                )
                
        # Check workflow aliases:
        # 1. next steps / after prediction
        for alias in ["after prediction", "after getting a prediction", "after receiving a prediction", "next steps"]:
            if alias in clean_msg:
                return (
                    "After receiving your prediction, you should review the contributing risk factors, "
                    "follow any personalized lifestyle recommendations, and consult a qualified "
                    "healthcare professional to discuss your results."
                )
                
        # 2. compare assessments
        for alias in ["compare assessments", "compare previous predictions"]:
            if alias in clean_msg:
                return (
                    "You can compare your assessments by visiting the Prediction History page, "
                    "where you can view changes in your risk factors and levels over time."
                )
                
        # 3. improve risk factors
        for alias in ["improve risk factors", "reduce risk factors", "improve my risk"]:
            if alias in clean_msg:
                return (
                    "You can improve your risk factors by focusing on the personalized recommendations "
                    "shown on your dashboard, such as smoking cessation, maintaining a healthy BMI, and "
                    "adjusting dietary habits."
                )
                
        return ""

# Instantiate global service instance
platform_help_service = PlatformHelpService()

