import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt


st.set_page_config(page_title="Teacher Course time stamp", layout="wide")
st.title("📊 Time stamp Dashboard")
def timestampdashboard():
    @st.cache_data(show_spinner=False)
    def load_data():
        df = pd.read_csv("processed_timestamp2.xls", parse_dates=[
            "created_at", "next_created_at", "prev_time"])
        df["watch_duration"] = pd.to_timedelta(df["watch_duration"])
        df["time_diff"] = pd.to_timedelta(df["time_diff"])
        return df

    df = load_data()

    # ----------------------------
    # GLOBAL FILTERS
    # ----------------------------
    st.subheader("🔍 Filter Options")
    col1, col2 = st.columns(2)
    with col1:
        selected_user = st.selectbox("👤 Select User", ['All'] + sorted(df['user_id'].unique().tolist()))
    with col2:
        selected_topic = st.selectbox("📘 Select Topic", ['All'] + sorted(df['mentor_course_topic_id'].unique().tolist()))

    filtered_df = df.copy()
    if selected_user != 'All':
        filtered_df = filtered_df[filtered_df['user_id'] == selected_user]
    if selected_topic != 'All':
        filtered_df = filtered_df[filtered_df['mentor_course_topic_id'] == selected_topic]

    # ----------------------------
    # TABS
    # ----------------------------
    behavior_tab, dropoff_tab, time_tab = st.tabs(["👥 User Behavior", "🚫 Drop-off Analysis", "⏱ Time-based Analysis"])

    # ----------------------------
    # TAB 1: User Behavior
    # ----------------------------
    with behavior_tab:
        st.metric("Total Users", filtered_df['user_id'].nunique())

        # Time features
        filtered_df['hour'] = filtered_df['created_at'].dt.hour
        filtered_df['day_of_week'] = filtered_df['created_at'].dt.day_name()
        filtered_df['created_date'] = filtered_df['created_at'].dt.date

        # Summary Data
        hourly = filtered_df['hour'].value_counts().sort_index()
        dow_counts = filtered_df['day_of_week'].value_counts().sort_index()

        st.subheader("🧾 Summary")
        st.markdown(f"- Total Users: {filtered_df['user_id'].nunique()}")
        st.markdown(f"- Total Topics Viewed: {filtered_df['mentor_course_topic_id'].nunique()}")
        if not hourly.empty:
            st.markdown(f"- Most Active Hour: {hourly.idxmax():02d}:00 with {hourly.max()} views")
        if not dow_counts.empty:
            st.markdown(f"- Most Active Day: {dow_counts.idxmax()} with {dow_counts.max()} views")

        # 📊 Most Active Hours (24-hour)
        fig1 = px.bar(
            x=hourly.index,
            y=hourly.values,
            labels={"x": "Hour", "y": "Views"},
            title="Most Active Hours (24-hour format)"
        )
        fig1.update_layout(
            xaxis=dict(
                tickmode="linear",
                dtick=1,
                tickvals=list(range(24)),
                ticktext=[f"{i:02d}" for i in range(24)],
                title="Hour (24-hour format)"
            )
        )
        st.plotly_chart(fig1, use_container_width=True)

        # 📆 Activity by Day of Week
        fig2 = px.bar(
            x=dow_counts.index,
            y=dow_counts.values,
            labels={"x": "Day of the Week", "y": "Views"},
            title="Activity by Day of the Week"
        )
        st.plotly_chart(fig2, use_container_width=True)

        # 📅 Most Active Dates
        daily = filtered_df['created_date'].value_counts().sort_index()
        fig3 = px.bar(
            x=daily.index,
            y=daily.values,
            labels={"x": "Date", "y": "Views"},
            title="Most Active Dates"
        )
        st.plotly_chart(fig3, use_container_width=True)

        # 📘 Topic Completion Counts
        topic_counts = filtered_df['mentor_course_topic_id'].value_counts().reset_index()
        topic_counts.columns = ['Topic', 'Completions']
        fig4 = px.bar(topic_counts, x='Topic', y='Completions', title='Topic Completion Counts')
        st.plotly_chart(fig4, use_container_width=True)

        # 🥧 Course-wise Engagement Share
        users_per_topic = filtered_df.groupby('mentor_course_topic_id')['user_id'].nunique().reset_index()
        users_per_topic.columns = ['Topic', 'Unique Users']
        pie_chart = px.pie(users_per_topic, names='Topic', values='Unique Users', title='Course-wise Engagement Share')
        st.plotly_chart(pie_chart, use_container_width=True)

            # ⏱ Number of Topics Watched Per Session (Horizontal Bar Chart)
        session_lengths = filtered_df.groupby('session_id')['mentor_course_topic_id'].count().reset_index()
        session_lengths.columns = ['Session ID', 'Topics Watched']
        session_lengths = session_lengths.sort_values('Topics Watched', ascending=False)

        fig5 = px.bar(
            session_lengths,
            x='Topics Watched',
            y='Session ID',
            orientation='h',
            hover_data=['Session ID'],
            title='Number of Topics Watched Per Session (Horizontal Bar Chart)'
        )

        fig5.update_layout(
            xaxis_title='Topics Watched',
            yaxis_title='Session ID',
            bargap=0.2,
            height=600
        )
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown("🔍 *Insight*: Each horizontal bar represents a unique session and how many topics were watched in it.")


    # ----------------------------
    # TAB 2: Drop-off Analysis
    # ----------------------------
    with dropoff_tab:
        all_topics = df['mentor_course_topic_id'].nunique()
        user_topic_counts = filtered_df.groupby('user_id')['mentor_course_topic_id'].nunique().reset_index()
        user_topic_counts.columns = ['User', 'Completed Topics']
        user_topic_counts['Drop-off'] = user_topic_counts['Completed Topics'] < all_topics

        fig6 = px.histogram(user_topic_counts[user_topic_counts['Drop-off']], x='Completed Topics', nbins=20,
                            title='Users  Completeled All Topics')
        st.plotly_chart(fig6, use_container_width=True)

        topics_per_user = filtered_df.groupby('user_id')['mentor_course_topic_id'].nunique().reset_index()
        topics_per_user.columns = ['User', 'Topics Completed']
        fig7 = px.histogram(topics_per_user, x='Topics Completed', nbins=20, title='Topics Wise Drop-off Detection')
        st.plotly_chart(fig7, use_container_width=True)

    # ----------------------------
    # TAB 3: Time-Based Analysis
    # ----------------------------
    with time_tab:
        short_views = filtered_df[filtered_df['watch_duration'] < pd.Timedelta(minutes=3)]
        short_view_count = short_views.groupby('mentor_course_topic_id')['user_id'].nunique().reset_index()
        short_view_count.columns = ['Topic', 'Users (<3min)']
        fig8 = px.line(short_view_count, x='Topic', y='Users (<3min)', markers=True,
                    title='Users Who Watched Topic < 3 Minutes')
        fig8.update_traces(line=dict(color='orange', width=3), marker=dict(size=8))
        fig8.update_layout(xaxis_title='Topic ID', yaxis_title='User Count (<3min)')
        st.plotly_chart(fig8, use_container_width=True)