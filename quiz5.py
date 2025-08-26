import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data(show_spinner=False)
def quiz5dashboard():
    df = pd.read_csv('quiz5.csv')

    st.title("Quiz 5 Dashboard")

    st.header("📋 Quiz Summary")

    col1, col2, col3 = st.columns(3)

    # Total Users
    total_users = df['User_id'].nunique()
    col1.metric("Total Unique Users", total_users)

    # Total Quizzes
    total_quizzes = df['Quiz_id'].nunique()
    col2.metric("Total Quizzes", total_quizzes)

    # Total Attempts
    total_attempts = df['Attempts'].sum()
    col3.metric("Total Attempts", total_attempts)

    col4, col5, col6 = st.columns(3)

    # Total Questions Answered
    total_questions_answered = len(df)
    col4.metric("Total Questions Answered", total_questions_answered)

    # Avg. Score per Question
    avg_score_per_q = df['score'].mean()
    col5.metric("Average Score per Question", f"{avg_score_per_q:.2f}")

    # Avg. Total Score per User
    avg_total_score = df.groupby('User_id')['Total_Score'].mean().mean()
    col6.metric("Avg Total Score per User", f"{avg_total_score:.2f}")

    # Calculate overall accuracy
    total_attempts = len(df)
    total_correct = df['is_correct'].sum()
    overall_accuracy = (total_correct / total_attempts) * 100

    # Display as card metric
    st.metric(label="Overall Accuracy", value=f"{overall_accuracy:.2f}%")

    # -------------------
    # SCORE DISTRIBUTION
    # -------------------
    st.header("Score Distribution Histogram")

    bins = [0, 2, 5, 8, float('inf')]
    labels = ['0-2', '3-5', '6-8', '10s']
    df['score_range'] = pd.cut(df['score'], bins=bins, labels=labels)

    score_counts = df['score_range'].value_counts().sort_index().reset_index()
    score_counts.columns = ['Score Range', 'Count']

    fig = px.bar(score_counts, x='Score Range', y='Count', title='Score Distribution Histogram')
    st.plotly_chart(fig)

    # -------------------
    # SCORE RANGE PER QUESTION
    # -------------------
    st.header("Score Range Per Question")

    score_range = df.groupby('question_no')['score'].agg(['min', 'max']).reset_index()
    fig2 = px.line(score_range, x='question_no', y=['min', 'max'], title='Min/Max Score per Question')
    st.plotly_chart(fig2)

    # -------------------
    # MOST COMMON WRONG ANSWERS
    # -------------------
    st.header("Most Common Wrong Answers")

    incorrect_df = df[df['is_correct'] == 0]
    wrong_counts = incorrect_df.groupby(['question_no', 'selected_option']).size().reset_index(name='count')
    most_common_wrong = wrong_counts.loc[wrong_counts.groupby('question_no')['count'].idxmax()]

    fig3 = px.bar(most_common_wrong, x='question_no', y='count', color='selected_option', 
                title='Most Common Wrong Answers per Question')
    st.plotly_chart(fig3)

    # -------------------
    # ATTEMPT DISTRIBUTION
    # -------------------
    st.header("Attempt Distribution")

    attempt_distribution = df['Attempts'].value_counts().sort_index().reset_index()
    attempt_distribution.columns = ['Attempts', 'Count']

    fig_attempt = px.bar(
        attempt_distribution,
        x='Attempts',
        y='Count',
        title='Distribution of Attempt Counts',
        labels={'Attempts': 'Number of Attempts', 'Count': 'Number of Records'}
    )

    st.plotly_chart(fig_attempt)

    # -------------------
    # QUESTION-WISE ACCURACY
    # -------------------
    st.header("Question-wise Accuracy")

    question_accuracy = df.groupby('question_no')['is_correct'].mean().reset_index()
    question_accuracy['accuracy_percent'] = question_accuracy['is_correct'] * 100

    fig_accuracy = px.bar(
        question_accuracy,
        x='question_no',
        y='accuracy_percent',
        title='Question-wise Accuracy (%)',
        labels={'question_no': 'Question No', 'accuracy_percent': 'Accuracy (%)'}
    )

    st.plotly_chart(fig_accuracy)

    # -------------------
    # USERS WHO COMPLETED ALL QUESTIONS
    # -------------------
    st.header("Users who Completed All Questions")

    total_questions = df['question_no'].nunique()
    user_question_counts = df.groupby('User_id')['question_no'].nunique().reset_index(name='questions_answered')
    users_completed_all = user_question_counts[user_question_counts['questions_answered'] == total_questions]

    st.write(f"Total users who completed all questions: {len(users_completed_all)}")
    st.dataframe(users_completed_all)

    # -------------------
    # USERS WHO GOT ALL WRONG
    # -------------------
    st.header("Students who Got All Answers Wrong")

    correct_counts = df.groupby(['User_id', 'Name'])['is_correct'].sum().reset_index()
    all_wrong_users = correct_counts[correct_counts['is_correct'] == 0]

    st.write(f"Total users who got all wrong: {len(all_wrong_users)}")
    st.dataframe(all_wrong_users)

    # -------------------
    # USERS WHO ANSWERED CORRECTLY IN FIRST ATTEMPT
    # -------------------
    st.header("Users who Answered Correctly in First Attempt")

    first_attempt_df = df[df['Attempts'] == 1]
    correct_first_attempt = first_attempt_df[first_attempt_df['is_correct'] == 1]['User_id'].nunique()

    st.write(f"Users who answered correctly in first attempt: {correct_first_attempt}")

    # -------------------
    # USERS WHO NEEDED MULTIPLE ATTEMPTS
    # -------------------
    st.header("Users who Needed More Than One Attempt")

    multiple_attempts_df = df[df['Attempts'] > 1]
    users_multiple_attempts = multiple_attempts_df['User_id'].nunique()

    st.write(f"Users who needed more than one attempt: {users_multiple_attempts}")

    # -------------------
    # ERROR PATTERN: REPEATED SAME WRONG ANSWER
    # -------------------
    st.header("Repeated Wrong Answers on Same Question")

    repeat_wrong = incorrect_df.groupby(['User_id', 'question_no', 'selected_option']).size().reset_index(name='count')
    repeat_wrong_multiple = repeat_wrong[repeat_wrong['count'] > 1]

    # Only keep question_no, selected_option, and count
    repeat_wrong_summary = repeat_wrong_multiple[['question_no', 'selected_option', 'count']]

    st.write(f"Total repeated wrong answers found: {len(repeat_wrong_summary)}")
    st.dataframe(repeat_wrong_summary)