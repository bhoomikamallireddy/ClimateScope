import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
import os
import warnings
warnings.filterwarnings("ignore")
 
@st.cache_data
def load_data():
    return pd.read_csv("data/GlobalWeatherRepository.csv")
st.set_page_config(page_title="ClimateScope",page_icon="🌍", layout="wide")

# Load dataset
df = load_data()

st.title("Hello, ClimateScope! 🌍  - Global Weather Analysis")
st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)
fl = st.file_uploader(":file_folder: Upload your file", type=["csv","txt","xlsx","xls"])
if fl is not None:
     filename=fl.name
     st.write(filename)
     if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl)
     elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(fl)
     else:
           os.chdir("E:\AspireInfo\ClimateScope\data")
           df = pd.read_csv("GlobalWeatherRepository.csv")

st.sidebar.header("Filter Options")
#For Country
regions = st.sidebar.multiselect("Select Regions", df['country'].unique())
if not regions:
      df2=df.copy()
else:
      df2=df[df['country'].isin(regions)]  
location = st.sidebar.multiselect("Select Locations", df2['location_name'].unique())   
if not location:
      df3=df2.copy()    
else:
      df3=df2[df2['location_name'].isin(location)]
if not regions and not location:
      filtered_df=df
elif not location:
      filtered_df=df[df['country'].isin(regions)]
elif not regions:
      filtered_df=df[df['location_name'].isin(location)]      
else:
      filtered_df=df3

st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)
st.write(df.head())
col1,col2 = st.columns((1,1))
df['last_updated'] = pd.to_datetime(df['last_updated'])
startDate=pd.to_datetime( df['last_updated'].min())
endDate=pd.to_datetime( df['last_updated'].max())

with col1:
      date1= pd.to_datetime( st.date_input("Start Date", startDate))

with col2:
      date2= pd.to_datetime( st.date_input("End Date", endDate))

df = df[(df['last_updated'] >= date1) & (df['last_updated'] <= date2)].copy()

