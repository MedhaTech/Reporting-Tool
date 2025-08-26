import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Student Course Progress Dashboard", layout="wide")

st.markdown("<h1 style='text-align: center;'>🧑‍🏫 Student Course Progress Dashboard</h1>", unsafe_allow_html=True)
def  courseprogress_dashboard():
# Load and preprocess data
    df = pd.read_csv("D:\\tst\\data files\\courseprogress1.xls", parse_dates=["created_at", "updated_at"], dayfirst=True)
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['updated_at'] = pd.to_datetime(df['updated_at'], errors='coerce')
    df = df.dropna(subset=['created_at'])

    # Add helper columns
    df['created_date'] = df['created_at'].dt.date
    df['hour'] = df['created_at'].dt.hour + 1  # 0-23 ➝ 1–24
    df['hour'] = df['hour'].apply(lambda x: x if x <= 24 else 1)
    df['weekday'] = df['created_at'].dt.day_name()
    original_df = df.copy()

    # Global Filters
    st.subheader("🔍 Filter Options")
    colf1, colf2 = st.columns(2)
    with colf1:
        user_options = ["All"] + sorted(original_df['user_id'].astype(str).unique())
        selected_user = st.selectbox("👤 Select User", user_options)
    with colf2:
        topic_options = ["All"] + sorted(original_df['course_topic_id'].astype(str).unique())
        selected_topic = st.selectbox("📘 Select Topic", topic_options)

    df = original_df.copy()
    if selected_user != "All":
        df = df[df['user_id'] == int(selected_user)]
    if selected_topic != "All":
        df = df[df['course_topic_id'] == int(selected_topic)]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["👥 User Behavior Insights", "⏰ Time-Based Insights", "📚 Topic Engagement Insights"])

    # ------------------------------------------
    # TAB 1 - USER BEHAVIOR INSIGHTS
    # ------------------------------------------
    with tab1:
        st.subheader("📊 Overall Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("👤 Unique Users", df['user_id'].nunique())
        col2.metric("📘 Total Topics", df['course_topic_id'].nunique())
        col3.metric("✅ Total Completions", df.shape[0])

        st.subheader("👥 Users per Topic")
        users_per_topic = df.groupby('course_topic_id')['user_id'].nunique().reset_index(name='Unique Users')
        fig_users = px.bar(users_per_topic, x='course_topic_id', y='Unique Users',
                        labels={'course_topic_id': 'Topic ID'}, title="Unique Users per Topic")
        st.plotly_chart(fig_users)

        st.subheader("📋 Per-User Progress Report")
        selected_user_id = st.selectbox("🔍 Select a user to view progress", df['user_id'].unique())
        user_data = df[df['user_id'] == selected_user_id].sort_values('created_at')

        if not user_data.empty:
            user_data['next_time'] = user_data['created_at'].shift(-1)
            user_data['gap_minutes'] = (user_data['next_time'] - user_data['created_at']).dt.total_seconds() / 60

            summary = user_data.groupby('course_topic_id').agg(
                Total_Completions=('course_topic_id', 'count'),
                Min_Time=('gap_minutes', 'min'),
                Max_Time=('gap_minutes', 'max')
            ).reset_index()

            summary['Min_Time'] = summary['Min_Time'].fillna(0).round(2)
            summary['Max_Time'] = summary['Max_Time'].fillna(0).round(2)

            st.dataframe(summary.rename(columns={
                'course_topic_id': 'Course Topic',
                'Total_Completions': 'Completions',
                'Min_Time': 'Min Time (min)',
                'Max_Time': 'Max Time (min)'
            }))
        else:
            st.warning("No data available for the selected user.")

        st.subheader("📊 Sequential Drop-Off Detection & Completion Analysis")
        topic_order = sorted(original_df['course_topic_id'].unique())
        sequential_results = []
        sequential_by_date = []

        for i, topic in enumerate(topic_order):
            eligible_users = set()
            completed_users = set()
            completion_dates = []

            for user_id, group in original_df.groupby('user_id'):
                user_topics = group.sort_values('created_at')
                topics = user_topics['course_topic_id'].tolist()
                if i == 0:
                    if topic in topics:
                        eligible_users.add(user_id)
                        completed_users.add(user_id)
                        min_created_at = pd.to_datetime(user_topics[user_topics['course_topic_id'] == topic]['created_at'].min(), errors='coerce')
                        if pd.notnull(min_created_at):
                            completion_dates.append(min_created_at.date())
                else:
                    prev_topic = topic_order[i - 1]
                    if prev_topic in topics:
                        eligible_users.add(user_id)
                        if topic in topics:
                            completed_users.add(user_id)
                            min_created_at = pd.to_datetime(user_topics[user_topics['course_topic_id'] == topic]['created_at'].min(), errors='coerce')
                            if pd.notnull(min_created_at):
                                completion_dates.append(min_created_at.date())

            total_eligible = len(eligible_users)
            total_completed = len(completed_users)
            drop_off = total_eligible - total_completed
            completion_pct = round((total_completed / total_eligible) * 100, 2) if total_eligible > 0 else 0.0
            dropoff_pct = round(100 - completion_pct, 2)

            sequential_results.append({
                'Topic ID': topic,
                'Eligible Users': total_eligible,
                'Completed Users': total_completed,
                'Drop-off Count': drop_off,
                'Completion %': completion_pct,
                'Drop-off %': dropoff_pct
            })

            for date in completion_dates:
                sequential_by_date.append({'Topic ID': topic, 'Date': date})

        seq_df = pd.DataFrame(sequential_results)
        st.dataframe(seq_df)

        st.subheader("📈 Completions per Topic")
        fig_completions = px.bar(seq_df, x='Topic ID', y='Completed Users',
                                text='Completed Users', title="Completions per Topic")
        fig_completions.update_traces(marker_color='green', textposition='outside')
        st.plotly_chart(fig_completions)

        st.subheader("📉 Drop-off % per Topic")
        fig_dropoff = px.bar(seq_df, x='Topic ID', y='Drop-off %',
                            color='Drop-off %', color_continuous_scale='Reds',
                            text='Drop-off %', title="Drop-off Percentage per Topic")
        fig_dropoff.update_traces(texttemplate='%{text}%', textposition='outside')
        st.plotly_chart(fig_dropoff)

        st.markdown("""
        - This shows how many users continued from one topic to the next in a sequential learning path.
        - Drop-off % highlights where users lose interest.
        - Completion % shows what fraction progressed to the current topic.
        """)

        st.subheader("📉 Sequential Drop-Off Trend by Topic (Over Time)")
        seq_date_df = pd.DataFrame(sequential_by_date)
        if not seq_date_df.empty:
            trend = seq_date_df.groupby(['Date', 'Topic ID']).size().reset_index(name='Completions')
            fig_seq_trend = px.bar(trend, x='Date', y='Completions', color='Topic ID',
                                title="Sequential Completion Trend Over Time", barmode='group')
            st.plotly_chart(fig_seq_trend)
        else:
            st.info("No sequential completion data available for plotting.")

    # ------------------------------------------
    # TAB 2 - TIME-BASED INSIGHTS
    # ------------------------------------------

    with tab2:
        st.subheader("📅 Activity Heatmap (Weekday x Hour)")

        # Shift hour to 1–24
        df['hour'] = df['created_at'].dt.hour + 1
        df['hour'] = df['hour'].apply(lambda x: x if x <= 24 else 1)

        # Group by weekday and hour
        heatmap_df = df.groupby(['weekday', 'hour']).size().reset_index(name='completions')
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_df['weekday'] = pd.Categorical(heatmap_df['weekday'], categories=weekday_order, ordered=True)

        # Pivot for heatmap
        pivot = heatmap_df.pivot(index='weekday', columns='hour', values='completions').fillna(0)
        pivot = pivot.reindex(columns=range(1, 25), fill_value=0)

        # Plot heatmap
        fig_heat = px.imshow(
            pivot,
            x=list(range(1, 25)),
            y=pivot.index,
            color_continuous_scale="Viridis",
            labels=dict(x="Hour", y="Day", color="Completions"),
            title="User Activity Heatmap by Hour (1–24) & Day"
        )

        # Force display of all x-axis tick labels 1–24
        fig_heat.update_xaxes(
            tickmode='array',
            tickvals=list(range(24)),  # because imshow uses zero-based indexing
            ticktext=[str(i) for i in range(1, 25)],
            title_text="Hour"
        )

        st.plotly_chart(fig_heat, use_container_width=True)

        st.subheader("🔁 Most Revisited Topics (Using updated_at)")
        revisits = df[df['updated_at'] > df['created_at']]
        revisit_counts = revisits.groupby('course_topic_id')['user_id'].nunique().reset_index(name='Revisited Users')

        fig_revisit = px.bar(
            revisit_counts.sort_values('Revisited Users', ascending=False),
            x='course_topic_id',
            y='Revisited Users',
            title="Most Revisited Topics",
            color='Revisited Users'
        )
        st.plotly_chart(fig_revisit, use_container_width=True)

    # TAB 3 - TOPIC ENGAGEMENT
    # ------------------------------------------
    with tab3:
        st.subheader("📈 Topic Completion Trend (All Topics)")
        trend = df.groupby(['created_date', 'course_topic_id']).size().reset_index(name='Completions')
        fig_trend = px.line(trend, x='created_date', y='Completions', color='course_topic_id',
                            title="Topic Completion Over Time")
        st.plotly_chart(fig_trend)

        st.subheader("🔍 View Topic Completion Trend by ID")
        topic_ids = df['course_topic_id'].unique()
        selected_topic_id = st.selectbox("Select a Topic to Filter", sorted(topic_ids))
        trend_filtered = df[df['course_topic_id'] == selected_topic_id]
        trend_filtered_grouped = trend_filtered.groupby('created_date').size().reset_index(name='Completions')

        if not trend_filtered_grouped.empty:
            fig_topic = px.line(trend_filtered_grouped, x='created_date', y='Completions',
                                title=f"Completion Trend for Topic {selected_topic_id}")
            st.plotly_chart(fig_topic)
        else:
            st.warning("No data available for the selected topic.")

        st.subheader("🏆 Most & Least Completed Topics")
        topic_completions = df['course_topic_id'].value_counts().reset_index()
        topic_completions.columns = ['Topic ID', 'Total Completions']
        top_topic = topic_completions.iloc[0]
        bottom_topic = topic_completions.iloc[-1]

        col1, col2 = st.columns(2)
        col1.metric("🔥 Most Completed Topic", f"{top_topic['Topic ID']}", f"{top_topic['Total Completions']} Completions")
        col2.metric("❄ Least Completed Topic", f"{bottom_topic['Topic ID']}", f"{bottom_topic['Total Completions']} Completions")