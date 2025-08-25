import streamlit as st
from login import login_page, logout

st.set_page_config(page_title="Umagine Dashboards", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    login_page()

else:
    with st.sidebar:
        st.title("📊 Dashboard")
        #st.success(f"Logged in as: {st.session_state.username}", icon="✅")

        section = st.radio("Go to", [
            "Teacher Registration",
            "School Registration",
            "Teacher Course Timestamp",
            "Teacher Progress Dashboard",
            "Pre Survey Dashboard",
            "Student Course Progress",
            "Quiz 1 Dashboard",
            "Quiz 2 Dashboard",
            "Quiz 3 Dashboard",
            "Quiz 4 Dashboard",
            "Quiz 5 Dashboard",
            "Submitted Ideas",
            "Student Progress Dashboard",
            "Post Survey Dashboard"
        ])
        
        if st.button("🚪 Logout"):
            logout()
    with st.spinner("🔄 Loading dashboard..."):
        if section == "Quiz 1 Dashboard":
            from quiz1 import quiz1_dashboard
            quiz1_dashboard()
        elif section == "Quiz 2 Dashboard":
            from quiz2 import quiz2dashboard
            quiz2dashboard()
            

        elif section == "Quiz 3 Dashboard":
            from quiz3 import quiz3dashboard
            quiz3dashboard()

        elif section == "Quiz 4 Dashboard":
            from quiz4 import quiz4_dashboard
            quiz4_dashboard()

        elif section == "Quiz 5 Dashboard":
            from quiz5 import quiz5dashboard
            quiz5dashboard()

        elif section == "Student Progress Dashboard":
            from studentprogress import student_progress_dashboard
            student_progress_dashboard()

        elif section == "Teacher Progress Dashboard":
            from teacherprogress import teacher_progress_dashboard
            teacher_progress_dashboard()

        elif section == "School Registration":
            from student_registration import school_registration_dashboard
            school_registration_dashboard()

        elif section == "Teacher Registration":
            from teacher_registration import teacher_registration_dashboard
            teacher_registration_dashboard()

        elif section == "Student Course Progress":
            from courseprogress import courseprogress_dashboard
            courseprogress_dashboard()

        elif section == "Teacher Course Timestamp":
            from timestamp import timestampdashboard
            timestampdashboard()

        elif section == "Submitted Ideas":
            from submitted_ideas import submitted_ideas_dashboard
            submitted_ideas_dashboard()
        
        elif section == "Post Survey Dashboard":
            from postsurvey import postsurvey_dashboard
            postsurvey_dashboard()
        
        elif section == "Pre Survey Dashboard":
            from presurvey import presurvey_dashboard
            presurvey_dashboard()
