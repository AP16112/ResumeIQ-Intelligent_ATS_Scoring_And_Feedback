#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Project :- ResumeIQ - "Intelligent ATS scoring & feedback"

# ResumeIQ – Intelligent ATS Scoring & Feedback is an AI‑powered web application that evaluates resumes against job descriptions, providing ATS compatibility scores along with clear, actionable feedback. 
# Built with FastAPI, Streamlit, and NLP models like BERT and spaCy, it helps candidates optimize their resumes to improve job search success.

#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Here we will use this app.py file to write out streamlit deployment code here
# Actually Streamlit wants some entry point and this app.py is actually acting as the entry point for this project

# Streamlit is an open‑source Python framework designed to make it easy to build and share data apps, dashboards, and interactive machine learning demos with just a few lines of code.

# What Streamlit does :-
# - Lets you turn a Python script into a web app instantly.
# - Focuses on simplicity — you don’t need HTML, CSS, or JavaScript.
# - Perfect for data scientists, ML engineers, and analysts who want to showcase models or visualizations interactively.

# Key Features :-
# - Widgets: Sliders, buttons, text inputs, file uploaders.
# - Charts: Native support for Matplotlib, Plotly, Altair, and more.
# - Live updates: Apps auto‑refresh when you change code.
# - Deployment: Easy to share via Streamlit Cloud or run locally.




import streamlit as st


# The sys module gives you access to system-level functions and variables.
# Common uses:
# sys.argv → command-line arguments passed to your script.
# sys.exit() → exit the program.
# sys.path → list of directories Python searches for modules.
# sys.version → Python version info.
import sys


# pathlib is a modern library for working with filesystem paths.
# Path is its main class, representing a file or directory path.
# It’s more powerful and readable than using raw strings or os.path
from pathlib import Path

# Put the repo root on sys.path so `from frontend.views import ...` resolves
# regardless of the directory streamlit was launched from.
sys.path.insert(0, str(Path(__file__).parent.parent))
# sys.path :- A list of directories Python searches when you do import something. By default, it includes the current working directory and standard library paths.
# Path(__file__).parent.parent :- __file__ → the path of the current file.
# .parent → the directory containing this file.
# .parent.parent → the directory two levels up (the repo root).
# Example: If this file is at project/frontend/app.py, then:
# Path(__file__) → project/frontend/app.py
# .parent → project/frontend
# .parent.parent → project
# str(...) :- Converts the Path object into a string, since sys.path expects strings.
# sys.path.insert(0, ...) :- Adds the repo root directory to the front of sys.path. This ensures Python looks there first when resolving imports.




# Configure page
st.set_page_config(
    page_title="ResumeIQ : Intelligent ATS scoring & feedback",
    page_icon="🎯",
    layout="wide",    # Controls the default layout width. "wide" → the app stretches across the full browser width. "centered" → content is centered with fixed width.
    initial_sidebar_state="expanded"
    # Controls the sidebar’s default state. "expanded" → sidebar is open when the app loads. "collapsed" → sidebar is hidden initially.
)



# Auth state. Populated by Supabase sign-in / sign-up / OAuth.
# All four are None when signed out, all four are set when signed in.
for key, default in [
    ("access_token", None),
    ("refresh_token", None),
    ("user_id", None),       # Supabase auth user id (uuid); also used by api_client
    ("user_email", None),
    ("auth_error", None),
    ("auth_info", None),
]:
    # Defines the keys we want to track in the Streamlit session.
    if key not in st.session_state:
        st.session_state[key] = default



# This block is handling the Google OAuth callback flow inside your Streamlit app
# If we just came back from Google OAuth, Supabase appends `?code=<authcode>`
# to the redirect URL. Exchange it for a session before rendering anything.
# After Google OAuth, Supabase redirects back to your app with ?code=<authcode> in the URL.
# This condition checks: No user is logged in yet (access_token missing). The URL contains a code query parameter.
if( not st.session_state.access_token and "code" in st.query_params):
    from frontend.services import supabase_client

    # Calls Supabase’s Auth API to exchange the temporary code for a full session.
    # The session includes access_token, refresh_token, and user info.
    result = supabase_client.exchange_code_for_session(st.query_params["code"])

    # e.g When a user clicks “Sign in with Google,” Supabase redirects them back to your app with a URL like: http://localhost:8501/?code=abc123xyz
    # That code=abc123xyz is a temporary authorization code.  
    # Supabase takes the temporary code (abc123xyz) and exchanges it for a full session.


    # Always clear the ?code= param so a refresh doesn't try to re-exchange.
    # Removes ?code=abc123xyz from the URL. Prevents re-exchanging the same code if the user refreshes the page.
    st.query_params.clear()

    if "error" in result:
        st.session_state.auth_error = f"Google sign-in failed: {result['error']}"
    else:
        st.session_state.access_token  = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user_id       = result["user_id"]
        st.session_state.user_email    = result["email"]
        st.rerun()




# Load custom CSS into our streamlit app
def load_css():
    try:
        # __file__ → the path of the current Python file. 
        # .parent → the directory containing this file.
        # / 'assets' / 'styles.css' → appends assets/styles.css to that directory.
        # So if your file is at project/frontend/app.py, this resolves to:
        # project/frontend/assets/styles.css
        css_path = Path(__file__).parent / 'assets' / 'style.css'
        

        # Reads the contents of styles.css. Wraps it inside <style> ... </style> tags so Streamlit can inject it into the page.
        with open(css_path, 'r') as f:
            return f'<style>{f.read()}</style>'
        
    except FileNotFoundError:
        return ''



