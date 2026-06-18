from typing import List, Dict, Any

class RecommendationService:
    def generate_lifestyle_recommendations(self, context: Dict[str, Any]) -> List[str]:
        """
        Generates personalized educational recommendations based on user lifestyle variables.
        """
        patient_data = context.get("patient_data")
        if not patient_data:
            return []
            
        recs = []
        
        # 1. Smoking Habits
        smoking = int(patient_data.get("Smoking", 0))
        if smoking > 5:
            recs.append(
                "Reducing tobacco intake is highly critical. Consider researching structured smoking "
                "cessation support systems, behavioral counseling, and lung health evaluation options."
            )
            
        # 2. Obesity & BMI
        obesity = int(patient_data.get("Obesity", 0))
        bmi = float(patient_data.get("BMI", 24.5))
        if obesity > 5 or bmi > 25.0:
            recs.append(
                f"Your BMI is {bmi:.1f} (overweight category starts at 25.0). Maintaining a healthy weight "
                "through targeted calorie management and limiting processed/salted foods is highly beneficial."
            )
            
        # 3. Alcohol Consumption
        alcohol = int(patient_data.get("Alcohol_Use", 0))
        if alcohol > 5:
            recs.append(
                "Limiting daily alcohol intake is standard guidance for cellular health, as high intake "
                "is linked to several gastrointestinal and upper aerodigestive cancers."
            )
            
        # 4. Physical Activity
        activity = int(patient_data.get("Physical_Activity", 5))
        act_level = int(patient_data.get("Physical_Activity_Level", 5))
        if activity <= 4 or act_level <= 4:
            recs.append(
                "Aim to integrate at least 150 minutes of moderate aerobic exercise weekly (like brisk "
                "walking, swimming, or cycling) to improve metabolic function and reduce systemic inflammation."
            )
            
        # 5. Red Meat Intake
        red_meat = int(patient_data.get("Diet_Red_Meat", 0))
        processed_diet = int(patient_data.get("Diet_Salted_Processed", 0))
        if red_meat > 6 or processed_diet > 6:
            recs.append(
                "Transitioning dietary habits to limit red meat and heavily processed or salted food items "
                "can decrease colorectal irritation risk. Emphasize whole grains and lean protein alternatives."
            )
            
        # 6. Fruit & Veg Intake
        fruit_veg = int(patient_data.get("Fruit_Veg_Intake", 5))
        if fruit_veg <= 4:
            recs.append(
                "Increasing your daily portions of fresh fruits and cruciferous vegetables provides essential "
                "antioxidants and dietary fiber linked to lower cancer risk vectors."
            )
            
        return recs

    def generate_screening_guidelines(self, context: Dict[str, Any]) -> List[str]:
        """
        Provides educational details on standard clinical screenings based on patient demographics and type.
        This function never prescribes or schedules procedures.
        """
        age = int(context.get("age", 0))
        gender = context.get("gender", "Female")
        cancer_type = context.get("cancer_type", "Unknown")
        patient_data = context.get("patient_data", {})
        
        guidelines = []
        
        # 1. Suspected Cancer Type-specific education
        if cancer_type == "Breast":
            guidelines.append(
                "Breast Screening Education: Mammography is commonly utilized for early detection. "
                "Women over 40 (or earlier if family history exists) are encouraged to consult a clinician "
                "regarding when to initiate regular screening mammograms."
            )
        elif cancer_type == "Prostate":
            guidelines.append(
                "Prostate Screening Education: Prostate-Specific Antigen (PSA) blood tests are standard "
                "screening considerations for men starting at age 50 (or 45 for individuals with family history). "
                "A clinician can guide you on the benefits and limitations of PSA testing."
            )
        elif cancer_type in ["Colon", "Colorectal"]:
            guidelines.append(
                "Colorectal Screening Education: Standard preventive screening (e.g., colonoscopy, FIT, "
                "or stool-DNA tests) is commonly recommended starting at age 45. A healthcare professional "
                "can help determine the most suitable option for your history."
            )
        elif cancer_type == "Lung":
            guidelines.append(
                "Lung Screening Education: Low-dose computed tomography (LDCT) scans may be recommended "
                "as an educational screening tool for individuals aged 50 to 80 with a significant history "
                "of smoking. Talk to a physician to evaluate your eligibility."
            )
        elif cancer_type in ["Cervical", "Ovarian", "Endometrial"]:
            guidelines.append(
                "Gynecologic Screening Education: Routine Pap tests and HPV co-testing are primary tools "
                "for cervical health monitoring in women aged 21-65. Discuss an appropriate regular screening "
                "cadence with your gynecologist."
            )
            
        # 2. Genetic / History specific guidelines
        brca = int(patient_data.get("BRCA_Mutation", 0))
        fam_history = int(patient_data.get("Family_History", 0))
        
        if brca == 1:
            guidelines.append(
                "BRCA Mutation Guidance: Having a BRCA genetic mutation significantly alters surveillance "
                "strategies. Standard educational guidance involves regular specialized consultations with a "
                "genetic counselor to outline clinical breast exams, MRI imaging, or risk-reducing measures."
            )
        elif fam_history == 1:
            guidelines.append(
                "Family History Guidance: An elevated risk of hereditary cancer syndromes may be present. "
                "Sharing a detailed multi-generational family history with your physician helps determine if "
                "earlier or more frequent diagnostic surveillance is indicated."
            )
            
        h_pylori = int(patient_data.get("H_Pylori_Infection", 0))
        if h_pylori == 1:
            guidelines.append(
                "H. Pylori Management: An active H. pylori bacterial infection is a known risk factor for gastric "
                "lesions. Medical guidelines commonly recommend standard antibiotic eradication regimens. Please "
                "consult a gastroenterologist."
            )
            
        # Fallback general screening info if no specific factors match
        if not guidelines:
            guidelines.append(
                "General Preventive Screenings: Age-appropriate clinical surveillance, skin checks, and routine "
                "blood tests are essential components of preventive care. Please discuss a personalized plan with your doctor."
            )
            
        return guidelines

# Instantiate global service instance
recommendation_engine = RecommendationService()
