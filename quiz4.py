import streamlit as st
import pandas as pd
import plotly.express as px



# Load data
@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("D:\\tst\\data files\\df_cleaned_quiz4.csv")

def quiz4_dashboard():
    df = load_data()

    st.title("📊 Quiz 4 Dashboard")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 Accuracy",
        "📋 Question-Wise Analysis",
        "🧩 Error Pattern Analysis",
        "🔁 Attempts",
        "📈 Performance Improvement"
    ])

    with tab1:
        st.header("📌 Accuracy Metrics")

        st.subheader("✅ 1. Overall Accuracy")
        total_score = df['Total_Score'].sum()
        total_correct = total_score / 10
        total_attempted = df['Attempts'].sum()
        overaccuracy = (total_correct / total_attempted * 100) if total_attempted > 0 else 0
        st.metric(label="Overall Accuracy (%)", value=f"{overaccuracy:.2f}%")

        st.subheader("🎯 2. Users Who Got All Questions Correct")
        user_summary = (
            df.groupby('User_id')
            .agg(TotalScore=('score', 'sum'), QuestionAttempted=('question_no', 'nunique'))
            .reset_index()
        )
        user_summary['AllCorrect'] = (user_summary['TotalScore'] == user_summary['QuestionAttempted']).astype(int)
        total_all_correct = user_summary['AllCorrect'].sum()
        st.metric(label="Users Who Answered All Correctly", value=total_all_correct)

        st.subheader("❌ 3. Users Who Did NOT Answer All Correctly")
        users_not_all_correct = user_summary[user_summary['AllCorrect'] == 0]
        count_not_all_correct = users_not_all_correct['User_id'].nunique()
        st.metric(label="Users NOT All Correct", value=count_not_all_correct)

        st.subheader("📈 4. Pie Chart – All Correct vs Not All Correct")
        total_users = user_summary.shape[0]
        all_correct_users = user_summary[user_summary['AllCorrect'] == 1].shape[0]
        percent_all_correct = (all_correct_users / total_users) * 100 if total_users > 0 else 0
        st.metric(label="Users All Correct", value=all_correct_users)
        st.metric(label="Percentage of Users", value=f"{percent_all_correct:.2f}%")

        labels = ['All Correct', 'Not All Correct']
        values = [all_correct_users, total_users - all_correct_users]
        colors = ['#4CAF50', '#F44336']

        # Create interactive pie chart (without hole)
        fig = px.pie(
            names=labels,
            values=values,
            color=labels,
            color_discrete_map={'All Correct': '#4CAF50', 'Not All Correct': '#F44336'},
            title="Users Who Answered All Questions Correctly"
        )

        fig.update_traces(
            textinfo='label+percent',
            hovertemplate='%{label}: %{value} users<br>(%{percent})',
            textfont_size=14
        )

        fig.update_layout(
            title_font_size=18,
            title_x=0.5,
            legend=dict(orientation="h", y=-0.2),
            margin=dict(t=50, b=50, l=25, r=25)
        )

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📊 5. Score Distribution of Students (0–10)")

        # Score distribution logic
        user_scores = df[df['is_correct'] == True].groupby('User_id').size().reset_index(name='totalscore')

        raw_counts = user_scores['totalscore'].value_counts().reset_index()
        raw_counts.columns = ['totalscore', 'user_count']

        # Create full score range (0 to 10)
        all_scores = pd.DataFrame({'totalscore': range(0, 11)})
        score_counts = pd.merge(all_scores, raw_counts, on='totalscore', how='left').fillna(0)
        score_counts['user_count'] = score_counts['user_count'].astype(int)

        # Plotly bar chart with hover effect
        fig = px.bar(
            score_counts,
            x='totalscore',
            y='user_count',
            text='user_count',
            labels={'totalscore': 'Total Score', 'user_count': 'Number of Students'},
            color_discrete_sequence=['#E69F00'],
            hover_data={'totalscore': True, 'user_count': True}
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(
            title='Score Distribution of Students (0–10)',
            xaxis=dict(tickmode='linear'),
            yaxis_title='Number of Students',
            xaxis_title='Total Score',
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            bargap=0.3
        )

        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("✅ Most Correctly Answered Question")
        most_correct = df.groupby(['question_no', 'question'])['is_correct'].sum().reset_index()
        most_correct_sorted = most_correct.sort_values(by='is_correct', ascending=False)
        st.dataframe(most_correct_sorted.head(1)[['question_no', 'question']], use_container_width=True, hide_index=True)

        st.subheader("❌ Most Incorrectly Answered Question (Distractor)")
        question_errors = df.groupby(['question_no', 'question'])['is_correct'].agg(total_attempts='count', total_correct='sum').reset_index()
        question_errors['incorrect'] = question_errors['total_attempts'] - question_errors['total_correct']
        most_incorrect = question_errors.sort_values(by='incorrect', ascending=False)
        st.dataframe(most_incorrect.head(1)[['question_no', 'question']], use_container_width=True, hide_index=True)

        st.subheader("📊 Accuracy Percentage Per Question")
        accuracy_per_question = df.groupby(['question_no', 'question'])['is_correct'].agg(total_attempts='count', total_correct='sum').reset_index()
        accuracy_per_question['accuracy_percent'] = (accuracy_per_question['total_correct'] / accuracy_per_question['total_attempts'] * 100).round(2)
        accuracy_per_question = accuracy_per_question.sort_values(by='question_no')
        st.dataframe(accuracy_per_question[['question_no', 'question', 'accuracy_percent']], use_container_width=True, hide_index=True)

    with tab3:
        st.header("🧩 Error Pattern Analysis")

        st.subheader("📌 1. Error Rate (%) Per Question")
        error_rate_df = df.groupby(['question_no', 'question'])['is_correct'].agg(total_attempts='count', total_correct='sum').reset_index()
        error_rate_df['incorrect'] = error_rate_df['total_attempts'] - error_rate_df['total_correct']
        error_rate_df['error_rate_percent'] = (error_rate_df['incorrect'] / error_rate_df['total_attempts']) * 100
        error_rate_df['error_rate_percent'] = error_rate_df['error_rate_percent'].round(2)
        st.dataframe(error_rate_df[['question_no', 'question', 'error_rate_percent']], use_container_width=True, hide_index=True)

        st.subheader("🚨 2. Maximum Error Rate Across Questions")
        max_error_rate = error_rate_df['error_rate_percent'].max()
        st.metric(label="Maximum Error Rate", value=f"{max_error_rate:.2f}%")

        st.subheader("🧪 3. Most Common Incorrect Options Per Question")
        incorrect_df = df[df['is_correct'] == 0]
        incorrect_option_counts = incorrect_df.groupby(['question_no', 'selected_option']).size().reset_index(name='temp_count')
        most_common_incorrect = incorrect_option_counts.sort_values(['question_no', 'temp_count'], ascending=[True, False]).groupby('question_no').first().reset_index()
        final_result = most_common_incorrect[['question_no', 'selected_option']].copy()
        final_result.rename(columns={'selected_option': 'most_common_incorrect_option'}, inplace=True)
        st.dataframe(final_result, use_container_width=True, hide_index=True)

        st.subheader("🔁 4. Repeated Wrong Selections by Users")
        repeated_wrong_groups = incorrect_df.groupby(['User_id', 'quiz_question_id', 'selected_option']).size().reset_index(name='wrongcount')
        repeated_wrong_selections = repeated_wrong_groups[repeated_wrong_groups['wrongcount'] > 1]
        st.metric(label="Total Repeated Wrong Selections", value=repeated_wrong_selections.shape[0])

    with tab4:
        st.header("🔁 Attempts Analysis")

        st.subheader("📊 1. Average Attempts per Question")
        max_attempts_per_question = df.groupby('quiz_question_id')['Attempts'].max().reset_index(name='MaxAttempts')
        average_attempts = max_attempts_per_question['MaxAttempts'].mean()
        st.metric(label="Average Attempts per Question", value=f"{average_attempts:.2f}")

        st.subheader("🎯 2. First Attempt Accuracy")
        first_attempt_df = df[df['Attempts'] == 1]
        total_first_attempts = len(first_attempt_df)
        correct_first_attempts = first_attempt_df[first_attempt_df['is_correct'] == 1].shape[0]
        first_attempt_accuracy = (correct_first_attempts / total_first_attempts) * 100 if total_first_attempts > 0 else 0
        st.metric(label="First Attempt Accuracy (%)", value=f"{first_attempt_accuracy:.2f}%")

        st.subheader("🍩 3. Accuracy Groups by User")

    # Group and calculate accuracy
        user_accuracy = df.groupby('User_id').agg(
            total_questions=('question_no', 'count'),
            correct_answers=('is_correct', 'sum')
        ).reset_index()

        user_accuracy['accuracy'] = user_accuracy['correct_answers'] / user_accuracy['total_questions']

        # Categorize accuracy
        def categorize_accuracy(acc):
            if acc > 0.8:
                return "High (above 80%)"
            elif acc >= 0.5:
                return "Medium (50%–80%)"
            else:
                return "Low (below 50%)"

        user_accuracy['accuracy_group'] = user_accuracy['accuracy'].apply(categorize_accuracy)

        # Count users in each group
        group_counts = user_accuracy['accuracy_group'].value_counts().reindex(
            ['High (above 80%)', 'Medium (50%–80%)', 'Low (below 50%)'], fill_value=0
        ).reset_index()
        group_counts.columns = ['accuracy_group', 'user_count']

        # Plotly donut chart
        fig = px.pie(
            group_counts,
            names='accuracy_group',
            values='user_count',
            color='accuracy_group',
            color_discrete_sequence=['#4CAF50', '#FFC107', '#F44336'],
            hole=0.4,
            title='Student Accuracy Groups',
        )

        fig.update_traces(
            textinfo='percent+label',
            hovertemplate='%{label}: %{value} users<br>%{percent}',
            textfont_size=13
        )

        fig.update_layout(
            showlegend=True,
            height=400,
            margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📋 Accuracy Group Summary:")
        for _, row in group_counts.iterrows():
            st.write(f"{row['accuracy_group']}: {row['user_count']} students")


        st.subheader("📶 4. Accuracy by Attempt Number")

    # Group and calculate accuracy
        attempt_accuracy = df.groupby('Attempts').agg(
            total_answers=('is_correct', 'count'),
            correct_answers=('is_correct', 'sum')
        ).reset_index()

        attempt_accuracy['accuracy'] = (attempt_accuracy['correct_answers'] / attempt_accuracy['total_answers']) * 100
        attempt_accuracy = attempt_accuracy.round(2)

        # Plotly bar chart
        fig = px.bar(
            attempt_accuracy,
            x='Attempts',
            y='accuracy',
            text='accuracy',
            labels={'accuracy': 'Accuracy (%)'},
            color_discrete_sequence=['skyblue'],
            hover_data={'total_answers': True, 'correct_answers': True, 'accuracy': True}
        )

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(
            title='Accuracy (%) by Attempt Number',
            yaxis=dict(range=[0, 100], title='Accuracy (%)'),
            xaxis_title='Attempt',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)
    with tab5:
        st.header("📈 Performance Improvement Analysis")

        st.subheader("👥 1. Users with Single vs Multiple Attempts")
        attempt_counts = df.groupby(['User_id', 'Name'])['Attempts'].nunique().reset_index()
        attempt_counts.rename(columns={'Attempts': 'num_attempts'}, inplace=True)
        attempt_counts['attempt_type'] = attempt_counts['num_attempts'].apply(lambda x: 'single attempt' if x == 1 else 'multiple attempt')
        single_attempt_df = attempt_counts[attempt_counts['attempt_type'] == 'single attempt'][['User_id', 'Name']]
        multiple_attempt_df = attempt_counts[attempt_counts['attempt_type'] == 'multiple attempt'][['User_id', 'Name']]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### ✅ Multiple Attempts")
            st.dataframe(multiple_attempt_df.head(15))
        with col2:
            st.markdown("### ✅ Single Attempts")
            st.dataframe(single_attempt_df.head(15))

        st.subheader("📊 2. Bar Chart – Users by Attempt Type")

        # Summarize attempt types
        attempt_summary = df.groupby(['User_id', 'Name'])['Attempts'].nunique().reset_index()
        attempt_summary.rename(columns={'Attempts': 'unique_attempts'}, inplace=True)
        attempt_summary['attempt_type'] = attempt_summary['unique_attempts'].apply(
            lambda x: 'single attempt' if x == 1 else 'multiple attempts'
        )

        attempt_counts_chart = attempt_summary['attempt_type'].value_counts().reset_index()
        attempt_counts_chart.columns = ['attempt_type', 'user_count']

        # Plotly bar chart with hover
        fig = px.bar(
            attempt_counts_chart,
            x='attempt_type',
            y='user_count',
            text='user_count',
            color='attempt_type',
            color_discrete_sequence=px.colors.qualitative.Pastel,
            labels={'attempt_type': 'Attempt Type', 'user_count': 'Number of Users'},
            hover_data={'attempt_type': True, 'user_count': True}
        )

        fig.update_traces(textposition='outside')
        fig.update_layout(
            title='Users by Attempt Type',
            yaxis_title='Number of Users',
            xaxis_title='Attempt Type',
            showlegend=False,
            height=400,
            plot_bgcolor='rgba(0,0,0,0)'
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📈 3. Comparison of Score: Attempt 1 vs Attempt 2")
        score1 = df[df['Attempts'] == 1].groupby('User_id')['score'].max().reset_index().rename(columns={'score': 'score1'})
        score2 = df[df['Attempts'] == 2].groupby('User_id')['score'].max().reset_index().rename(columns={'score': 'score2'})
        comparison = pd.merge(score1, score2, on='User_id', how='outer')

        def categorize(row):
            if pd.isna(row['score1']) or pd.isna(row['score2']):
                return 'incomplete'
            elif row['score2'] > row['score1']:
                return 'improved'
            elif row['score2'] < row['score1']:
                return 'worsened'
            else:
                return 'no change'

        comparison['result_category'] = comparison.apply(categorize, axis=1)
        category_counts = comparison['result_category'].value_counts().reset_index()
        category_counts.columns = ['result_category', 'count']
        total_users = category_counts['count'].sum()
        category_counts['percentage'] = (category_counts['count'] / total_users * 100).round(1)
        st.markdown("### 📊 Result Category Breakdown")
        st.dataframe(category_counts)

        colors = ['#66c2a5', '#fc8d62', '#8da0cb', '#e78ac3']

        # Plotly pie chart with hover
        fig = px.pie(
            category_counts,
            names='result_category',
            values='count',
            color='result_category',
            color_discrete_sequence=colors,
            hole=0,  # set to 0.4 for donut chart if needed
            title='% of Students: Improved vs Worsened vs No Change vs Incomplete',
        )

        fig.update_traces(
            textinfo='percent+label',
            hovertemplate='%{label}: %{value} students<br>%{percent}',
            textfont_size=13
        )

        fig.update_layout(
            height=400,
            showlegend=True,
            margin=dict(t=50, b=50, l=50, r=50)
        )

        st.plotly_chart(fig, use_container_width=True)