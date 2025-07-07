import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import json

st.set_page_config(page_title="Student Registration Insights", layout="wide")

# ---------- Load Data ----------
df_student = pd.read_csv("cleaned_school_data.csv")
df_student['State'] = df_student['State'].str.strip().str.title()
df_student['School Name'] = df_student['School Name'].str.strip().str.title()
df_student['City'] = df_student['City'].str.strip().str.title()
df_student['No of teachers registered'] = pd.to_numeric(df_student['No of teachers registered'], errors='coerce').fillna(0)

# ---------- Metrics ----------
total_schools = df_student['School Name'].nunique()
total_teachers = df_student['No of teachers registered'].sum()
avg_teachers = round(total_teachers / total_schools, 2)

st.title("📊 Student Registration – Insight Dashboard")
col1, col2, col3 = st.columns(3)
col1.metric("🏫 Unique Schools", total_schools)
col2.metric("👨‍🏫 Total Teachers Registered", total_teachers)
col3.metric("📈 Avg Teachers per School", avg_teachers)

st.markdown("---")

# ---------- City-wise Schools ----------
city_school_counts = df_student.groupby('City')['School Name'].nunique().sort_values(ascending=False)
st.subheader("🏙️ Top & Bottom Cities by Number of Schools")
col1, col2 = st.columns(2)
col1.dataframe(city_school_counts.head(5).rename("Top Cities"))
col2.dataframe(city_school_counts.tail(5).rename("Bottom Cities"))

# ---------- School-wise Teacher Registrations ----------
school_teacher_counts = df_student.groupby('School Name')['No of teachers registered'].sum().sort_values(ascending=False)
st.subheader("🎓 Top & Bottom Schools by Teacher Registrations")
col3, col4 = st.columns(2)
col3.bar_chart(school_teacher_counts.head(5))
col4.bar_chart(school_teacher_counts.tail(5))

# ---------- Low Participation Cities ----------
st.subheader("📌 Cities with 2 or Fewer Registered Schools")
low_participation_cities = city_school_counts[city_school_counts <= 2]
st.dataframe(low_participation_cities)

# ---------- Zero Teacher Schools ----------
zero_teacher_schools = df_student[df_student['No of teachers registered'] == 0]['School Name'].nunique()
st.subheader("⚠️ Schools with 0 Teachers Registered")
st.write(f"Total Schools: **{zero_teacher_schools}**")

# ---------- State-Level Participation Insight ----------
state_teacher_counts = df_student.groupby('State')['No of teachers registered'].sum().sort_values(ascending=False)
top_state = state_teacher_counts.idxmax()
top_value = state_teacher_counts.max()
bottom_state = state_teacher_counts.idxmin()
bottom_value = state_teacher_counts.min()
total_value = state_teacher_counts.sum()
top_percent = round(top_value / total_value * 100, 2)
bottom_percent = round(bottom_value / total_value * 100, 2)

st.subheader("🌍 State-Level Participation")
st.markdown(f"🏆 **Top State:** {top_state} – {top_value} teachers ({top_percent}%)")
st.markdown(f"🔻 **Lowest State:** {bottom_state} – {bottom_value} teachers ({bottom_percent}%)")

# ---------- Data Quality ----------
duplicates = df_student.duplicated().sum()
missing_city = df_student['City'].isnull().sum()
missing_address = df_student['Address'].isnull().sum()
missing_pincode = df_student['Pincode'].isnull().sum()

st.subheader("🧹 Data Quality Insights")
st.write(f"Duplicates: **{duplicates}**")
st.write(f"Missing Values → City: {missing_city}, Address: {missing_address}, Pincode: {missing_pincode}")

# ---------- Outlier Detection ----------
school_teacher_distribution = df_student.groupby('School Name')['No of teachers registered'].sum()
outliers = school_teacher_distribution[school_teacher_distribution > 100]
threshold_90 = school_teacher_distribution.quantile(0.9)

st.subheader("🧯 Outlier Schools")
st.write(f"Schools with >100 teachers registered: **{len(outliers)}**")
st.write(f"90% of schools have < **{int(threshold_90)}** teachers registered")

# ---------- Distribution of 3–10 Teachers ----------
in_range_count = school_teacher_distribution[(school_teacher_distribution >= 3) & (school_teacher_distribution <= 10)].count()
percent_in_range = round((in_range_count / total_schools) * 100, 2)
st.subheader("📊 Teacher Distribution")
st.write(f"{in_range_count} out of {total_schools} schools ({percent_in_range}%) have between 3–10 teachers registered.")

# ---------- State Heatmap with Plotly ----------
st.subheader("🗺️ State-wise Heatmap")

with open("india_states.geojson", "r", encoding="utf-8") as f:
    india_geo = json.load(f)

for feature in india_geo['features']:
    feature['properties']['ST_NM'] = feature['properties']['ST_NM'].strip().title()

heatmap_df = df_student.groupby('State')['No of teachers registered'].sum().reset_index()
fig = px.choropleth(
    heatmap_df,
    geojson=india_geo,
    featureidkey='properties.ST_NM',
    locations='State',
    color='No of teachers registered',
    color_continuous_scale='RdYlGn_r',
    title="🗺️ State-wise Teacher Registration Heatmap"
)
fig.update_geos(fitbounds="locations", visible=False)
st.plotly_chart(fig, use_container_width=True)

# ---------- Seaborn-style Heatmap ----------
st.subheader("📍 Text-based Heatmap")
fig2, ax = plt.subplots(figsize=(10, 12))
sns.heatmap(
    heatmap_df.set_index('State'),
    cmap="YlGnBu",
    annot=True,
    fmt=".0f",
    linewidths=0.5,
    ax=ax,
    cbar_kws={'label': 'Teachers Registered'}
)
st.pyplot(fig2)
