import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Quiz 2 Dashboard", layout="wide")

@st.cache_data(show_spinner=False)
def load_data():
    return pd.read_csv("D:\\tst\\data files\\prcss_quiz2.csv")  # 🔁 Replace with your CSV file
def quiz2dashboard():
    st.title(" 📊 Quiz-2 Dashboard")
    df = load_data()

    user_scores = df.drop_duplicates(subset=["User_id", "Quiz_id"])

    # Create Tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "1️⃣ Overall Performance",
        "2️⃣ Question-Level Insights",
        "3️⃣ User Behavior",
        "4️⃣ Additional Insights"
    ])

    with tab1:
        st.header("📊 Overall Performance Insights")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_students = user_scores["User_id"].nunique()
            st.metric("👨‍🏫 Total Unique Students Attempted", total_students)

        with col2:
            average_score = user_scores["Total_Score"].mean()
            st.metric("📈 Average Total Score", round(average_score, 2))

        with col3:
            full_scorers = user_scores[user_scores["Total_Score"] == 10].shape[0]
            st.metric("🏆 Full Scorers (10/10)", full_scorers)

        with col4:
            zero_scorers = user_scores[user_scores["Total_Score"] == 0].shape[0]
            st.metric("❌ Zero Scorers (0/10)", zero_scorers)

        st.header("📊Total Score Distribution (Pie Chart)")
        score_counts = user_scores["Total_Score"].value_counts().sort_index()
        fig = px.pie(
            names=score_counts.index,
            values=score_counts.values,
            title="Total Score Distribution",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textinfo='percent+label', hovertemplate='Score: %{label}<br>Count: %{value}<br>Percentage: %{percent}')
        st.plotly_chart(fig, use_container_width=True)


    with tab2:
        question_accuracy = df.groupby("Question_no")["Is_Correct"].mean().reset_index()
        question_accuracy["Accuracy (%)"] = round(question_accuracy["Is_Correct"] * 100, 2)
        st.subheader("📊 Accuracy per Question")

        fig = px.bar(
            question_accuracy,
            x="Question_no",
            y="Accuracy (%)",
            text="Accuracy (%)",
            title="Accuracy by Question",
            labels={"Question_no": "Question Number", "Accuracy (%)": "Accuracy (%)"},
            color="Accuracy (%)",
            color_continuous_scale="Blues"
        )

        fig.update_traces(
            hovertemplate="Q%{x}<br>Accuracy: %{y:.2f}%",
            texttemplate="%{text:.1f}%",
            textposition="outside"
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        easiest = question_accuracy.loc[question_accuracy["Accuracy (%)"].idxmax()]
        hardest = question_accuracy.loc[question_accuracy["Accuracy (%)"].idxmin()]
        col7, col8 = st.columns(2)
        with col7:
            st.metric("📈 Easiest Question", f"Q{int(easiest['Question_no'])} - {easiest['Accuracy (%)']}% accuracy")
        with col8:
            st.metric("📉 Hardest Question", f"Q{int(hardest['Question_no'])} - {hardest['Accuracy (%)']}% accuracy")

        incorrect_answers = df[df["Is_Correct"] == 0]
        wrong_option_counts = (
            incorrect_answers.groupby(["Question_no", "Selected_Option"])
            .size()
            .reset_index(name="Wrong Answer Count")
            .sort_values(["Question_no", "Wrong Answer Count"], ascending=[True, False])
        )

        most_common_wrong = wrong_option_counts.groupby("Question_no").first().reset_index()
        most_common_wrong.columns = ["Question_no", "Most Common Wrong Option", "Times Selected"]
        st.subheader("🚫 Most Commonly Selected Wrong Option per Question (by Frequency)")
        st.dataframe(most_common_wrong, hide_index=True)

    with tab3:
        st.subheader("🔁No. of people selected correct and wrong Answer  on particular question")
        answer_counts = df.groupby(["User_id", "Question_no", "Selected_Option", "Is_Correct"]).size().reset_index(name="Count")
        repeats = answer_counts[answer_counts["Count"] > 1]
        repeat_summary = repeats.groupby(["Question_no", "Is_Correct"]).size().reset_index(name="Repeat Count")
        repeat_summary["Answer Type"] = repeat_summary["Is_Correct"].replace({1: "Correct", 0: "Incorrect"})
        fig = px.bar(
            repeat_summary,
            x="Question_no",
            y="Repeat Count",
            color="Answer Type",
            barmode="group",
            title="correct and wrong Answer  on particular question",
            labels={"Question_no": "Question Number", "Repeat Count": "Selection Count"},
            color_discrete_map={"Correct": "green", "Incorrect": "red"}
        )
        st.plotly_chart(fig, use_container_width=True)



        col1,col2=st.columns(2)
        st.header("")
        with col1:
                avg_attempts = df.groupby("User_id")["Attempts"].max().mean()
                st.metric("🔁 Average Attempts per Student", round(avg_attempts, 2))
        with col2:
                most_attempted_q = df["Question_no"].value_counts().idxmax()
                st.metric("📌Question which student felt most easy", f"Q{most_attempted_q}")



        st.subheader("✅ vs ❌ Answer Percentage (Pie Chart)")
        correct_percentages = df["Is_Correct"].value_counts(normalize=True).reset_index()
        correct_percentages.columns = ["Is_Correct", "Percentage"]
        correct_percentages["Percentage"] = round(correct_percentages["Percentage"] * 100, 2)
        correct_percentages["Answer"] = correct_percentages["Is_Correct"].replace({1: "✅ Correct", 0: "❌ Incorrect"})

        fig = px.pie(
            correct_percentages,
            names="Answer",
            values="Percentage",
            color="Answer",
            color_discrete_map={"✅ Correct": "green", "❌ Incorrect": "red"},
            title=""
        )

        fig.update_traces(
            textinfo="percent+label",
            hovertemplate="%{label}<br>Percentage: %{value:.2f}%<extra></extra>"
        )

        st.plotly_chart(fig, use_container_width=True)



        st.subheader("🧾Response Summary of Student")
        student_list = df[~df["Name"].str.contains("class", case=False, na=False)]["Name"].dropna().unique()
        selected_student = st.selectbox("Select a student", sorted(student_list))
        student_df = df[df["Name"] == selected_student]
        summary_df = student_df[[
            "Quiz_id", "Attempts", "Question_no", "Question",
            "Selected_Option", "Correct_Answer",
            "Is_Correct", "Total_Score", "Level"
        ]].sort_values(by=["Attempts", "Question_no"])

        summary_df["Is_Correct"] = summary_df["Is_Correct"].replace({
            1: "✅ Correct", 0: "❌ Incorrect", True: "✅ Correct", False: "❌ Incorrect"
        })

        summary_df.reset_index(drop=True, inplace=True)

        st.dataframe(summary_df, use_container_width=True,hide_index=True)
        if st.checkbox("🔍 Show Attempt-wise Summary Count"):
            attempt_summary = summary_df.groupby(["Attempts", "Is_Correct"]).size().unstack(fill_value=0)
            st.write("Correct vs Incorrect answers per attempt:")
            st.dataframe(attempt_summary)


    with tab4:
        st.subheader("🎯 Users Who Scored 10/10 on 1st Attempt")
        first_attempt_df = df[df["Attempts"] == 1]
        unique_first_attempt = first_attempt_df.drop_duplicates(subset=["User_id", "Quiz_id"])
        perfect_scorers = unique_first_attempt[unique_first_attempt["Total_Score"] == 10]
        result = perfect_scorers[["Name", "Total_Score", "Attempts"]].drop_duplicates()
        st.metric("🏆 Total Users Scored 10/10 on First Attempt", result.shape[0])
        st.dataframe(result, hide_index=True)

        st.subheader("🔁 User with Maximum Quiz Attempts")
        user_attempts = df.groupby("User_id")["Attempts"].max().reset_index()
        user_attempts = user_attempts.merge(df[["User_id", "Name"]].drop_duplicates(), on="User_id", how="left")
        top_user = user_attempts.loc[user_attempts["Attempts"].idxmax()]
        top_user_df = pd.DataFrame({
            "User ID": [top_user["User_id"]],
            "Name": [top_user["Name"]],
            "Times Attempted": [top_user["Attempts"]]
        })
        st.dataframe(top_user_df, use_container_width=True, hide_index=True)


        attempts_vs_score = df.groupby(["User_id", "Quiz_id"]).agg({
            "Attempts": "max",
            "Total_Score": "max"
        }).reset_index()
        correlation = attempts_vs_score["Attempts"].corr(attempts_vs_score["Total_Score"])
        st.subheader("📊 Attempts vs Score")
        fig = px.scatter(
            attempts_vs_score,
            x="Attempts",
            y="Total_Score",
            hover_data=["User_id"],
            title="Does More Attempts Lead to Better Scores?",
            labels={"Attempts": "Number of Attempts", "Total_Score": "Score"},
        )

        fig.update_traces(
            marker=dict(size=4, color="yellow", opacity=0.6),
            hovertemplate="User ID: %{customdata[0]}<br>Attempts: %{x}<br>Score: %{y}"
        )

        fig.update_layout(
        xaxis=dict(
            tickmode='linear',
            dtick=5,  # Show every 5 attempts on x-axis
            tickangle=0
        )
    )
        st.plotly_chart(fig, use_container_width=True)
        st.success("User with 68 attempts achieved 9 scores whereas users with 1 attempts achieved 10, suggesting that higher attempts do not always correlate with better performance.")

        
