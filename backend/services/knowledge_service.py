class KnowledgeService:
    # Version tracking for audit compliance
    VERSION = "1.0.0"

    def __init__(self):
        # Approved educational articles for cancers, lifestyle, and screenings
        self._articles = {
            "breast_cancer": {
                "title": "Breast Cancer Risk and Screening",
                "content": (
                    "Breast cancer develops from breast cells. Primary risk factors include advanced age, "
                    "female gender, hereditary genetic mutations (notably BRCA1 and BRCA2 genes), obesity, "
                    "family history of breast/ovarian cancer, and alcohol usage. Screening tools include clinical "
                    "breast examinations and routine mammograms."
                ),
                "keywords": ["breast", "brca", "mammogram", "clinical exam"]
            },
            "lung_cancer": {
                "title": "Lung Cancer Prevention and Screenings",
                "content": (
                    "Lung cancer is primarily linked to inhalation of toxins, with cigarette smoking being the leading "
                    "cause. Key risk factors include smoking intensity, environmental tobacco smoke (secondhand smoke), "
                    "air pollution exposure, and occupational hazards (such as asbestos or chemical inhalants). "
                    "Low-Dose Computed Tomography (LDCT) scans are recommended screenings for high-risk smokers "
                    "aged 50 to 80."
                ),
                "keywords": ["lung", "smoking", "smoke", "tobacco", "air pollution", "ldct"]
            },
            "colon_cancer": {
                "title": "Colorectal Cancer Risk and Prevention",
                "content": (
                    "Colorectal cancer starts in the colon or rectum. Primary lifestyle drivers include diets high in "
                    "red or processed meats, obesity, physical inactivity, smoking, and high alcohol use. Screening "
                    "methods include colonoscopies, fecal immunochemical tests (FIT), and stool-DNA tests, typically "
                    "starting at age 45."
                ),
                "keywords": ["colon", "colorectal", "rectal", "colonoscopy", "red meat", "processed meat", "fit"]
            },
            "prostate_cancer": {
                "title": "Prostate Cancer Education and PSA Screenings",
                "content": (
                    "Prostate cancer is one of the most common cancers in men, developing slowly in the prostate gland. "
                    "Key risk factors include older age, family history of prostate cancer, and African ancestry. "
                    "Screening is centered on the Prostate-Specific Antigen (PSA) blood test, which should be discussed "
                    "with a clinician to weigh its benefits and options."
                ),
                "keywords": ["prostate", "psa", "testicular"]
            },
            "skin_cancer": {
                "title": "Skin Cancer Prevention and Checkups",
                "content": (
                    "Skin cancer, including melanoma, basal cell, and squamous cell carcinoma, is heavily driven by "
                    "ultraviolet (UV) radiation from sunlight or tanning beds. Prevention methods include sunscreen "
                    "usage (SPF 30+), avoiding peak sun hours, wearing protective clothing, and performing monthly "
                    "skin self-exams or regular clinical checks."
                ),
                "keywords": ["skin", "melanoma", "sun", "sunscreen", "uv", "radiation"]
            },
            "lifestyle": {
                "title": "General Lifestyle Recommendations for Risk Reduction",
                "content": (
                    "Adopting a healthy lifestyle is a primary defense against cellular irritation. Standard guidelines "
                    "recommend: doing at least 150 minutes of moderate physical activity weekly; eating a balanced diet "
                    "rich in fruits, vegetables, and fiber; limiting red/processed meats; avoiding tobacco products; "
                    "limiting alcohol consumption; and maintaining a healthy body weight (BMI index)."
                ),
                "keywords": ["lifestyle", "exercise", "nutrition", "diet", "physical activity", "alcohol", "obesity", "bmi"]
            },
            "screening": {
                "title": "Overview of Clinical Screening Guidelines",
                "content": (
                    "Clinical screenings aim to detect precancerous changes before symptoms appear. Common procedures "
                    "include mammography (breast), colonoscopy/stool tests (colorectal), Low-Dose CT scans (lung), "
                    "PSA tests (prostate), and visual skin audits. Screenings should only be initiated after consulting "
                    "with a qualified doctor."
                ),
                "keywords": ["screening", "screenings", "test", "checkup", "diagnostic", "mammogram", "colonoscopy", "ldct", "psa"]
            }
        }

    def get_article(self, topic: str) -> dict:
        """
        Retrieves a specific approved educational article by key.
        """
        return self._articles.get(topic, {})

    def search_articles(self, query: str) -> list:
        """
        Scans keyword tags against the query string and returns matching article bodies.
        """
        clean_query = query.lower()
        matches = []
        for key, article in self._articles.items():
            if any(kw in clean_query for kw in article["keywords"]):
                matches.append(article)
        return matches

knowledge_service = KnowledgeService()
