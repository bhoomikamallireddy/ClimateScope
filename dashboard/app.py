import streamlit as st 
import pandas as pd
import numpy as np
import os
import plotly.express as px
from datetime import datetime

# ==========================================
# 1. PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="ClimateScope | Global Weather Intelligence",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CUSTOM CSS FOR HIGH-END UI
# ==========================================
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    
    section[data-testid="stSidebar"] {
        background-color: #6a86b3 !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p, 
    section[data-testid="stSidebar"] label, 
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3 {
        color: #000000 !important;
        font-weight: 600;
    }

    div[data-baseweb="select"] > div {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    span[data-baseweb="tag"] {
        background-color: #3b82f6 !important;
        color: white !important;
    }

    /* Fixed Radio Button Text Visibility */
    div[data-testid="stWidgetLabel"] p {
        color: #000000 !important;
    }

    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }

    .main-header {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        color: #1e3a8a;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 3. SMART DATA LOADING (CACHE)
# ==========================================
@st.cache_data
def load_analytical_data():
    base_path = os.path.dirname(os.path.abspath(__file__))
    daily_path = os.path.join(base_path, "..", "data", "analytical", "daily_weather_final.csv")
    monthly_path = os.path.join(base_path, "..", "data", "analytical", "monthly_trends.csv")
    
    if not os.path.exists(daily_path):
        daily_path = "data/analytical/daily_weather_final.csv"
        monthly_path = "data/analytical/monthly_trends.csv"

    daily = pd.read_csv(daily_path, parse_dates=["date"])
    monthly = pd.read_csv(monthly_path, parse_dates=["year_month"])
    return daily, monthly

try:
    daily_df, monthly_df = load_analytical_data()
except Exception as e:
    st.error("🚨 Analytical files not found! Please run 'feature_engineering.py' first.")
    st.stop()

# ==========================================
# 4. SIDEBAR GLOBAL FILTERS
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/869/869869.png", width=80)
    st.title("ClimateScope 🌍")
    st.markdown("---")
    
    st.header("🎛️ Global Controls")
    
    page = st.selectbox("Navigate To:", 
        ["Executive Summary", "Statistical Analysis", "Climate Trends", "Extreme Events", "User Guide"])
    
    st.markdown("---")
    
    unit = st.radio("Display Units:", ["Metric (°C, mm)", "Imperial (°F, in)"], horizontal=True)
    
    top_countries = daily_df['country'].value_counts().head(5).index.tolist()
    selected_countries = st.multiselect(
        "Select Countries:", 
        options=sorted(daily_df['country'].unique()), 
        default=top_countries
    )
    
    metric_label = st.selectbox("Focus Metric:", 
        ["Temperature", "Humidity", "Precipitation", "Wind Speed"])
    
    metric_map = {
        "Temperature": "temperature_celsius",
        "Humidity": "humidity",
        "Precipitation": "precip_mm",
        "Wind Speed": "wind_kph"
    }
    target_metric = metric_map[metric_label]

    # Date Range Selection
    min_date = daily_df['date'].min().date()
    max_date = daily_df['date'].max().date()
    
    with st.expander("📅 Select Date Range:", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start", value=min_date, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("End", value=max_date, min_value=start_date, max_value=max_date)
             
# ==========================================
# 5. DATA FILTERING LOGIC
# ==========================================
# Filtering by Country
filtered_df = daily_df[daily_df['country'].isin(selected_countries)].copy()

# Filtering by Date using the start and end variables directly
filtered_df = filtered_df[
    (filtered_df['date'].dt.date >= start_date) & 
    (filtered_df['date'].dt.date <= end_date)
]

# Unit Conversion
if "Imperial" in unit:
    filtered_df['temperature_celsius'] = (filtered_df['temperature_celsius'] * 9/5) + 32
    filtered_df['precip_mm'] = filtered_df['precip_mm'] / 25.4
# Sidebar Footer Checkpoint
st.sidebar.markdown("---")
st.sidebar.success(f"Verified: {len(filtered_df)} records loaded.")
# ==========================================
# 6. MAIN CONTENT ROUTER
# ==========================================
st.markdown(f"<h1 class='main-header'>🌍 {page}</h1>", unsafe_allow_html=True)

if page == "Executive Summary":
    if filtered_df.empty:
        st.warning("No data found for the selected criteria.")
    else:
        # Calculate Global Comparisons
        global_mean_temp = daily_df['temperature_celsius'].mean()
        global_max_wind = daily_df['wind_kph'].max()
        global_total_precip_avg = daily_df['precip_mm'].mean()

        current_mean_temp = filtered_df['temperature_celsius'].mean()
        current_max_wind = filtered_df['wind_kph'].max()
        current_mean_precip = filtered_df['precip_mm'].mean()

        # KPI ROW
        st.markdown("### 📊 Key Performance Indicators")
        k1, k2, k3 = st.columns(3)
        
        with k1:
            temp_delta = current_mean_temp - global_mean_temp
            st.metric(label="Mean Temperature", value=f"{current_mean_temp:.1f} °C", 
                      delta=f"{temp_delta:.1f} °C vs Global", delta_color="inverse")
        with k2:
            st.metric(label="Peak Wind Speed", value=f"{current_max_wind:.1f} kph", 
                      delta=f"{current_max_wind - global_max_wind:.1f} vs Max")
        with k3:
            st.metric(label="Data Density", value=f"{(len(filtered_df)/len(daily_df)*100):.1f}%", 
                      delta="Coverage")

        st.markdown("---")

        # MAP SECTION
        st.markdown("### 🌎 Global Temperature Distribution (Monthly Avg)")
        map_data = monthly_df.groupby('country')['avg_temp'].mean().reset_index()
        fig_map = px.choropleth(
            map_data, locations="country", locationmode="country names",
            color="avg_temp", color_continuous_scale="YlOrRd", projection="natural earth"
        )
        fig_map.update_traces(locationmode="country names")
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=500)
        st.plotly_chart(fig_map, width='stretch')

        # SNAPSHOT TABLE
        st.markdown("### ⏱️ Latest Weather Snapshots")
        latest_updates = filtered_df.sort_values(by='date', ascending=False).head(5)
        display_cols = ['date', 'country', 'temperature_celsius', 'humidity', 'precip_mm']
        st.table(latest_updates[display_cols])

        # DOWNLOAD ACTION
        st.download_button(
            label="📥 Export Filtered Report (CSV)",
            data=filtered_df.to_csv(index=False).encode('utf-8'),
            file_name='climatescope_report.csv',
            mime='text/csv',
        )
# ==========================================
# 7. STATISTICAL ANALYSIS PAGE
# ==========================================
elif page == "Statistical Analysis":
    st.markdown("### 🔍 Bivariate Relationship Analysis")
    
    # Check if we have enough data
    if filtered_df.empty:
        st.warning("Please select at least one country in the sidebar to view statistics.")
    else:
        # Create two columns for the scatter controls
        sc1, sc2 = st.columns(2)
        
        with sc1:
            x_axis = st.selectbox("Select X-Axis Metric:", 
                                 ["temperature_celsius", "humidity", "precip_mm", "wind_kph", "pressure_mb"],
                                 index=0)
        with sc2:
            y_axis = st.selectbox("Select Y-Axis Metric:", 
                                 ["temperature_celsius", "humidity", "precip_mm", "wind_kph", "pressure_mb"],
                                 index=1)

        # A. SCATTER PLOT WITH SAFETY FALLBACK
        try:
            # Attempt to render with Trendline
            fig_scatter = px.scatter(
                filtered_df, 
                x=x_axis, 
                y=y_axis, 
                color="country", 
                trendline="ols",
                hover_data=['date'],
                template="plotly_white",
                title=f"Relationship: {x_axis.replace('_', ' ').title()} vs {y_axis.replace('_', ' ').title()}"
            )
        except Exception as e:
            # Fallback: Render without trendline if statsmodels environment link fails
            st.info("💡 Note: Linear Trendline (OLS) is hidden due to environment sync. Showing raw distribution.")
            fig_scatter = px.scatter(
                filtered_df, 
                x=x_axis, 
                y=y_axis, 
                color="country", 
                hover_data=['date'],
                template="plotly_white",
                title=f"Relationship: {x_axis.replace('_', ' ').title()} vs {y_axis.replace('_', ' ').title()}"
            )
        
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, width='stretch')
        
        

        st.markdown("---")
        
        # B. CORRELATION HEATMAP
        st.markdown("### 🌡️ Global Correlation Heatmap")
        
        corr_cols = ["temperature_celsius", "humidity", "precip_mm", "wind_kph", "pressure_mb", "cloud"]
        available_corr_cols = [c for c in corr_cols if c in filtered_df.columns]
        
        if len(available_corr_cols) > 1:
            corr_matrix = filtered_df[available_corr_cols].corr()

            fig_heat = px.imshow(
                corr_matrix,
                text_auto=".2f",
                aspect="auto",
                color_continuous_scale='RdBu_r', 
                title="Correlation Matrix (Inter-variable Relationships)",
                labels=dict(color="Correlation")
            )
            st.plotly_chart(fig_heat, width='stretch')
        
        

        st.markdown("---")
        
        # C. DESCRIPTIVE STATS TABLE
        st.markdown("### 📋 Descriptive Statistics Summary")
        
        stats_summary = filtered_df[available_corr_cols].describe().T
        
        # Adding some styling to the table
        st.dataframe(stats_summary.style.format("{:.2f}").background_gradient(cmap='Blues'), 
                     width='stretch')

        

        # Analyst Insight Note
        with st.expander("💡 How to interpret this page?"):
            st.write("""
            - **Trend Line:** If the line goes up, the variables have a *positive correlation*.
            - **Correlation Heatmap:** Values close to **1.0** mean variables move together. Values close to **-1.0** mean they move in opposite directions.
            - **Stats Table:** Check the 'std' (Standard Deviation) to see which weather metric is the most volatile in your selected region.
            """)
# ==========================================
# 8. CLIMATE TRENDS PAGE (COMBINED & OPTIMIZED)
# ==========================================
elif page == "Climate Trends":
    st.markdown("### 📈 Temporal Analysis & Smoothing")
    
    if filtered_df.empty:
        st.warning("Please select countries in the sidebar to view trends.")
    else:
        # A. LINE CHART: RAW VS. SMOOTHED (Signal vs. Noise)
        st.markdown(f"#### {metric_label} Over Time: Raw vs. 7-Day Moving Average")
        
        # Determine the smoothed column (engineered in Phase 4)
        # Use existing 'temp_7d_avg' for speed, or calculate on-the-fly for other metrics
        if target_metric == "temperature_celsius" and "temp_7d_avg" in filtered_df.columns:
            smooth_col = "temp_7d_avg"
        else:
            # Sort is required for a proper rolling calculation
            filtered_df = filtered_df.sort_values(['country', 'date'])
            filtered_df['smooth_metric'] = filtered_df.groupby('country')[target_metric].transform(
                lambda x: x.rolling(7, min_periods=1).mean()
            )
            smooth_col = "smooth_metric"

        fig_trend = px.line(
            filtered_df, 
            x="date", 
            y=[target_metric, smooth_col],
            color="country",
            labels={"value": metric_label, "variable": "Data Type", "date": "Timeline"},
            template="plotly_white",
            color_discrete_sequence=px.colors.qualitative.Safe,
            title=f"7-Day Trend Analysis: {metric_label}"
        )
        
        # UI Polish: Thin dotted line for raw data, Thick solid line for Trend
        fig_trend.update_traces(line=dict(width=1, dash='dot'), selector=dict(name=target_metric))
        fig_trend.update_traces(line=dict(width=3), selector=dict(name=smooth_col))
        
        # Add Range Slider for deep-dive exploration
        fig_trend.update_xaxes(rangeslider_visible=True)
        st.plotly_chart(fig_trend, width='stretch')
        
        

        st.markdown("---")
        
        # B. SEASONAL HEATMAP (The Climate Pulse)
        st.markdown(f"#### 🌡️ Seasonal Pulse: Monthly Avg {metric_label}")
        
        # Performance trick: Use pre-aggregated monthly_df for selected countries
        seasonal_pivot = monthly_df[monthly_df['country'].isin(selected_countries)].pivot_table(
            index='country', 
            columns='month', 
            values='avg_temp' if target_metric == 'temperature_celsius' else target_metric, 
            aggfunc='mean'
        )
        
        fig_pulse = px.imshow(
            seasonal_pivot,
            labels=dict(x="Month", y="Country", color=metric_label),
            x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            color_continuous_scale="RdYlBu_r", # Red-Yellow-Blue is intuitive for weather
            text_auto=".1f",
            aspect="auto"
        )
        st.plotly_chart(fig_pulse, width='stretch')

        

        st.markdown("---")

        # C. DISTRIBUTION COMPARISON (Violin + Box Combo)
        st.markdown(f"#### 🎻 Statistical Spread: {metric_label} Variance")
        
        # This shows exactly where the 'density' of weather events lies
        fig_dist = px.violin(
            filtered_df, 
            y=target_metric, 
            x="country", 
            color="country", 
            box=True, # Keeps the box plot inside for IQR visibility
            points="all", # Shows every single day as a dot (great for outlier visibility)
            title=f"Variance and Outlier Spread by Country"
        )
        st.plotly_chart(fig_dist, width='stretch')
# ==========================================
# 9. EXTREME EVENTS PAGE
# ==========================================
elif page == "Extreme Events":
    st.markdown("### ⚠️ Extreme Event & Anomaly Detection")
    st.markdown("Identify localized weather anomalies by setting custom thresholds for heatwaves and storms.")
    
    if filtered_df.empty:
        st.warning("Please select at least one country in the sidebar to scan for anomalies.")
    else:
        # A. USER-DEFINED THRESHOLD INPUTS
        t1, t2 = st.columns(2)
        with t1:
            temp_threshold = st.number_input("Temp Heatwave Threshold (°C):", 
                                            min_value=0.0, max_value=60.0, value=35.0, step=1.0)
        with t2:
            rain_threshold = st.number_input("Heavy Rain Threshold (mm):", 
                                            min_value=0.0, max_value=500.0, value=50.0, step=5.0)

        # Create separate dataframes for anomalies (using .copy() to avoid warnings)
        extreme_heat = filtered_df[filtered_df['temperature_celsius'] >= temp_threshold].copy()
        extreme_rain = filtered_df[filtered_df['precip_mm'] >= rain_threshold].copy()

# B. ANOMALY TABLES (Using Tabs for Clean UX)
        tab1, tab2 = st.tabs(["🔥 Heatwave Analysis", "🌧️ Heavy Rainfall Analysis"])
        
        with tab1:
            st.markdown("##### 🚀 Top 5 Hottest Recorded Days")
            if not extreme_heat.empty:
                # 1. Define the columns we PREFER to show
                preferred_cols = ['date', 'country', 'temperature_celsius', 'humidity', 'condition_text']
                
                # 2. Only select columns that ACTUALLY exist in the dataframe
                actual_cols = [c for c in preferred_cols if c in extreme_heat.columns]
                
                heat_display = extreme_heat.sort_values('temperature_celsius', ascending=False).head(5)
                
                # 3. Display safely
                st.dataframe(
                    heat_display[actual_cols].style.format({
                        "temperature_celsius": "{:.1f}°C" if "temperature_celsius" in actual_cols else "{}"
                    }), 
                    width='stretch'
                )
            else:
                st.info("No temperature anomalies detected above the current threshold.")

        with tab2:
            st.markdown("##### 🚀 Top 5 Highest Precipitation Events")
            if not extreme_rain.empty:
                # 1. Define preferred columns
                preferred_cols_rain = ['date', 'country', 'precip_mm', 'wind_kph', 'condition_text']
                
                # 2. Filter for existing columns
                actual_cols_rain = [c for c in preferred_cols_rain if c in extreme_rain.columns]
                
                rain_display = extreme_rain.sort_values('precip_mm', ascending=False).head(5)
                
                # 3. Display safely
                st.dataframe(
                    rain_display[actual_cols_rain].style.format({
                        "precip_mm": "{:.1f} mm" if "precip_mm" in actual_cols_rain else "{}"
                    }), 
                    width='stretch'
                )
            else:
                st.info("No rainfall anomalies detected above the current threshold.")

        st.markdown("---")

        # C. EXTREME FREQUENCY (BAR CHART)
        st.markdown("#### 📊 Seasonal Distribution of Extremes")
        
        # Add labels for the combined chart
        extreme_heat['Event Type'] = 'Heatwave'
        extreme_rain['Event Type'] = 'Heavy Rain'
        
        # Combine anomalies
        combined_extremes = pd.concat([extreme_heat, extreme_rain])

        if not combined_extremes.empty:
            # Grouping to find which months see the most 'Residual' noise/anomalies
            freq_data = combined_extremes.groupby(['month', 'Event Type']).size().reset_index(name='Occurrences')
            
            fig_freq = px.bar(
                freq_data, 
                x="month", 
                y="Occurrences", 
                color="Event Type",
                barmode="group",
                title="Monthly Frequency of Extreme Weather Events",
                color_discrete_map={'Heatwave': '#ef4444', 'Heavy Rain': '#3b82f6'},
                template="plotly_white"
            )
            
            # Professional Month Labels
            fig_freq.update_xaxes(
                tickmode='array', 
                tickvals=list(range(1,13)), 
                ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            )
            
            st.plotly_chart(fig_freq, width='stretch')
            
            
            
            st.caption("Note: This chart links to the 'Residuals' analysis from the EDA, highlighting deviations from seasonal norms.")
        else:
            st.info("Adjust thresholds to visualize monthly frequency patterns.")        
    
elif page == "User Guide":
    st.markdown("### 📖 ClimateScope Documentation")
    st.markdown("""

    Welcome to **ClimateScope**, a professional-grade weather analysis tool.
    
    **How to use:**
    1. **Sidebar:** Set your global filters (Countries, Metrics, Dates).
    2. **Navigation:** Switch between specialized analysis pages.
    3. **Interactivity:** All charts are interactive—hover to see specific data points.
    
    **Data Source:** Global Weather Repository (2024-2025).
    """
    )
    with st.expander("📝 Dataset Overview", expanded=True):
        st.write("""
        This dashboard analyzes a global weather repository covering 211 countries over 500 days.
        The data has been normalized from raw hourly pings into daily analytical summaries.
        """)

    with st.expander("⚙️ Understanding the Metrics"):
        st.write("""
        - **Temperature:** Daily mean in Celsius.
        - **7-Day Avg:** A smoothed trend line that removes daily volatility.
        - **Residuals:** Deviations from the seasonal norm (used for Anomaly detection).
        """)

    with st.expander("🛠️ Technical Stack"):
        st.code("""
        - Frontend: Streamlit
        - Analytics: Pandas, NumPy
        - Visualization: Plotly Express
        - Statistics: Statsmodels (OLS Regression)
        """)

    st.info("💡 **Developer Note:** All charts are interactive. You can zoom, pan, and save any chart as a PNG using the camera icon on the top right of each plot.")    
     # ==========================================
     # AUTOMATED ANALYST INSIGHTS
     # ==========================================
    st.markdown("### 💡 AI-Powered Climate Insights")

    # 1. Logic for Temperature Insight
    avg_temp = filtered_df['temperature_celsius'].mean()
    if avg_temp > 25:
      temp_msg = "The selected region is currently experiencing a **Tropical/Hot climate phase**. Recommend focusing on heatwave mitigation metrics."
    elif avg_temp < 10:
        temp_msg = "The region is in a **Cold/Boreal phase**. Seasonal trends show significant heating demand during this period."
    else:
        temp_msg = "The region is within a **Temperate range**. Weather patterns are likely stable for this selection."
    # 2. Logic for Volatility (Consistency)
    temp_std = filtered_df['temperature_celsius'].std()
    if temp_std > 5:
        vol_msg = "⚠️ **High Volatility:** We are seeing sharp temperature swings. This indicates unpredictable weather fronts or rapid seasonal transitions."
    else:
        vol_msg = "✅ **Weather Stability:** Temperature variance is low. Predicted trends are highly reliable for this period."
     # 3. Logic for Precipitation
    total_rain = filtered_df['precip_mm'].sum()
    if total_rain > 100:
        rain_msg = "The area has recorded **Significant Precipitation**. This correlates with the 'Heavy Rain' logs found in the Extreme Events page."
    else:
        rain_msg = "The region is currently in a **Arid/Dry spell**. Risk of localized water stress if the trend continues."
     # Display as an organized colored box
    st.info(f"""
**Executive Summary for {', '.join(selected_countries[:3])}...**
* **Temperature Profile:** {temp_msg}
* **Predictability:** {vol_msg}
* **Hydrology:** {rain_msg}
    """)


