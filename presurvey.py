import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Pre-Survey Dashboard", layout="wide")
st.title("📊 Pre-Survey Dashboard")

@st.cache_data(show_spinner=False)
def presurvey_dashboard():
    st.title("📊 Pre-Survey Dashboard")
    def load_data():
        df = pd.read_excel("cleaned_pre_survey.xlsx")
        return df

    df = load_data()

    tabs = st.tabs([
        "Participation & Exposure",
        "Personal Attributes",
        "Community & Problem-Solving",
        "Action-Based Thinking",
        "Creativity & Expression",
        "Learning Style & Curiosity",
        "Overall Insights"
    ])

    # 1. Participation & Exposure
    with tabs[0]:
        st.subheader("1. Participation & Exposure")

        st.markdown("*Q1: Did you participate in this program last year?*")
        q1 = df[df['question_no'] == 1]
        fig1 = px.bar(q1['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='selected_option', y='count', color='selected_option')
        st.plotly_chart(fig1, use_container_width=True)
        st.caption("📅 Shows how many students are returning participants versus new ones.")

        st.markdown("*Q2: In a school year, how often do you get an opportunity to: Learn using online material like courses, websites or apps*")
        q2 = df[df['question_no'] == 2]
        fig2 = px.bar(q2['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='selected_option', y='count', color='selected_option')
        st.plotly_chart(fig2, use_container_width=True)
        st.caption("🌐 Highlights the frequency of digital learning experiences among students.")

        st.markdown("*Q10: In a school year, how often do you get an opportunity to: Work in pairs or small groups to learn or complete tasks together*")
        q10 = df[df['question_no'] == 10]
        fig10 = px.bar(q10['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='selected_option', y='count', color='selected_option')
        st.plotly_chart(fig10, use_container_width=True)
        st.caption("👥 Captures collaborative learning exposure through peer-based group activities.")

    # 2. Personal Attributes
    with tabs[1]:
        st.subheader("2. Personal Attributes")

        st.markdown("*Q3: Think about your daily life, Which of the following best describes you? [Tick all that apply]*")
        q3 = df[df['question_no'] == 3]
        fig3 = px.bar(q3['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='count', y='selected_option', orientation='h')
        st.plotly_chart(fig3, use_container_width=True)
        st.caption("🧠 Reveals dominant personality traits and habits students see in themselves.")

        st.markdown("*Q4: Think about your daily life, Which of the following best describes you? [Tick all that apply]*")
        q4 = df[df['question_no'] == 4]
        fig4 = px.bar(q4['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='count', y='selected_option', orientation='h')
        st.plotly_chart(fig4, use_container_width=True)
        st.caption("💡 Adds more depth to how students perceive their everyday behavior and mindset.")

        st.markdown("*Q15: How do you feel you express your creativity in the above activity?*")
        q15 = df[df['question_no'] == 15]
        fig15 = px.pie(q15, names='selected_option')
        st.plotly_chart(fig15, use_container_width=True)
        st.caption("🎨 Visualizes how students express creativity through activities like drawing or music.")

        st.markdown("*Q20: What kind of student are you in class?*")
        q20 = df[df['question_no'] == 20]
        fig20 = px.treemap(
            q20['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
            path=['selected_option'],
            values='count',
            hover_data=[]
        )
        fig20.update_traces(hovertemplate='%{label}<br>Count: %{value}<extra></extra>')
        st.plotly_chart(fig20, use_container_width=True)
        st.caption("📚 Maps classroom identities like active participant, silent observer, or question-asker.")

    # 3. Community & Problem-Solving
    with tabs[2]:
        st.subheader("3. Community & Problem-Solving")

        st.markdown("*Q5: If these problems were an issue in your community, which would you pick to solve?*")
        q5 = df[df['question_no'] == 5]
        fig5 = px.bar(q5['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='count', y='selected_option', orientation='h')
        st.plotly_chart(fig5, use_container_width=True)
        st.caption("🏘️ Highlights the community issues students are most motivated to solve.")

        st.markdown("### ❓ Q6: Why did you pick this problem?")
        q6 = df[df['question_no'] == 6]
        q6_summary = q6['selected_option'].value_counts().reset_index()
        q6_summary.columns = ['Reason', 'Count']
        st.dataframe(q6_summary)

        fig_q6 = px.bar(
            q6_summary,
            x='Count',
            y='Reason',
            orientation='h',
            title='Reasons for Picking a Community Problem',
            text='Count',
            color='Count',
            color_continuous_scale='Blues'
        )
        fig_q6.update_layout(xaxis_title='Number of Students', yaxis_title='Reason', height=500)
        st.plotly_chart(fig_q6, use_container_width=True)
        st.caption("📖 Displays student reasoning behind choosing a specific community issue.")

        st.markdown("*Q7: Dental problems in your community — best solution steps?*")
        q7 = df[df['question_no'] == 7]
        fig7 = px.bar(q7['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                    x='selected_option', y='count')
        st.plotly_chart(fig7, use_container_width=True)
        st.caption("🦷 Analyzes how students propose to tackle real-world health problems like dental care.")

    # 4. Action-Based Thinking
    with tabs[3]:
        st.subheader("4. Action-Based Thinking")

        questions = {
            8: "Q8: Which actions did you do before? [Tick all that apply]",
            9: "Q9: Which actions did you do before? [Tick all that apply]",
            11: "Q11: David just had art class... What should David do?",
            16: "Q16: How do you feel about events where you present /speak in front of others?",
            17: "Q17: Think about your last one year at school/home, which of the following best describes you? [Tick all that apply]",
            22: "Q22: What would you do if you were in Raj's position?"
        }

        captions = {
            8: "✅ Tracks past actions students engaged in, such as helping or researching.",
            9: "🧩 Complements Q8 by exploring additional action patterns and student decisions.",
            11: "🧹 A situational decision scenario: Evaluates students' sense of responsibility.",
            16: "🎤 Gauges student comfort and confidence with public speaking events.",
            17: "📆 Provides insight into behaviors and experiences over the past school year.",
            22: "🔧 A creative problem-solving test showing how students think through design challenges."
        }

        for q_no, q_text in questions.items():
            st.markdown(f"*{q_text}*")
            qdf = df[df['question_no'] == q_no]
            fig = px.bar(qdf['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                        x='count', y='selected_option', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
            st.caption(captions[q_no])

    # 5. Creativity & Expression
    with tabs[4]:
        st.subheader("5. Creativity & Expression")

        creativity_questions = {
            12: "Q12: Which of the following activities do you like doing?",
            13: "Q13: How do you feel you express your creativity in the above activity?",
            14: "Q14: Which of the following activities do you like doing?"
        }

        for q_no, q_text in creativity_questions.items():
            st.markdown(f"*{q_text}*")
            qdf = df[df['question_no'] == q_no]
            fig = px.treemap(
                qdf['selected_option'].value_counts().reset_index(name='count').rename(columns={'index': 'selected_option'}),
                path=['selected_option'],
                values='count',
                hover_data=[]
            )
            fig.update_traces(hovertemplate='%{label}<br>Count: %{value}<extra></extra>')
            st.plotly_chart(fig, use_container_width=True)
            st.caption("🎭 Shows student preferences in creative or expressive domains like dance, music, and art.")

    # 6. Learning Style & Curiosity
    with tabs[5]:
        st.subheader("6. Learning Style & Curiosity")

        st.markdown("*Q18: Helping a friend’s traditional art business — What would you do?*")
        q18 = df[df['question_no'] == 18]
        counts18 = q18['selected_option'].value_counts().reset_index(name='count')
        counts18.rename(columns={'index': 'selected_option'}, inplace=True)

        fig18 = px.bar_polar(
            counts18,
            r='count',
            theta='selected_option',
            color='selected_option',
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        st.plotly_chart(fig18, use_container_width=True)
        st.caption("🛍️ Captures student responses to support entrepreneurship and creative thinking.")

        fig18b = px.line_polar(
            counts18,
            r='count',
            theta='selected_option',
            line_close=True,
            color_discrete_sequence=px.colors.sequential.Plasma_r
        )
        st.plotly_chart(fig18b, use_container_width=True)
        st.caption("📈 Reinforces trends in student preferences for action-based problem-solving.")

        st.dataframe(counts18.rename(columns={'selected_option': 'Preferred Action', 'count': 'Total Count'}))

        st.markdown("*Q21: When you have questions, how do you try to find answers?*")
        q21 = df[df['question_no'] == 21]
        counts21 = q21['selected_option'].value_counts().reset_index(name='count')
        counts21.rename(columns={'index': 'selected_option'}, inplace=True)

        fig21 = px.bar(counts21, x='count', y='selected_option', orientation='h')
        st.plotly_chart(fig21, use_container_width=True)
        st.caption("🔎 Highlights curiosity and students' preferred ways of exploring answers independently or collaboratively.")

    # 7. Overall Summary
    with tabs[6]:
        st.header("📌 Overall Summary")
        st.markdown("""
        ✅ *Participation:* Around half are new participants. Many rely on online learning and group work.

        ✅ *Personal Traits:* There's a healthy mix of confident, curious, shy, and reserved personalities.

        ✅ *Community Thinking:* Students care about real issues — dental health, waste, and water lead concerns.

        ✅ *Action Thinking:* Some students show proactive steps; others still need guidance on execution.

        ✅ *Creativity:* Drawing and music are popular; public speaking remains a weaker skill.

        ✅ *Curiosity & Learning:* Most seek help from friends, teachers, or videos — suggesting blended learning.

        This survey offers a strong foundation for personalized and community-based interventions.
        """)