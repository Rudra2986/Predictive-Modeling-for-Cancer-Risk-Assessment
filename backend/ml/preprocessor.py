import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

class OncoRiskPreprocessor(BaseEstimator, TransformerMixin):
    """
    Custom preprocessor for OncoRisk AI pipeline.
    Handles scaling of numeric features, pass-through of binary flags,
    and one-hot encoding of categorical variables.
    """
    def __init__(self):
        # Define columns categories
        self.categorical_cols = ["Cancer_Type"]
        
        self.numeric_cols = [
            "Age", "Smoking", "Alcohol_Use", "Obesity", "Diet_Red_Meat", 
            "Diet_Salted_Processed", "Fruit_Veg_Intake", "Physical_Activity", 
            "Air_Pollution", "Occupational_Hazards", "Calcium_Intake", 
            "BMI", "Physical_Activity_Level"
        ]
        
        self.binary_cols = [
            "Gender", "Family_History", "BRCA_Mutation", "H_Pylori_Infection"
        ]
        
        self.feature_names_ = []
        self._preprocessor = None

    def fit(self, X: pd.DataFrame, y=None):
        # Validate columns exist
        missing_cols = [col for col in (self.categorical_cols + self.numeric_cols + self.binary_cols) if col not in X.columns]
        if missing_cols:
            raise ValueError(f"Input DataFrame is missing required columns: {missing_cols}")
            
        # Create transformers
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])
        
        binary_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent"))
        ])
        
        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])
        
        # Combine into ColumnTransformer
        self._preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, self.numeric_cols),
                ("bin", binary_transformer, self.binary_cols),
                ("cat", categorical_transformer, self.categorical_cols)
            ],
            remainder="drop"
        )
        
        # Fit preprocessor
        self._preprocessor.fit(X, y)
        
        # Extract feature names
        # Numeric columns name remain same
        feature_names = list(self.numeric_cols)
        # Binary names remain same
        feature_names.extend(self.binary_cols)
        # OneHot column names
        cat_encoder = self._preprocessor.named_transformers_["cat"].named_steps["onehot"]
        cat_feature_names = cat_encoder.get_feature_names_out(self.categorical_cols)
        feature_names.extend(list(cat_feature_names))
        
        self.feature_names_ = feature_names
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        if self._preprocessor is None:
            raise ValueError("Preprocessor has not been fitted yet. Call fit or fit_transform first.")
        return self._preprocessor.transform(X)

    def fit_transform(self, X: pd.DataFrame, y=None) -> np.ndarray:
        self.fit(X, y)
        return self.transform(X)

    def get_feature_names(self) -> list:
        return self.feature_names_
