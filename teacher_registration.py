import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import json

def teacher_registration_dashboard():
# ---------- PAGE CONFIG ----------
    st.set_page_config(page_title="Teacher Registration Dashboard", layout="wide")

    # ---------- LOAD DATA ----------
    df = pd.read_csv("D:\\tst\\data files\\Teacher_Registration_Cleaned (1).csv")
    df.columns = df.columns.str.strip().str.title()
    df['State'] = df['State'].str.title().str.strip()
    df['District'] = df['District'].str.title().str.strip()
    df['School_Name'] = df['School_Name'].str.title().str.strip()
    df['Teacher_Name'] = df['Teacher_Name'].str.title().str.strip()
    df['Teacher_Gender'] = df['Teacher_Gender'].str.title().str.strip()

    # ---------- HEADER ----------
    st.markdown("<h1 style='text-align: center; color: white;'>👩‍🏫 Teacher Registration Dashboard</h1>", unsafe_allow_html=True)

    # ------------------ TOP FILTER SECTION ------------------
    st.markdown("### 🔍 Filter Teachers by State & District")

    state_options = ["All States"] + sorted(df["State"].dropna().unique())
    col1, col2 = st.columns(2)

    with col1:
        selected_state = st.selectbox("Select State", state_options)

    if selected_state == "All States":
        district_options = ["All Districts"] + sorted(df["District"].dropna().unique())
    else:
        district_options = ["All Districts"] + sorted(
            df[df["State"] == selected_state]["District"].dropna().unique()
        )

    with col2:
        selected_district = st.selectbox("Select District", district_options)

    if selected_state == "All States" and selected_district == "All Districts":
        filtered_df = df.copy()
    elif selected_state != "All States" and selected_district == "All Districts":
        filtered_df = df[df["State"] == selected_state]
    elif selected_state == "All States" and selected_district != "All Districts":
        filtered_df = df[df["District"] == selected_district]
    else:
        filtered_df = df[(df["State"] == selected_state) & (df["District"] == selected_district)]

    st.markdown("---")

    # ---------- METRICS ----------
    total_teachers = len(filtered_df)
    total_schools = filtered_df['School_Name'].nunique()
    avg_teachers = round(total_teachers / total_schools, 2)

    col1, col2, col3 = st.columns(3)
    col1.metric("👥 Total Teachers", total_teachers)
    col2.metric("🏫 Total Schools", total_schools)
    col3.metric("📈 Avg Teachers/School", avg_teachers)

    st.markdown("---")

    # ---------- GENDER DISTRIBUTION ----------
    st.subheader("📊 Gender Distribution of Teachers")
    gender_data = filtered_df['Teacher_Gender'].value_counts().reset_index()
    gender_data.columns = ['Gender', 'Count']

    fig_gender = px.pie(
        gender_data,
        names='Gender',
        values='Count',
        hole=0.3,
        title="Gender-wise Teacher Distribution"
    )
    fig_gender.update_traces(
        textinfo='percent+label',
        textfont_size=16,
        marker=dict(line=dict(color='#000000', width=2))
    )
    fig_gender.update_layout(
        legend_title_text="Gender",
        legend_font=dict(size=14, color='white'),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hoverlabel=dict(bgcolor="#1f1f1f", font_size=14, font_color="white")
    )

    st.plotly_chart(fig_gender, use_container_width=True)

    # ---------- TOP & BOTTOM SCHOOLS ----------
    st.subheader("🏫 Top & Bottom Schools by Teacher Count")
    school_counts = filtered_df['School_Name'].value_counts().sort_values(ascending=False)
    top_schools = school_counts.head(5).reset_index()
    bottom_schools = school_counts.tail(5).reset_index()
    top_schools.columns = ['School_Name', 'Count']
    bottom_schools.columns = ['School_Name', 'Count']

    col4, col5 = st.columns(2)
    col4.plotly_chart(px.bar(top_schools, x='School_Name', y='Count', color='Count',
                            color_continuous_scale='Greens', title='Top 5 Schools'))
    col5.plotly_chart(px.bar(bottom_schools, x='School_Name', y='Count', color='Count',
                            color_continuous_scale='Reds', title='Bottom 5 Schools'))

    # ---------- DISTRICT-WISE REGISTRATIONS ----------
    st.subheader("🏙️ District-wise Teacher Registrations")
    district_counts = df['District'].value_counts().reset_index()
    district_counts.columns = ['District', 'Count']
    top5 = district_counts.head(5).copy()
    bottom5 = district_counts.tail(5).copy()

    def highlight_top(s): return ['background-color: #d4edda; color: black' for _ in s]
    def highlight_bottom(s): return ['background-color: #f8d7da; color: black' for _ in s]

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 Top 5 Districts")
        st.dataframe(top5.style.apply(highlight_top, axis=1).format({'Count': '{:,}'}))

    with col2:
        st.markdown("### 🔴 Bottom 5 Districts")
        st.dataframe(bottom5.style.apply(highlight_bottom, axis=1).format({'Count': '{:,}'}))

    # ---------- STATE PARTICIPATION ----------
    st.subheader("🌍 Statewise Teacher Participation Ranking")
    state_counts = df['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Count']
    total_teachers = state_counts['Count'].sum()
    top_states = state_counts.head(5).copy()
    bottom_state = state_counts.tail(1).copy()
    top_states['Percentage'] = round(top_states['Count'] / total_teachers * 100, 2)
    bottom_state['Percentage'] = round(bottom_state['Count'] / total_teachers * 100, 2)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🏆 Top 5 States by Teacher Registration")
        st.dataframe(top_states.style.background_gradient(cmap='Greens').format({'Count': '{:,}', 'Percentage': '{:.2f}%'}))
    with col2:
        st.markdown("### 🔻 Lowest Participating State")
        state_name = bottom_state.iloc[0]['State']
        count = bottom_state.iloc[0]['Count']
        percent = bottom_state.iloc[0]['Percentage']
        st.markdown(f"""
        <div style='padding: 20px; background-color: #ffe6e6; border-left: 6px solid red; border-radius: 8px'>
            <h3 style='color: red;'>🚨 {state_name}</h3>
            <p><b>Only {count} teacher</b> registered from this state.</p>
            <p>This represents just <b>{percent}%</b> of all registrations.</p>
        </div>
        """, unsafe_allow_html=True)

    # ---------- TEXT HEATMAP ----------
    st.subheader("📍 Statewise Heatmap (Text Style)")
    state_teacher_counts = df.groupby("State")["Teacher_Name"].count().reset_index()
    state_teacher_counts = state_teacher_counts.sort_values("Teacher_Name", ascending=False)
    fig2, ax = plt.subplots(figsize=(8, 14))
    sns.heatmap(state_teacher_counts.set_index('State'), cmap='YlOrRd', annot=True, fmt="d", linewidths=0.5)
    st.pyplot(fig2)

    # ---------- GEO HEATMAP ----------
    st.subheader("🗺️ India Geo Heatmap – Teacher Participation")
    with open("D:\\tst\\data files\\india_states.geojson", "r", encoding="utf-8") as f:
        india_geo = json.load(f)
    for feature in india_geo['features']:
        feature['properties']['ST_NM'] = feature['properties']['ST_NM'].strip().title()

    map_df = df.groupby("State")["Teacher_Name"].count().reset_index()
    map_df.columns = ["State", "TeacherCount"]

    fig_map = px.choropleth(
        map_df,
        geojson=india_geo,
        featureidkey='properties.ST_NM',
        locations='State',
        color='TeacherCount',
        color_continuous_scale='RdYlGn_r',
        title='📌 Geo Map: Teacher Registration Intensity'
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)

    # ---------- LOW PARTICIPATION DISTRICTS ----------
    st.subheader("📌 Districts with Low Participation")
    district_counts = df['District'].value_counts().sort_values()
    low_districts = district_counts[district_counts <= 2]
    if not low_districts.empty:
        st.dataframe(low_districts.rename("Teacher Count"))
    else:
        st.success("✅ All districts have good participation!")

    # ---------- OUTLIERS ----------
    st.subheader("📉 Outlier & Range Detection")
    school_dist = df.groupby("School_Name")["Teacher_Name"].count()
    over_100 = school_dist[school_dist > 100]
    range_3_10 = school_dist[(school_dist >= 3) & (school_dist <= 10)].count()
    percent_range = round((range_3_10 / total_schools) * 100, 2)

    col6, col7 = st.columns(2)
    col6.info(f"🧯 Schools > 100 Teachers: **{len(over_100)}**")
    col7.info(f"📊 Schools with 3–10 Teachers: **{range_3_10}** ({percent_range}%)")

    # ---------- PARTICIPATION RANKING ----------
    st.subheader("🏆 State Participation Ranking")
    top_state = map_df.sort_values("TeacherCount", ascending=False).iloc[0]
    bottom_state = map_df.sort_values("TeacherCount", ascending=True).iloc[0]
    total_teachers_all = map_df["TeacherCount"].sum()
    top_pct = round((top_state["TeacherCount"] / total_teachers_all) * 100, 2)
    bot_pct = round((bottom_state["TeacherCount"] / total_teachers_all) * 100, 2)

    col8, col9 = st.columns(2)
    col8.success(f"""
    🏆 **Top State:**  
    **{top_state['State']}**  
    👨‍🏫 {top_state['TeacherCount']} teachers  
    📊 {top_pct}%
    """)
    col9.error(f"""
    🔻 **Lowest State:**  
    **{bottom_state['State']}**  
    👨‍🏫 {bottom_state['TeacherCount']} teachers  
    📉 {bot_pct}%
    """)

    # ---------- DATA QUALITY ----------
    st.subheader("🧹 Data Quality Report")
    duplicates = df.duplicated().sum()
    missing_school = df['School_Name'].isnull().sum()
    missing_teacher = df['Teacher_Name'].isnull().sum()
    missing_address = df['Address'].isnull().sum() if 'Address' in df.columns else 0

    colX, colY, colZ = st.columns(3)
    colX.info(f"🔁 Duplicate Rows: {duplicates}")
    colY.warning(f"🏫 Missing School Name: {missing_school}")
    colZ.warning(f"👤 Missing Teacher Name: {missing_teacher}")
    st.info(f"🏠 Missing Address: {missing_address}")

    # ---------- MAP INSIGHT SUMMARY ----------
    st.markdown("## 🌍 India Map Insight Summary")
    html_code = """
    <style>
    .fla-map-wrapper {
        width: 100%;
        height: 110%;
        min-height: 1200px;
        overflow: hidden;
    }
    .fla-map-wrapper iframe {
        width: 100%;
        height: 1100px;
        border: none;
    }
    </style>
    <div class="fla-map-wrapper">
        <iframe src="https://app.fla-shop.com/7f5w8/9c3628c2-d794-4375-b9bf-6dbee11de204" ></iframe>
    </div>
    """
    components.html(html_code, height=1000, scrolling=False)

    # ---------- STATE INSIGHTS ----------
    st.markdown("""
    ### 🧠 Insights by State Performance

    #### 🟢 Top Performing States
    Rajasthan, Tamil Nadu, Andhra Pradesh, Kerala, Madhya Pradesh, Uttar Pradesh, Maharashtra, Gujarat, Karnataka, Telangana

    #### 🟠 Medium Performing States
    Odisha, Assam, Bihar, Chhattisgarh, Jharkhand, West Bengal, Delhi, Haryana, Punjab, Himachal Pradesh

    #### 🔴 Low Performing States
    Goa, Tripura, Manipur, Sikkim, Meghalaya, Nagaland, Mizoram, Arunachal Pradesh, Chandigarh, Daman and Diu, Andaman and Nicobar Islands, Lakshadweep, Puducherry, Ladakh
    """)