# st.markdown(...) :- Streamlit’s function to render Markdown text. By default, it only allows safe Markdown (no raw HTML).
# unsafe_allow_html=True :- Tells Streamlit: “It’s okay to render raw HTML tags.”
# Without this, your <style> block would just show up as text instead of applying CSS.
st.markdown(load_css(), unsafe_allow_html=True)



# Initialize session state for view management
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'landing'
    # Sets the default view to "landing". This means when the app first loads, it will show the landing page.




# Sidebar navigation
with st.sidebar:
    st.markdown("## Navigation")
    
    # use_container_width=True makes the button stretch to fill the available width of its container (for a cleaner layout).
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_view = 'landing'
        st.rerun()
    
    if st.button("🎯 ATS Score", use_container_width=True):
        st.session_state.current_view = 'scorer'
        st.rerun()
    
    if st.button("📊 History", use_container_width=True):
        st.session_state.current_view = 'history'
        st.rerun()
    
    if st.button("📚 Resources", use_container_width=True):
        st.session_state.current_view = 'resources'
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 👤 Account")

    from frontend.services import supabase_client

    if st.session_state.access_token:
        # Signed-in state: show email + sign-out button.

        # Streamlit’s function for showing subtle, smaller text (usually gray and slightly smaller than normal text). Ideal for footnotes, hints, or status messages.
        st.caption(f"Signed in as **{st.session_state.user_email}**")

        if st.button("Sign out", use_container_width=True):
            supabase_client.sign_out()    # logs the user out of Supabase authentication.

            for k in ("access_token", "refresh_token", "user_id", "user_email"):
                st.session_state[k] = None

            st.rerun()
    else:
        # Signed-out state: tabs for sign-in vs sign-up + Google OAuth button.
        
        if st.session_state.auth_error:
            # Holds any error message from a failed sign‑in attempt (e.g., wrong password, invalid OAuth code). If it’s not empty, Streamlit displays it with st.error(...) → a red error box.
            # Then it resets the value to None so the message doesn’t keep showing forever.
            st.error(st.session_state.auth_error)
            st.session_state.auth_error = None
        if st.session_state.auth_info:
            st.info(st.session_state.auth_info)
            st.session_state.auth_info = None


        # st.tabs([...]) :- Streamlit function that creates a tabbed interface.
        # Each string in the list becomes a tab label. Here, you get two tabs: Sign in & Sign up
        tab_in, tab_up = st.tabs(["Sign in", "Sign up"])


        # with tab_in: Places this code inside the Sign in tab created earlier.
        with tab_in:
            with st.form("signin_form", clear_on_submit=False):    # clear_on_submit=False means the entered values stay in the text boxes after submission.
                email = st.text_input("Email", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_pw")
                submitted = st.form_submit_button("Sign in", use_container_width=True)
            
            if submitted:
                result = supabase_client.sign_in_with_password(email, password)
                
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.user_email    = result["email"]
                
                st.rerun()


        with tab_up:
            with st.form("signup_form", clear_on_submit=False):
                email_up = st.text_input("Email", key="signup_email")
                password_up = st.text_input("Password (min 6 chars)", type="password", key="signup_pw")
                submitted_up = st.form_submit_button("Create account", use_container_width=True)
            
            if submitted_up:
                result = supabase_client.sign_up_with_password(email_up, password_up)
                
                if "error" in result:
                    st.session_state.auth_error = result["error"]
                elif result.get("pending_confirmation"):
                    # Supabase requires email confirmation for new accounts by default.
                    # If the account was created but not yet confirmed, Supabase sets pending_confirmation=True.
                    # The app then shows a blue info message telling the user to check their email.
                    st.session_state.auth_info = (
                        f"Check your inbox — confirmation email sent to {result['email']}."
                    )
                else:
                    st.session_state.access_token  = result["access_token"]
                    st.session_state.refresh_token = result["refresh_token"]
                    st.session_state.user_id       = result["user_id"]
                    st.session_state.user_email    = result["email"]
                
                st.rerun()

        # This line is adding a styled divider in your Streamlit app to visually separate sections — for example, between “Sign in with Email” and “Sign in with Google”:
        # Creates a <div> containing the text "or".
        st.markdown("<div style='text-align:center; margin: 8px 0; color:#94a3b8;'> or </div>",
                    unsafe_allow_html=True)

        
        # Asks Supabase to generate the Google OAuth login URL. This is the special link that redirects the user to Google’s sign‑in page, then back to your app with a ?code=... parameter.
        oauth = supabase_client.google_oauth_url()

        if "error" in oauth:
            # If Supabase couldn’t generate the URL (e.g., misconfigured credentials), show a small caption message explaining why Google sign‑in isn’t available.
            st.caption(f"Google sign-in unavailable: {oauth['error']}")
        else:
            # Displays a button labeled “Continue with Google”. When clicked, it sends the user to the Google OAuth page.
            # use_container_width=True makes the button stretch across the available space for a clean look.
            st.link_button(
                "Continue with Google",
                url=oauth["url"],
                use_container_width=True,
            )




# Main content area - render based on current view
if st.session_state.current_view == 'landing':
    # Import and render landing page
    from frontend.views import landing
    landing.render()

elif st.session_state.current_view == 'scorer':
    # Import and render scorer page
    from frontend.views import scorer
    scorer.render()

elif st.session_state.current_view == 'history':
    # Import and render history page
    from frontend.views import history
    history.render()

elif st.session_state.current_view == 'resources':
    # Import and render resources page
    from frontend.views import resources
    resources.render()





#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# To run any streamlit application , we use this :-
# streamlit run your_script.py
# Here we will use this :- streamlit run app.py