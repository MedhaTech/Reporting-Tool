import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Post-Survey Dashboard", layout="wide")
st.title("📊 Post-Survey Dashboard")

@st.cache_data(show_spinner=False)
def postsurvey_dashboard():
    def load_data():
        return pd.read_excel("D:\\tst\\data files\\cleaned_post_survey.xlsx")

    df = load_data()

    # Reusable plot functions
    def plot_horizontal_bar(series, title):
        data = series.value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'})
        fig = px.bar(data, x='count', y='selected_option', orientation='h', color='selected_option', title=title)
        st.plotly_chart(fig, use_container_width=True)

    def plot_vertical_bar(series, title):
        data = series.value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'})
        fig = px.bar(data, x='selected_option', y='count', color='selected_option', title=title)
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Tabs
    tabs = st.tabs([
        "Daily Life Impact",
        "Community Problem Identification",
        "Scenario Thinking",
        "Decision-Making",
        "Self-Perception",
        "Resilience",
        "Feedback & Satisfaction",
        "Course Feedback"
    ])

    # 1. Daily Life Impact
    with tabs[0]:
        st.subheader("1. Daily Life Impact")

        q1 = df[df['question_no'] == 1]
        st.markdown("*Q1: What is your favorite part of the program?*")
        st.dataframe(q1['selected_option'].value_counts().reset_index().rename(columns={'index': 'Favorite Part', 'selected_option': 'Count'}))

        q2 = df[df['question_no'] == 2]
        st.markdown("*Q2: Did any activity make you think about your own life in a new way?*")
        fig_q2 = px.pie(q2, names='selected_option', title="Reflection on Life")
        fig_q2.update_layout(height=500)
        st.plotly_chart(fig_q2, use_container_width=True)

        q3 = df[df['question_no'] == 3]
        st.markdown("*Q3: If yes, which activity?*")
        plot_horizontal_bar(q3['selected_option'], "Activities That Made You Reflect")

        q4 = df[df['question_no'] == 4]
        st.markdown("*Q4: What did you learn about yourself through this program?*")
        plot_horizontal_bar(q4['selected_option'], "What You Learned About Yourself")

    # 2. Community Problem Identification
    with tabs[1]:
        st.subheader("2. Community Problem Identification")

        q5 = df[df['question_no'] == 5]
        st.markdown("*Q5: Which community problem do you now notice more after this program?*")
        plot_vertical_bar(q5['selected_option'], "Community Problems Noticed")

    # 3. Scenario Thinking
    with tabs[2]:
        st.subheader("3. Scenario Thinking")

        q6 = df[df['question_no'] == 6]
        st.markdown("*Q6: What would be your first step as a community leader?*")
        st.dataframe(q6['selected_option'].value_counts().reset_index().rename(columns={'index': 'Step', 'selected_option': 'Count'}))

        q7 = df[df['question_no'] == 7]
        st.markdown("*Q7: What is one thing you learned from others?*")
        st.dataframe(q7['selected_option'].value_counts().reset_index().rename(columns={'index': 'Learning', 'selected_option': 'Count'}))

    # 4. Decision-Making
    with tabs[3]:
        st.subheader("4. Decision-Making")

        q8 = df[df['question_no'] == 8]
        st.markdown("*Q8: What would you do if you see someone littering?*")
        plot_horizontal_bar(q8['selected_option'], "Response to Littering")

        q9 = df[df['question_no'] == 9]
        st.markdown("*Q9: What would you do if a friend is excluded?*")
        data_q9 = q9['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'})
        fig_q9 = px.bar(data_q9, x='selected_option', y='count', color='selected_option', title="Response to Exclusion")
        fig_q9.update_layout(height=500)
        st.plotly_chart(fig_q9, use_container_width=True)

    # 5. Self-Perception
    # 5. Self-Perception
    with tabs[4]:
        st.subheader("5. Self-Perception")

        q10 = df[df['question_no'] == 10]
        st.markdown("*Q10: Which word best describes you after completing the program?*")
        data_q10 = q10['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'})
        fig_q10 = px.treemap(data_q10, path=['selected_option'], values='count', title="Self Description")
        fig_q10.update_traces(hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>')
        st.plotly_chart(fig_q10, use_container_width=True)

        q11 = df[df['question_no'] == 11]
        st.markdown("*Q11: How did your thinking change after the program?*")
        st.dataframe(q11['selected_option'].value_counts().reset_index().rename(columns={'index': 'Change', 'selected_option': 'Count'}))

        q12 = df[df['question_no'] == 12]
        st.markdown("*Q12: What new skill or ability did you discover?*")
        st.dataframe(q12['selected_option'].value_counts().reset_index().rename(columns={'index': 'Skill', 'selected_option': 'Count'}))

    # 6. Resilience
    with tabs[5]:
        st.subheader("6. Resilience")

        q13 = df[df['question_no'] == 13]
        st.markdown("*Q13: How confident do you feel about solving problems?*")
        st.plotly_chart(px.pie(q13, names='selected_option'), use_container_width=True)

        q14 = df[df['question_no'] == 14]
        st.markdown("*Q14: What is something difficult you overcame during the program?*")
        plot_vertical_bar(q14['selected_option'], "Difficulties Overcome")

    # 7. Feedback & Satisfaction
    with tabs[6]:
        st.subheader("7. Feedback & Satisfaction")

        q15 = df[df['question_no'] == 15]
        st.markdown("*Q15: How satisfied are you with the program?*")
        st.plotly_chart(px.pie(q15, names='selected_option'), use_container_width=True)

        q16 = df[df['question_no'] == 16]
        st.markdown("*Q16: What was missing in the program?*")
        plot_vertical_bar(q16['selected_option'], "What Was Missing")

        q17 = df[df['question_no'] == 17]
        st.markdown("*Q17: What was the most memorable part of the program?*")
        plot_horizontal_bar(q17['selected_option'], "Most Memorable Moments")

    # 8. Course Feedback
    # 8. Course Feedback
    with tabs[7]:
        st.subheader("8. Course Feedback")

        q18 = df[df['question_no'] == 18]
        st.markdown("*Q18: How likely are you to recommend the program?*")
        st.plotly_chart(px.pie(q18, names='selected_option'), use_container_width=True)

        q19 = df[df['question_no'] == 19]
        st.markdown("*Q19: Suggestions to improve the program?*")
        plot_horizontal_bar(q19['selected_option'], "Improvement Suggestions")

        q20 = df[df['question_no'] == 20]
        st.markdown("*Q20: Any final thoughts?*")
        st.dataframe(
            q20['selected_option']
            .value_counts()
            .reset_index()
            .rename(columns={'index': 'Final Thought', 'selected_option': 'Count'})
        )