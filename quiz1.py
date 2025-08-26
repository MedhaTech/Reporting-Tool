import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="📊 Quiz 1 Insights Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("D:\\tst\\data files\\quiz1dataprocessed.csv")
def quiz1_dashboard():
    df = load_data()

    st.title("📊 Quiz 1 Dashboard")
    # 1. Performance Metrics (1–10)
    st.subheader("1. Performance Metrics")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_students = df['user_id'].nunique()
        st.metric("👥 Total Students", total_students)

        full_scorers = df[df['total_score'] == 10]

        num_full_scorers = full_scorers['user_id'].nunique()
        st.metric("Number of users who scored 10/10:", num_full_scorers)


    with col2:
        avg_score = df['total_score'].mean()
        st.metric("📈 Avg Score", round(avg_score, 2))


        zero_scorers = df[df['total_score'] == 0]['user_id'].nunique()
        st.metric("🚫 Zero Scorers", zero_scorers)

    with col3:
        all_correct_users = df.groupby('user_id')['is_correct'].sum() == 10
        percent_all_correct = (all_correct_users.sum() / total_students) * 100
        st.metric("✅ Overall Accuracy Rate (All Correct)", f"{percent_all_correct:.2f}%")

    # Score Distribution Histogram
    st.subheader("🎯 Score Distribution")
    fig1 = px.histogram(df, x="total_score", nbins=20, title="Total Score Distribution")
    st.plotly_chart(fig1, use_container_width=True)



    user_accuracy = df.groupby("user_id")['is_correct'].mean().reset_index()

    # Count users with all answers correct
    all_correct_users = user_accuracy[user_accuracy['is_correct'] == 1.0].shape[0]
    total_users = user_accuracy.shape[0]

    # Prepare data
    labels = ['Correct', 'Not Correct']
    values = [all_correct_users, total_users - all_correct_users]

    # Create pie chart using Plotly
    fig_pie = px.pie(
    names=labels,
    values=values,
    title="Users with Correct vs Not Correct",
    color=labels,
    color_discrete_map={'All Correct': '#4CAF50', 'Not All Correct': '#F44336'},
    hole=0  # Set hole=0 for pie (not donut)
    )
    st.plotly_chart(fig_pie, use_container_width=True)


    st.subheader("2. Question-Specific Insights")
    q_group = df.groupby('question_number')['is_correct'].mean().reset_index()
    fig2 = px.bar(q_group, x='question_number', y='is_correct', labels={'is_correct': 'Accuracy'}, color='is_correct')
    st.plotly_chart(fig2, use_container_width=True)

    # Easiest and Hardest Question
    q_acc = df.groupby('question_id')['is_correct'].mean().reset_index()
    easiest = q_acc.loc[q_acc['is_correct'].idxmax()]
    hardest = q_acc.loc[q_acc['is_correct'].idxmin()]
    st.info(f"✅ Easiest Question: Q{easiest['question_id']} – {easiest['is_correct']:.2f} accuracy")
    st.warning(f"❌ Most Missed Question: Q{hardest['question_id']} – {hardest['is_correct']:.2f} accuracy")

    wrong = df[df['is_correct'] == False].groupby('question_id').size().reset_index(name='count of wrong')
    wrong = wrong.sort_values(by='count of wrong', ascending=False).head(5).reset_index(drop=True)
    st.write("5 questions where most students answered incorrectly.")
    st.dataframe(wrong,hide_index=True)


    st.subheader("Most Common Incorrect Selections")
    incorrect = df[df['is_correct'] == 0]
    misconceptions = incorrect.groupby(['question_id', 'selected_option']).size().reset_index(name='count')
    top_mis = misconceptions.sort_values('count', ascending=False).head(10)
    fig4 = px.bar(top_mis, x='question_id', y='count', color='selected_option',
            title='Top Incorrect Choices by Question')
    st.plotly_chart(fig4, use_container_width=True)
    st.info("These are the top 5 questions where most users gave wrong answers. Consider revisiting the content or question design.")



    st.markdown("### Question Attempts Distribution")

    fig_attempts = px.histogram(
    df, 
    x='quiz_attempts', 
    nbins=15,
    title="Distribution of Question Attempts",
    labels={'quiz_attempts': 'Attempts'},
    range_x=[0, 30]  # 👈 limits x-axis from 0 to 30 attempts
    )

    st.plotly_chart(fig_attempts, use_container_width=True)

    st.success("Outcome.")
    recommendations = [
    "Most questions were attempted fewer than 10 times, with a steep drop-off in frequency beyond that point.",
    "A small minority of questions were attempted many times, potentially due to difficulty or retries."
    ]
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")


    # 3. Attempt & Behavior (21–30)
    st.subheader("3. Attempt Behavior Insights")
    retry_counts = df.groupby(['user_id', 'question_id'])['question_attempts'].max().reset_index()
    avg_retries = retry_counts['question_attempts'].mean()
    st.write(f"🔁 **Average Attempts per Question**: {avg_retries:.2f}")

    # Drop-off
    attempts_per_user = df.groupby('user_id')['question_id'].nunique()
    drop_off = (attempts_per_user < 10).sum()
    st.write(f"📉 **Drop-off Rate**: {(drop_off / total_students) * 100:.2f}% students didn't attempt all questions")

    st.markdown("### Retry Behavior")
    retry_df = df[df["question_attempts"] > 1]
    fig_retry = px.histogram(retry_df, x="question_attempts",
                        title="Retry Frequency (Attempts > 1)",
                        labels={"question_attempts": "Retry Count"})
    st.plotly_chart(fig_retry, use_container_width=True)


    # 3.2 Drop-off Questions
    skipped = df[df['selected_option'].isna()].groupby('question_number').size().reset_index(name='skipped')
    if not skipped.empty:
        fig_skip = px.bar(skipped, x='question_number', y='skipped',
                        title="Most Skipped Questions")
        st.plotly_chart(fig_skip, use_container_width=True)

    st.markdown("### Users by Attempt Type")
    attempt_summary = df.groupby(['user_id'])['quiz_attempts'].nunique().reset_index()
    attempt_summary.rename(columns={'quiz_attempts': 'unique_attempts'}, inplace=True)
    attempt_summary['attempt_type'] = attempt_summary['unique_attempts'].apply(lambda x: 'single attempt' if x == 1 else 'multiple attempts')
    attempt_counts_chart = attempt_summary['attempt_type'].value_counts().reset_index()
    attempt_counts_chart.columns = ['attempt_type', 'user_count']
    fig_type = px.bar(attempt_counts_chart, x='attempt_type', y='user_count',
                text='user_count', color='attempt_type',
                title='Users by Attempt Type',
                hover_data={'user_count': True, 'attempt_type': True})
    fig_type.update_traces(textposition='outside')
    st.plotly_chart(fig_type, use_container_width=True)



    st.subheader("4. Advanced Statistical Analysis")
    if 'difficulty_level' in df.columns:
        dif = df.groupby('difficulty_level')['is_correct'].mean().reset_index()
        st.dataframe(dif)

    # Learning curve
    df_sorted = df.sort_values(by=['user_id', 'question_number'])
    learning_curve = df_sorted.groupby('question_number')['is_correct'].mean().reset_index()
    fig3 = px.line(learning_curve, x='question_number', y='is_correct', title='Learning Curve (Accuracy by Question Order)')
    st.plotly_chart(fig3, use_container_width=True)
    st.info("Students began well on Q1, struggled with Q2, improved on Q4–Q5, dipped at Q6, stayed steady through Q7–Q9, and dropped again on Q10.")

    st.markdown("Wording Impact (Question Length vs Accuracy)")
    df["question_length"] = df["question_text"].str.len()
    word_impact = df.groupby("question_length")["is_correct"].mean().reset_index()
    word_impact["accuracy_percent"] = word_impact["is_correct"] * 100
    fig_wording = px.scatter(word_impact, x="question_length", y="accuracy_percent",
                        title="Wording Impact on Accuracy",
                        labels={"question_length": "Question Length (characters)", "accuracy_percent": "Accuracy (%)"})
    st.plotly_chart(fig_wording, use_container_width=True)
    recommendations = [
    "Short questions (30–50 chars): Mixed accuracy (65–100%); some easy, some tricky.",
    "Medium-length (60–90 chars): Lowest accuracy (~30–40%); possibly unclear.",
    "Long questions (100–140+ chars): Accuracy varies; well-structured ones did well."
    ]
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    st.info(
    "Conclusion:\n"
    "1. Question length doesn’t directly predict accuracy.\n"
    "2. Mid-length questions may need clarity improvement.\n"
    "3. Well-worded long or short questions perform better."
    )














