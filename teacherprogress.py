import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(page_title="Teacher Progress Dashboard", layout="wide")
def teacher_progress_dashboard():
    st.title("📊 Teacher Progress Dashboard")


    @st.cache_data(show_spinner=False)
    def load_data():
        df = pd.read_excel("D:\\tst\\data files\\cleaned_teacher_progress.xlsx")
        df['Teacher Gender'] = df['Teacher Gender'].astype(str).str.strip().str.replace(r'\s+', ' ', regex=True).str.title()
        df['School Type/Category'] = df['School Type/Category'].astype(str).str.strip().str.upper()
        return df

    df = load_data()


    st.subheader("🔍 Filter Options")
    colf1, colf2, colf3 = st.columns(3)
    with colf1:
        state_filter = st.selectbox("Select State", ['All'] + sorted(df['State'].dropna().unique().tolist()))
    with colf2:
        district_filter = st.selectbox("Select District", ['All'] + sorted(df['District'].dropna().unique().tolist()))
    with colf3:
        gender_filter = st.selectbox("Select Teacher Gender", ['All'] + sorted(df['Teacher Gender'].dropna().unique().tolist()))

    filtered_df = df.copy()
    if state_filter != 'All':
        filtered_df = filtered_df[filtered_df['State'] == state_filter]
    if district_filter != 'All':
        filtered_df = filtered_df[filtered_df['District'] == district_filter]
    if gender_filter != 'All':
        filtered_df = filtered_df[filtered_df['Teacher Gender'] == gender_filter]


    tab1, tab2, tab3, tab4 = st.tabs([
        "👩‍🏫 Teacher Demographics", 
        "📚 Teacher Pre and Post Survey", 
        "🎓 Student and Team Engagement", 
        "📈 Combined Insights"
    ])


    with tab1:
        st.subheader("Gender Distribution")
        gender_data = filtered_df['Teacher Gender'].value_counts().reset_index()
        gender_data.columns = ['Gender', 'Count']
        fig1 = px.bar(gender_data, x='Gender', y='Count', color='Gender', text='Count',
                        color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Teacher Count by District (Top 10 & Bottom 10)")
        district_counts = filtered_df['District'].value_counts().reset_index()
        district_counts.columns = ['District', 'Count']
        top10 = district_counts.head(10).sort_values(by='Count', ascending=True)
        bottom10 = district_counts.tail(10).sort_values(by='Count', ascending=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Top 10 Districts (Largest on Top)**")
            fig_top = px.bar(top10, x='Count', y='District', orientation='h', color='Count',
                                color_continuous_scale='Blues')
            st.plotly_chart(fig_top, use_container_width=True)

        with col2:
            st.markdown("**Bottom 10 Districts**")
            fig_bottom = px.bar(bottom10, x='Count', y='District', orientation='h', color='Count',
                                color_continuous_scale='Reds')
            st.plotly_chart(fig_bottom, use_container_width=True)

        st.subheader("Teacher Count by School Type (ATL vs NON-ATL vs HS vs HSS)")
        school_type_counts = filtered_df['School Type/Category'].value_counts().reset_index()
        school_type_counts.columns = ['School Type/Category', 'Teacher Count']
        fig_school = px.bar(school_type_counts, x='School Type/Category', y='Teacher Count',
                            color='School Type/Category', text='Teacher Count',
                            color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig_school, use_container_width=True)

    with tab2:
        st.subheader("Overall Teacher Course Status")
        status_data = filtered_df['Teacher Course Status'].value_counts().reset_index()
        status_data.columns = ['Course Status', 'Count']
        fig2 = px.bar(status_data, x='Course Status', y='Count', color='Course Status', text='Count',
                        color_discrete_sequence=px.colors.qualitative.Set3)
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Pre vs Post Survey Status")
        pre_counts = df["Teacher Pre Survey Status"].fillna("Unknown").value_counts().reset_index()
        pre_counts.columns = ["Survey Status", "Count"]
        pre_counts["Survey Type"] = "Pre Survey"

        post_counts = df["Teacher Post Survey Status"].fillna("Unknown").value_counts().reset_index()
        post_counts.columns = ["Survey Status", "Count"]
        post_counts["Survey Type"] = "Post Survey"


        survey_combined = pd.concat([pre_counts,post_counts], ignore_index=True)

        
        fig = px.bar(
            survey_combined,
            x="Survey Status",
            y="Count",
            color="Survey Type",
            barmode="group",
            text="Count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title="Pre vs Post Survey Completion Status"
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            xaxis_title="Completion Status",
            yaxis_title="Number of Teachers",
            legend_title="Survey Stage",
            title_font_size=20
        )

        st.plotly_chart(fig, use_container_width=True)


        st.subheader("Course Status by Gender")
        group1 = filtered_df.groupby(['Teacher Gender', 'Teacher Course Status']).size().reset_index(name='Count')
        fig3 = px.bar(group1, x='Teacher Gender', y='Count', color='Teacher Course Status', barmode='group',
                        color_discrete_sequence=px.colors.qualitative.Prism)
        st.plotly_chart(fig3, use_container_width=True)


    with tab3:
        st.subheader("Top 10 Teachers by Teams Created")
        teams_df = filtered_df.groupby("Teacher Name")["NO.of Teams Created"].sum().reset_index()
        top_teams = teams_df.sort_values(by="NO.of Teams Created", ascending=False).head(10)
        fig5 = px.pie(top_teams, names='Teacher Name', values='NO.of Teams Created', title='Top 10 Teachers')
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("Ideas Submitted vs Not Initiated")
        idea_data = {
            "Submitted": filtered_df['No.of Teams Idea Submitted'].sum(),
            "Not Initiated": filtered_df['No.of Teams Idea Not Initiated'].sum()
        }
        fig6 = px.pie(values=idea_data.values(), names=idea_data.keys(), title="Idea Submission Status",
                        color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig6, use_container_width=True)


        state_metrics = df.groupby('State').agg({
        'Teacher Name': 'nunique',
        'NO.of Teams Created': 'sum',
        'No.of Teams Idea Submitted': 'sum'
        }).reset_index()

        state_metrics.columns = ['State', 'No. of Teachers', 'No. of Teams Created', 'No. of Ideas Submitted']
        melted = state_metrics.melt(
            id_vars='State',
            value_vars=['No. of Teachers', 'No. of Teams Created', 'No. of Ideas Submitted'],
            var_name='Metric',
            value_name='Count'
        )
        fig = go.Figure()

        colors = {
            'No. of Teachers': 'orange',
            'No. of Teams Created': 'blue',
            'No. of Ideas Submitted': 'deeppink'
        }

        for metric in melted['Metric'].unique():
            data = melted[melted['Metric'] == metric]
            fig.add_trace(go.Scatter(
                x=data['State'],
                y=data['Count'],
                mode='lines+markers',
                name=metric,
                line=dict(color=colors[metric], width=4),
                marker=dict(size=10, line=dict(color='black', width=1))
            ))

        fig.update_layout(
            title='📊 State-wise No. of Teachers, No. of Teams Created & Ideas submitted',
            xaxis_title='State',
            yaxis_title='Count',
            height=800,
            xaxis_tickangle=45,
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(size=13),
            legend=dict(x=0.5, y=1.15, orientation='h', xanchor='center')
        )

        st.plotly_chart(fig, use_container_width=True)


        st.subheader("Course Engagement")
        engagement_data = filtered_df[[ 
            'No.of Students Course Completed',
            'No.of Students Course Inprogress',
            'No.of Students Course Not Started'
        ]].sum().reset_index()
        engagement_data.columns = ['Course Status', 'Count']
        fig4 = px.bar(engagement_data, x='Course Status', y='Count', color='Course Status', text='Count',
                        color_discrete_sequence=px.colors.sequential.Tealgrn)
        st.plotly_chart(fig4, use_container_width=True)

        
        st.subheader("Students Enrolled vs Completed")
        total_students = filtered_df[['No.of Students Enrolled', 'No.of Students Course Completed']].sum()
        bar_df = pd.DataFrame({
            "Category": total_students.index,
            "Count": total_students.values
        })

        
        fig = px.bar(bar_df, x="Category", y="Count", text="Count")
        fig.update_traces(marker_color='skyblue', textposition='outside')
        fig.update_layout(
            xaxis_tickangle=0, 
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            font_color="white"
        )

        st.plotly_chart(fig, use_container_width=True)

        

        st.subheader("Ideas Submitted by School Type")
        idea_school = filtered_df.groupby("School Type/Category")["No.of Teams Idea Submitted"].sum().reset_index()
        fig7 = px.bar(idea_school, x="School Type/Category", y="No.of Teams Idea Submitted",
                        color="School Type/Category", text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Top Districts by Ideas Submitted")
        idea_district = filtered_df.groupby("District")["No.of Teams Idea Submitted"].sum().reset_index()
        idea_district = idea_district.sort_values(by="No.of Teams Idea Submitted", ascending=False).head(10)
        fig8 = px.bar(idea_district, x="No.of Teams Idea Submitted", y="District", orientation="h",
                        color="No.of Teams Idea Submitted", color_continuous_scale="Agsunset")
        st.plotly_chart(fig8, use_container_width=True)

        st.subheader("Unique Schools per State")
        school_state = filtered_df.groupby("State")["School Name"].nunique().reset_index()
        school_state = school_state.sort_values(by="School Name", ascending=False).rename(columns={"School Name": "Unique Schools"}).head(5)
        fig9 = px.line(school_state, x="State", y="Unique Schools", markers=True)
        st.plotly_chart(fig9, use_container_width=True)


    with tab4:
        st.subheader("Teacher Course Status vs % Students Completed")
        combined = filtered_df.groupby("Teacher Course Status").agg({
            "No.of Students Enrolled": "sum",
            "No.of Students Course Completed": "sum"
        }).reset_index()
        combined["Percentage of student Completed"] = (combined["No.of Students Course Completed"] / combined["No.of Students Enrolled"]) * 100
        fig10 = px.bar(combined, x="Teacher Course Status", y="Percentage of student Completed", color="Teacher Course Status", text_auto=True,
                        color_discrete_sequence=px.colors.qualitative.Vivid)
        st.plotly_chart(fig10, use_container_width=True)

        st.success("💡Conclusion")
        conclusions = [
            "✅ Teachers who completed their courses had the highest student completion rate 69%.",
            "⚠️ Teachers in progress had 15% student completion.",
            "❌ Teachers who didn’t start had lowest student completion 9%."
        ]
        for i, rec in enumerate(conclusions, 1):
            st.write(f"{i}. {rec}")

        

        df["Idea Status"] = df["No.of Teams Idea Submitted"].apply(lambda x: "Submitted" if x > 0 else "Not Submitted")

        # Aggregate data
        idea_engagement = df.groupby("Idea Status").agg({
            "No.of Students Enrolled": "sum",
            "No.of Students Course Completed": "sum",
            "No.of Students Course Inprogress": "sum",
            "No.of Students Course Not Started": "sum"
        }).reset_index()


        for col in ["No.of Students Course Completed", "No.of Students Course Inprogress", "No.of Students Course Not Started"]:
            idea_engagement[col] = (idea_engagement[col] / idea_engagement["No.of Students Enrolled"]) * 100

        
        idea_engagement.rename(columns={
            "No.of Students Course Completed": "Course Completed",
            "No.of Students Course Inprogress": "Course In Progress",
            "No.of Students Course Not Started": "Course Not Started"
        }, inplace=True)

        
        melted_df = idea_engagement.melt(id_vars="Idea Status", 
                                        value_vars=["Course Completed", "Course In Progress", "Course Not Started"],
                                        var_name="Course Status", 
                                        value_name="Percentage of student")


        fig = px.bar(
            melted_df, 
            x="Course Status", 
            y="Percentage of student", 
            color="Idea Status", 
            barmode="group",
            title="Student Engagement Based on Idea Submission",
            text_auto=True,
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            title_font_size=20,
            legend_title_text='Idea Submission',
            xaxis_title='Course Engagement',
            yaxis_title='Percentage of Students',
        )

        st.plotly_chart(fig, use_container_width=True)

        
        st.success("💡Conclusion")
        insights = [
            "Course Completed:-There are 78.9% student who completed course and submitted ideas.Only 14.7% did not submit ideas.",
            "Course In Progress:-There are 7.19% student who are still in progress(doing course) and submitted ideas.Only 7.9% did not submit ideas.",
            "Course Not started:-There are 14.5% student who did not start course but submitted ideas.77.3% student did not start course and did not submit ideas."
        ]
        for i, insight in enumerate(insights, 1):
            st.write(f"{i}. {insight}")