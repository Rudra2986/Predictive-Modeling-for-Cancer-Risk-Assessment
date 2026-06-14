"""
app.py - OncoRisk ML

Streamlit web application for cancer risk prediction.
Loads a trained model and lets users input patient data
to get a predicted risk level (Low, Medium, or High).

UI will be kept minimal until design references are provided.
"""

import streamlit as st

st.set_page_config(
    page_title="OncoRisk ML",
    page_icon=None,
    layout="centered"
)

st.title("OncoRisk ML")
st.subheader("Cancer Risk Level Prediction")

st.write(
    "This application predicts cancer risk levels (Low, Medium, High) "
    "based on patient demographic, behavioral, and health data."
)

st.info("The prediction interface is under development. Model training must be completed first.")
