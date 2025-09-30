import streamlit as st
import pandas as pd
 
@st.cache_data
def load_data():
    return pd.read_csv("data/GlobalWeatherRepository.csv")

# Load dataset
df = load_data()

st.title("Hello, ClimateScope! 🌍  - Global Weather Analysis")

# Show first 5 rows
st.subheader("Sample Data")
st.write(df.head())
st.write(df.info())       
st.write(df.describe())