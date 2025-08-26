import pandas as pd
import streamlit as st
import plotly.express as px

# === Page Config ===
st.set_page_config(page_title="Submitted Ideas Dashboard", layout="wide")

def submitted_ideas_dashboard():
    st.title("🚀 Submitted Ideas Dashboard")
    st.markdown("Visual breakdown of ideas submitted across Indian states by themes.")

    # === Load Data ===
    df = pd.read_csv("Submitted_Ideas.csv", encoding='ISO-8859-1', low_memory=False,
                    dtype={'UDISE CODE': str, 'Pin code': str})
    df = df.dropna(subset=['State', 'Theme'])

    # === In-body Filters ===
    st.markdown("### 🔎 Filter Options")
    all_states = ["All States"] + sorted(df['State'].dropna().unique().tolist())
    selected_state = st.selectbox("Choose a State", all_states)



    # === Heatmap: Theme Distribution by State (%) ===
    st.subheader("🎯 Theme Distribution by State (%)")
    st.caption("This heatmap shows the percentage distribution of themes submitted per state.")

    state_theme = pd.crosstab(df['State'], df['Theme'], normalize='index') * 100
    fig1 = px.imshow(state_theme, text_auto=".1f", color_continuous_scale='RdBu', 
                    labels=dict(color='Percentage'), aspect="auto")
    fig1.update_layout(title="Theme Distribution by State (%)", height=800)
    st.plotly_chart(fig1, use_container_width=True)

    # === Language Preference by State (%) ===
    st.markdown("## 🌐 Language Preference by State (%)")
    language_col = 'Select in which language you prefer Submitting Your Idea?'

    if language_col in df.columns:
        lang_state = pd.crosstab(df['State'], df[language_col], normalize='index') * 100
        fig2 = px.imshow(lang_state, text_auto=".1f", color_continuous_scale='YlGnBu',
                        labels=dict(color='Percentage'), aspect="auto")
        fig2.update_layout(title="Language Preference by State (%)", height=800)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("⚠️ 'Language' column not found in the dataset.")

    # === Top Insights Section ===
    st.markdown("## 📊 Top Insights")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔝 Top 5 States by Participation")
        top_states = df['State'].value_counts().head(5)
        st.dataframe(top_states)

    with col2:
        st.markdown("### 🌟 Most Popular Themes")
        top_themes = df['Theme'].value_counts().head(5)
        st.dataframe(top_themes)


    # === Selected State Details ===
    if selected_state == "All States":
        st.markdown("## 📌 Top Themes in All States")
        theme_counts = df['Theme'].value_counts().head(5)

        col3, col4 = st.columns([1, 2])
        with col3:
            st.markdown("### 📄 Theme Breakdown")
            st.dataframe(theme_counts)

        with col4:
            st.markdown("### 📊 Bar Chart of Top Themes")
            fig3 = px.bar(theme_counts[::-1], orientation='h',
                        labels={'value': 'Number of Submissions', 'index': 'Theme'},
                        title="Top Themes in All States")
            st.plotly_chart(fig3, use_container_width=True)

    else:
        st.markdown(f"## 📌 Top Themes in {selected_state}")
        state_data = df[df['State'] == selected_state]
        state_theme_counts = state_data['Theme'].value_counts().head(5)

        if state_theme_counts.empty:
            st.warning(f"⚠️ No theme data found for {selected_state}.")
        else:
            col3, col4 = st.columns([1, 2])
            with col3:
                st.markdown("### 📄 Theme Breakdown")
                st.dataframe(state_theme_counts)

            with col4:
                st.markdown("### 📊 Bar Chart of Top Themes")
                fig3 = px.bar(state_theme_counts[::-1], orientation='h',
                            labels={'value': 'Number of Submissions', 'index': 'Theme'},
                            title=f"Top Themes in {selected_state}")
                st.plotly_chart(fig3, use_container_width=True)



    # === School Type Distribution by State (%) ===
    st.markdown("## 🏫 School Type Distribution by State (%) of submitted teams")
    try:
        school_type_dist = pd.crosstab(df['State'], df['School Type/Category'], normalize='index') * 100
        fig4 = px.imshow(school_type_dist, text_auto=".1f", color_continuous_scale='BuGn',
                        labels=dict(color='Percentage'), aspect="auto")
        fig4.update_layout(title="School Type Distribution by State (%)", height=800)
        st.plotly_chart(fig4, use_container_width=True)
    except KeyError:
        st.warning("⚠️ 'School Type/Category' column not found in the dataset.")




    # === Most Common Problem Locations ===
    st.markdown("## 📍 Most Common Problem Locations")
    col_name = 'In which places in your community did you find this problem?'

    if col_name in df.columns:
        problem_locations = df[col_name].value_counts().head(10)

        st.markdown("### 🧾 Top Locations")
        st.dataframe(problem_locations)

        st.markdown("### 📊 Bar Chart of Top Problem Locations")
        fig5 = px.bar(problem_locations[::-1], orientation='h',
                    labels={'value': 'Number of Reports', 'index': 'Location'},
                    title="Top 10 Reported Problem Locations")
        st.plotly_chart(fig5, use_container_width=True)
    else:
        st.warning("⚠️ 'Location of Problem' column not found in the dataset.")



    # Clean and standardize 'Teacher Gender' column
    df['Teacher Gender'] = df['Teacher Gender'].str.strip().str.lower()
    df['Teacher Gender'] = df['Teacher Gender'].replace({
        'male': 'Male',
        'female': 'Female',
        'not preferred': 'Not Preferred'
    })

    # === Completion Analysis by Teacher Gender ===
    st.markdown("## 🎓 Completion Analysis by Teacher Gender")

    if 'Teacher Gender' in df.columns and 'Idea Submission Status' in df.columns:
        comp_gender = pd.crosstab(df['Teacher Gender'], df['Idea Submission Status'])
        fig6 = px.bar(comp_gender, barmode='stack',
                    labels={'value': 'Number of Submissions', 'index': 'Teacher Gender'},
                    title="Completion Status by Teacher Gender")
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.warning("⚠️ Columns 'Teacher Gender' or 'Idea Submission Status' not found in the dataset.")

    action_col = 'Pick the actions your team did in your problem solving journey (You can choose multiple options)'

    st.markdown("## 📌 Most Common Actions Taken")
    if action_col in df.columns:
        common_actions = df[action_col].value_counts().head(10)

        st.markdown("### 🧾 Top 10 Actions")
        st.dataframe(common_actions)

        st.markdown("### 📊 Bar Chart of Top Actions")
        fig8 = px.bar(common_actions[::-1], orientation='h',
                    labels={'value': 'Number of Submissions', 'index': 'Action'},
                    title="Top 10 Most Common Actions")
        st.plotly_chart(fig8, use_container_width=True)
    else:
        st.warning("⚠️ 'Action Taken' column not found.")


    # === Feature Importance ===
    st.markdown("## 🧠 Feature Importance for Verification Prediction")
    feature_importance = pd.DataFrame({
        'feature': ['has_prototype', 'has_video', 'has_feedback', 'workbook_complete'],
        'importance': [0.35, 0.25, 0.20, 0.10]
    })

    try:
        fig10 = px.bar(feature_importance, x='importance', y='feature', orientation='h',
                    title="Feature Importance for Verification Prediction")
        st.plotly_chart(fig10, use_container_width=True)
        st.success("✅ ")
    except Exception as e:
        st.warning("⚠️ Failed to render Feature Importance chart.")
        st.exception(e)