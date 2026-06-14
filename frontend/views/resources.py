# This file will show the resources & tips for our resume.

import streamlit as st


def render():
    """Render the resources page"""
    
    st.title("📚 Resources & Tips")
    st.markdown("Learn how to optimize your resume for ATS systems")
    
    # ATS Tips
    st.markdown("## 🎯 ATS Optimization Tips")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### ✅ Do's
        - Use clear, standard section headings (e.g., Education, Experience, Skills)
        - Incorporate relevant keywords from the job description
        - Keep formatting simple, consistent, and easy to scan
        - List skills explicitly
        - Highlight achievements with measurable results (numbers, percentages, impact)
        - Use standard fonts (Arial, Calibri, Times New Roman)
        - Save as PDF or DOCX
        """)
    
    with col2:
        st.markdown("""
        ### ❌ Don'ts
        - Avoid tables and text boxes
        - Don't use headers/footers for important info
        - Avoid images and graphics
        - Don't use unusual fonts
        - Avoid columns (use single column layout)
        - Don't keyword stuff
        - Avoid abbreviations without spelling out first
        """)
    
    st.markdown("---")
    
    # Common ATS Keywords
    st.markdown("## 🔑 Common ATS Keywords by Industry")
    
    # This line is creating a tabbed interface in Streamlit with three tabs, each labeled with text and an emoji
    # st.tabs([...]) :- Streamlit’s tabs function creates multiple tab sections in the app.
    # Each string in the list is the label for one tab.
    # Emojis are allowed, so you can make the UI more visually engaging.
    tab1, tab2, tab3 = st.tabs(["💻 Tech", "💼 Business", "🎨 Creative"])
    
    with tab1:
        st.markdown("""
        ### Software Development :- 
        - **Languages:** Python, Java, JavaScript  
        - **Frameworks & Libraries:** React, Django, Spring  
        - **Tools & Platforms:** Git, Docker, Kubernetes  
        - **Practices:** Agile, Scrum, CI/CD 
        """)
    
    with tab2:
        st.markdown("""
        ### Business & Management :- 
        - **Project Management:** Planning, execution, and delivery  
        - **Stakeholder Engagement:** Communication and collaboration across teams  
        - **Budget Oversight:** Resource allocation and financial tracking  
        - **Strategic Planning:** Long-term vision and goal setting  
        - **Team Leadership:** Guiding, mentoring, and motivating teams
        """)
    
    with tab3:
        st.markdown("""
        ### Creative & Design :- 
        - **Design Tools:** Adobe Creative Suite (Photoshop, Illustrator, XD)  
        - **UI/UX Design:** User-centered interfaces and experiences  
        - **Wireframing & Prototyping:** Turning ideas into interactive mockups  
        - **Brand Identity:** Logos, typography, and cohesive visual systems  
        - **Visual Communication:** Storytelling through graphics and layouts 
        """)

