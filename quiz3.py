import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quiz 3 Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("D:\\tst\\data files\\df_cleaned_3.csv")

def quiz3dashboard(): 
    st.title("🧠 Quiz 3 Dashboard") 
    df = load_data()

    # ------------------ INSIGHT 1: OVERALL PERFORMANCE ------------------
    st.header("📌 Insight 1: OVERALL QUIZ PERFORMANCE")

    st.subheader("A. Average Score")
    avg_score = df['score'].mean()
    st.metric("Average Score", f"{avg_score:.2f}")

    st.subheader("B. Accuracy Rate")
    accuracy = df['is_correct'].mean() * 100
    st.metric("Accuracy Rate", f"{accuracy:.2f}%")

    st.subheader("C. Users who answered all questions correctly")
    all_correct = df.groupby('User_id')['is_correct'].sum() == df.groupby('User_id')['question_no'].nunique()
    st.metric("Users Got All Correct", all_correct.sum())

    st.subheader("D. Highest scoring question")
    score_by_question = df.groupby('question_no')['score'].mean().reset_index()
    highest_q = score_by_question.loc[score_by_question['score'].idxmax()]['question_no']
    st.success(f"Highest scoring question: {int(highest_q)}")

    st.subheader("E. Lowest scoring question")
    lowest_q = score_by_question.loc[score_by_question['score'].idxmin()]['question_no']
    st.error(f"Lowest scoring question: {int(lowest_q)}")

    fig1 = px.histogram(df, x="score", nbins=20, title="Score Distribution")
    st.plotly_chart(fig1)

    # ------------------ INSIGHT 2: QUESTION-LEVEL ANALYSIS ------------------
    st.header("📌 Insight 2: QUESTION-LEVEL ANALYSIS")

    st.subheader("A. Most Attempted Questions")
    attempts = df['question_no'].value_counts().reset_index()
    attempts.columns = ['question_no', 'Attempts']
    fig2 = px.bar(attempts.head(10), x='question_no', y='Attempts')
    st.plotly_chart(fig2)

    st.subheader("B. Highest Correct Answers")
    corrects = df[df['is_correct'] == True]['question_no'].value_counts().reset_index()
    corrects.columns = ['question_no', 'Correct Count']
    fig3 = px.bar(corrects.head(10), x='question_no', y='Correct Count')
    st.plotly_chart(fig3)

    st.subheader("C. Lowest Correct Answers")
    lowest_correct = corrects.sort_values(by='Correct Count').head(10)
    fig4 = px.bar(lowest_correct, x='question_no', y='Correct Count')
    st.plotly_chart(fig4)

    st.subheader("D. Most Wrong Answers")
    wrongs = df[df['is_correct'] == False]['question_no'].value_counts().reset_index()
    wrongs.columns = ['question_no', 'Wrong Count']
    fig5 = px.bar(wrongs.head(10), x='question_no', y='Wrong Count')
    st.plotly_chart(fig5)

    st.subheader("E. Correct vs Incorrect Answers")
    correct_vs_wrong = df['is_correct'].value_counts().reset_index()
    correct_vs_wrong.columns = ['Correct', 'Count']
    correct_vs_wrong['Correct'] = correct_vs_wrong['Correct'].map({True: 'Correct', False: 'Incorrect'})
    fig6 = px.bar(correct_vs_wrong, x='Correct', y='Count', color='Correct')
    st.plotly_chart(fig6)

    # ------------------ INSIGHT 3: ATTEMPT PATTERNS ------------------
    st.header("📌 Insight 3: ATTEMPT PATTERNS")

    st.subheader("A. Attempt Count Distribution")
    attempt_counts = df['Attempts'].value_counts().reset_index()
    attempt_counts.columns = ['Attempts', 'Count']
    fig7 = px.bar(attempt_counts.sort_values(by='Attempts'), x='Attempts', y='Count')
    st.plotly_chart(fig7)

    st.subheader("B. Avg Attempts per Question")
    avg_attempts = df.groupby('question_no')['Attempts'].mean().reset_index()
    fig8 = px.line(avg_attempts, x='question_no', y='Attempts')
    st.plotly_chart(fig8)

    st.subheader("C. Users who completed all questions")
    total_qs = df['question_no'].nunique()
    user_question_counts = df.groupby('User_id')['question_no'].nunique()
    completed_all = user_question_counts[user_question_counts == total_qs].count()
    st.metric("Users Completed All Questions", completed_all)

    st.subheader("D. Users correct in first attempt")
    first_attempt_correct = df[(df['Attempts'] == 1) & (df['is_correct'] == True)]['User_id'].nunique()
    st.metric("Correct on First Attempt", first_attempt_correct)

    st.subheader("E. Users with >1 attempt")
    more_than_one = df[df['Attempts'] > 1]['User_id'].nunique()
    st.metric("Users With >1 Attempt", more_than_one)

    st.subheader("F. Students who got all answers wrong")
    users_all_wrong = df.groupby('User_id')['is_correct'].sum() == 0
    st.metric("Users Got All Wrong", users_all_wrong.sum())

    # ------------------ INSIGHT 4: ERROR PATTERNS ------------------
    st.header("📌 Insight 4: ERROR PATTERNS")

    st.subheader("A. Most common wrong options")
    wrong_options = df[df['is_correct'] == False]['selected_option'].value_counts().reset_index().head(5)
    wrong_options.columns = ['selected_option', 'Count']
    fig9 = px.bar(wrong_options, x='selected_option', y='Count')
    st.plotly_chart(fig9)

    st.subheader("B. Repeated same wrong answer")
    same_wrong = df[df['is_correct'] == False].groupby(['User_id', 'quiz_question_id', 'selected_option']).size().reset_index(name='Count')
    repeat_wrongs = same_wrong[same_wrong['Count'] > 1]
    st.metric("Repeated Same Wrong Answers", repeat_wrongs.shape[0])

    # ------------------ INSIGHT 5: SCORING TRENDS ------------------
    st.header("📌 Insight 5: SCORING TRENDS")

    st.subheader("A. Score Range Distribution")
    score_bins = pd.cut(df['score'], bins=[0, 2, 5, 8, 10], labels=["0-2", "3-5", "6-8", "9-10"])
    score_dist = score_bins.value_counts().reset_index()
    score_dist.columns = ['Range', 'Count']
    fig10 = px.pie(score_dist, names='Range', values='Count', title="Score Ranges")
    st.plotly_chart(fig10)

    st.subheader("B. Score Range per Question")
    score_range = df.groupby('question_no')['score'].agg(['min', 'max']).reset_index()
    st.dataframe(score_range)

    #st.success("✅ Quiz 3 Dashboard Loaded Successfully!")


