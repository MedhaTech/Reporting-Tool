import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def student_progress_dashboard():
    

    st.set_page_config(
        page_title="Student Progress Dashboard", 
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for better styling
    st.markdown("""
    <style>
        .metric-container {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 1rem;
        }
    </style>
    """, unsafe_allow_html=True)

    # Load and process data with enhanced caching
    @st.cache_data(show_spinner=False)  
    def load_and_process_data():
        """Load and preprocess data with optimized operations"""
        try:
            #with st.spinner("loading"):
            df = pd.read_csv("D:\\tst\\data files\\StudentProgressDetailedReport_3_7_2025 10_10_32.csv")
            
            # Optimize data processing
            df.columns = df.columns.str.strip()
            
            # Vectorized string operations
            df["Course Completion%"] = pd.to_numeric(
                df["Course Completion%"].astype(str).str.replace("%", "").str.strip(), 
                errors="coerce"
            ).fillna(0)
            
            # Optimize categorical processing
            categorical_cols = {
                "Pre Survey Status": lambda x: x.str.strip().str.lower(),
                "Post Survey Status": lambda x: x.str.strip().str.lower(),
                "Idea Status": lambda x: x.str.strip().str.upper(),
                "Gender": lambda x: x.str.strip().str.capitalize(),
                "Disability Type": lambda x: x.str.strip().str.lower(),
                "Class": lambda x: x.str.strip()
            }
            
            for col, func in categorical_cols.items():
                df[col] = func(df[col].astype(str))
            
            return df
        except Exception as e:
            st.error(f"Error loading data: {e}")
            return pd.DataFrame()

    # Cached computation functions
    @st.cache_data
    def compute_overall_metrics(df):
        """Compute overall metrics with caching"""
        completed = (df["Course Completion%"] == 100).sum()
        in_progress = ((df["Course Completion%"] > 0) & (df["Course Completion%"] < 100)).sum()
        not_started = (df["Course Completion%"] == 0).sum()
        avg_completion = df["Course Completion%"].mean()
        
        return {
            'completed': completed,
            'in_progress': in_progress,
            'not_started': not_started,
            'avg_completion': avg_completion,
            'total_students': len(df)
        }

    @st.cache_data
    def compute_demographic_data(df):
        """Compute demographic analysis with caching"""
        gender_completion = df.groupby("Gender")["Course Completion%"].mean().dropna()
        class_completion = df.groupby("Class")["Course Completion%"].mean().sort_values(ascending=False)
        
        with_disability = df[df["Disability Type"] != "no"]
        without_disability = df[df["Disability Type"] == "no"]
        
        return {
            'gender_completion': gender_completion,
            'class_completion': class_completion,
            'disability_counts': {
                'with': len(with_disability),
                'without': len(without_disability),
                'completed_with_disability': (with_disability["Course Completion%"] == 100).sum()
            }
        }

    @st.cache_data
    def compute_performance_data(df):
        """Compute performance metrics with caching"""
        school_performance = df.groupby("School Name")["Course Completion%"].mean().sort_values(ascending=False)
        
        # Active teams criteria
        active_criteria = (
            (df["Course Completion%"] == 100) &
            (df["Pre Survey Status"] == "completed") &
            (df["Post Survey Status"] == "completed") &
            (df["Idea Status"] == "SUBMITTED")
        )
        
        active_teams = df[active_criteria].groupby("Team Name").size().sort_values(ascending=False)
        
        # Low performing teams
        low_performing = df.groupby("Team Name").agg({
            "Course Completion%": ["mean", "count"]
        }).round(2)
        low_performing.columns = ["avg_completion", "student_count"]
        low_performing = low_performing[low_performing["avg_completion"] < 20].sort_values("avg_completion")
        
        return {
            'school_performance': school_performance,
            'active_teams': active_teams,
            'low_performing': low_performing
        }

    @st.cache_data
    def compute_survey_data(df):
        """Compute survey and idea metrics with caching"""
        pre_survey_rate = (df["Pre Survey Status"] == "completed").mean() * 100
        post_survey_rate = (df["Post Survey Status"] == "completed").mean() * 100
        
        idea_counts = df["Idea Status"].value_counts()
        
        idea_submitters = df[df["Idea Status"] == "SUBMITTED"]
        idea_completion_avg = idea_submitters["Course Completion%"].mean() if not idea_submitters.empty else 0
        
        return {
            'pre_survey_rate': pre_survey_rate,
            'post_survey_rate': post_survey_rate,
            'idea_counts': idea_counts,
            'idea_completion_avg': idea_completion_avg
        }

    # Load data
    df = load_and_process_data()

    if df.empty:
        st.error("No data available. Please check your data file.")
        st.stop()

    # Header with key metrics
    st.title("📊 Student Progress Dashboard")

    # Quick stats in header
    col1, col2, col3, col4 = st.columns(4)
    metrics = compute_overall_metrics(df)

    with col1:
        st.metric("Total Students", metrics['total_students'])
    with col2:
        st.metric("Avg Completion", f"{metrics['avg_completion']:.1f}%")
    with col3:
        st.metric("Completed (100%)", metrics['completed'])
    with col4:
        completion_rate = (metrics['completed'] / metrics['total_students'] * 100) if metrics['total_students'] > 0 else 0
        st.metric("Student Progress Success Rate", f"{completion_rate:.1f}%")

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📈 Overall Progress",
        "👥 Demographics",
        "🏫 Performance",
        "📝 Surveys & Ideas",
        "⚠️ Gaps Analysis"
    ])

    # Tab 1: Overall Progress
    with tab1:
        st.subheader("Course Completion Overview")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Completion status pie chart
            labels = ['Completed (100%)', 'In Progress (1-99%)', 'Not Started (0%)']
            values = [metrics['completed'], metrics['in_progress'], metrics['not_started']]
            colors = ['#00cc44', '#ff9900', '#ff4444']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=0.3,
                marker_colors=colors
            )])
            fig.update_layout(
                title="Student Progress Distribution",
                height=400,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Completion rate histogram
            fig = px.histogram(
            df,
            x="Course Completion%",
            nbins=20,
            title="Distribution of Completion Rates",
            color_discrete_sequence=px.colors.sequential.Viridis_r,  # Use any palette here
            labels={'Course Completion%': 'Completion Rate (%)', 'count': 'Number of Students'},
            color="Course Completion%"  # This lets each bin have its own color
        )

            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Demographics
    with tab2:
        st.subheader("Demographic Analysis")
        
        demo_data = compute_demographic_data(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Gender performance
            fig = px.bar(
            x=demo_data['gender_completion'].index,
            y=demo_data['gender_completion'].values,
            title="Average Course Completion Rate by Gender",
            labels={'x': 'Gender', 'y': 'Completion Rate (%)'},
            color=demo_data['gender_completion'].index,  # Add color
            color_discrete_sequence=px.colors.qualitative.Set2  # You can use Set1, Pastel1, Dark2, etc.
        )
            fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            #st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            
        # Class performance (Sorted Descending)
            class_sorted = demo_data['class_completion'].sort_values(ascending=False)

            fig = px.bar(
                x=class_sorted.index,
                y=class_sorted.values,
                title="Average Course Completion Rate by Class",
                labels={'x': 'Class', 'y': 'Completion Rate (%)'},
                color=class_sorted.index,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
            fig.update_layout(showlegend=False)

            st.plotly_chart(fig, use_container_width=True)

        
        # Disability insights
        st.subheader("Disability Insights")
        col1, col2, col3 = st.columns(3)
            
        with col1:
            st.metric("Students with Disabilities", demo_data['disability_counts']['with'])
        with col2:
            st.metric("Students without Disabilities", demo_data['disability_counts']['without'])
        with col3:
            st.metric("Completed (with Disabilities)", demo_data['disability_counts']['completed_with_disability'])

        with col3:
            # Filter disabled students
            # Clean Course Status values first
            df["Course Status"] = df["Course Status"].astype(str).str.strip().str.lower()

                # Filter disabled students
            disabled_students = df[df["Disability Type"] != "no"]

                # Count course statuses (normalize expected categories)
            status_counts = disabled_students["Course Status"].value_counts().reindex(
                    ["completed", "in progress", "not started"], fill_value=0
                ).rename({
                    "completed": "Completed",
                    "in progress": "In Progress",
                    "not started": "Not Started"
                })

                # Create DataFrame for Plotly
            chart_df = pd.DataFrame({
                    "Status": status_counts.index,
                    "Count": status_counts.values
                })

                # Plot
            fig = px.bar(
                    chart_df,
                    x="Status",
                    y="Count",
                    color="Status",
                    color_discrete_map={
                        "Completed": "#4CAF50",
                        "In Progress": "#FFC107",
                        "Not Started": "#F44336"
                    },
                    text="Count",
                    title="♿ Course Progress Among Students With Disabilities"
            )

            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(
                    xaxis_title="Course Status",
                    yaxis_title="Number of Students",
                    showlegend=False,
                    height=400
                )

        left, center, right = st.columns([1, 2, 1])
        with center:
            st.plotly_chart(fig, use_container_width=True)

    # Tab 3: Performance
    with tab3:
        st.subheader("School and Team Performance")
        
        perf_data = compute_performance_data(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top schools
            top_schools = perf_data['school_performance'].head(10)
            fig = px.bar(
                x=top_schools.values,
                y=top_schools.index,
                orientation='h',
                title="Top 10 Schools by Course Completion Rate 100%",
                labels={'x': 'Average Completion Rate (%)', 'y': 'School Name'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Active teams
            if not perf_data['active_teams'].empty:
                top_teams = perf_data['active_teams'].head(10)
                fig = px.bar(
                    x=top_teams.values,
                    y=top_teams.index,
                    orientation='h',
                    title="Most Active Teams All criteria(Presurvey,post survey,course Completion,idea submission)",
                    labels={'x': 'Number of Students', 'y': 'Team Name'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No teams meet all activity criteria")
        
        
        if not perf_data['low_performing'].empty:
            st.subheader("Teams Needing Attention (< 20% avg completion)")
            st.dataframe(perf_data['low_performing'], use_container_width=True)

    # Tab 4: Surveys & Ideas
    with tab4:
        st.subheader("Survey Participation & Idea Submission")
        
        survey_data = compute_survey_data(df)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Survey completion rates
            survey_rates = {
                'Pre Survey': survey_data['pre_survey_rate'],
                'Post Survey': survey_data['post_survey_rate']
            }
            
            fig = px.bar(
                x=list(survey_rates.keys()),
                y=list(survey_rates.values()),
                title="Survey Completion Rates",
                labels={'x': 'Survey Type', 'y': 'Completion Rate (%)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Idea submission status
            fig = px.pie(
                values=survey_data['idea_counts'].values,
                names=survey_data['idea_counts'].index,
                title="Idea Submission Status"
            )
            st.plotly_chart(fig, use_container_width=True)
        
    # Tab 5: Gaps Analysis
    with tab5:
        st.subheader("Engagement Gaps & action Needed")
        
        st.error("🚨 Critical Issues")

        zero_progress_schools = df.groupby("School Name").filter(lambda x: (x["Course Completion%"] == 0).all())
        
        if not zero_progress_schools.empty:
            st.write(f"**Schools with 0% completion for students:** {len(zero_progress_schools)}")
            critical_schools = zero_progress_schools[["School Name", "Team Name", "Teacher Name"]].drop_duplicates()
            st.dataframe(critical_schools, use_container_width=True,hide_index=True)
        
        df["Pre Survey Status"] = df["Pre Survey Status"].str.lower()
        df["Post Survey Status"] = df["Post Survey Status"].str.lower()
        df["Idea Status"] = df["Idea Status"].str.upper()

        no_engagement = df[
            (df["Course Completion%"] == 0) &
            (df["Pre Survey Status"] != "completed") &
            (df["Post Survey Status"] != "completed") &
            (df["Idea Status"] != "SUBMITTED")
        ]

        unique_no_engagement = no_engagement.drop_duplicates(subset=["Student Name"]) 

        if not unique_no_engagement.empty:
            st.write(f"**Unique students with zero engagement across all activities (Course completion,survey, idea submission): {len(unique_no_engagement)}**")
            st.dataframe(unique_no_engagement[["Student Name","Gender","Class","Teacher Name","School Name"]],hide_index=True)
            
            
            # Recommendations
            st.success("💡 Recommendations")
            
            recommendations = [
                "Focus on teams with 0% completion",
                "Engage students who haven't started surveys",
                "Replicate successful strategies from top-performing schools",
                "Provide additional support for students with disabilities",
                "Investigate why some students submit ideas but don't complete courses"
            ]
            
            for i, rec in enumerate(recommendations, 1):
                st.write(f"{i}. {rec}")

