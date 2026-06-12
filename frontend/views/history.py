# This file displays a user’s resume analysis history by talking to our backend API.

import requests

import streamlit as st


# Here we are importing a custom module called api_client from our project’s frontend/services package.
from frontend.services import api_client
# here we are actually importing this api_client.py file so that we can directly use any of the functions that we define inside that.



# This function is a backend error handler for your Streamlit app. It takes an exception (exc) and shows a clear, user‑friendly error message in the UI instead of exposing raw technical details
def _show_backend_error(exc: Exception) -> None:
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Is it running on port 8000?")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        st.error(f"Backend returned {exc.response.status_code}: {exc.response.text}")
    else:
        st.error(f"Unexpected error: {exc}")




def render() -> None:
    st.title("📊 Analysis History")
    st.markdown("Past analyses saved against your account.")

    access_token = st.session_state.get("access_token")

    if not access_token:
        st.warning("⚠️ Sign in from the sidebar to view your history.")
        return

    try:
        # api_client.get_history is a helper function that sends an authenticated request to your backend’s /history endpoint using the user’s access_token. If successful, it returns a list of past resume analyses.
        history = api_client.get_history(access_token)
    except requests.RequestException as exc:
        # Catches any error raised during the request (network issues, invalid response, timeout, etc.).
        # requests.RequestException is a base class for all exceptions in the requests library, so this covers:
        # ConnectionError (backend unreachable)
        # HTTPError (backend returned 4xx/5xx)
        # Timeout
        # Other request‑related failures
        _show_backend_error(exc)

        return
    

    if not history:
        st.info("No analyses yet for this account. Run a scoring on the ATS Scorer page first.")
        
        if st.button("🎯 Go to ATS Scorer"):
            st.session_state.current_view = "scorer"
            st.rerun()
        
        return


    st.markdown(f"**Total analyses:** {len(history)}")
    st.markdown("---")

    # history is a list of dictionaries, each representing one past resume analysis.
    # enumerate(history) gives both:
    # idx: the index (0, 1, 2, …)
    # entry: the actual dictionary for that analysis.
    for idx, entry in enumerate(history):
        filename = entry.get("filename", "resume")
        ats_score = float(entry.get("ats_score", 0))
        created_at = entry.get("created_at", "")
        analysis = entry.get("analysis_result", {}) or {}

        component_scores = analysis.get("component_scores", {}) or {}
        jd_comparison = analysis.get("jd_comparison") or analysis.get("jd_match_analysis")


        # This shows how we displays each resume analysis entry in a collapsible section with metrics laid out in columns:
        # st.expander(...) :- Creates a collapsible container in the UI.
        # The label is dynamically built using f‑string formatting: 📄 → document emoji, {filename} → the resume file name (e.g., "resume1.pdf"), {ats_score:.0f}/100 → the ATS score rounded to 0 decimal places (e.g., "85/100")
        # Users can click this expander to reveal detailed metrics for that analysis.
        with st.expander(f"📄 {filename} — Score: {ats_score:.0f}/100 — {created_at}"):
            c1, c2, c3 = st.columns(3)

            with c1:
                st.metric("Overall", f"{ats_score:.0f}/100")
                st.metric("Formatting", f"{component_scores.get('formatting', 0):.0f}/20")
            
            with c2:
                st.metric("Keywords", f"{component_scores.get('keywords', 0):.0f}/25")
                st.metric("Content", f"{component_scores.get('content', 0):.0f}/25")
            
            with c3:
                st.metric("Skill Validation", f"{component_scores.get('skill_validation', 0):.0f}/15")
                st.metric("ATS Compatibility", f"{component_scores.get('ats_compatibility', 0):.0f}/15")

            if jd_comparison:
                st.markdown(f"**JD Match:** {jd_comparison.get('match_percentage', 0):.0f}%")

            
            # Each history record from the backend has a unique identifier (id).
            # This is needed to tell the backend which analysis entry to delete.
            entry_id = entry.get("id")
            
            if entry_id:
                if st.button("🗑️ Delete", key=f"delete_{idx}"):
                    try:
                        api_client.delete_history_entry(str(entry_id), access_token)
                        st.success("Deleted.")
                        st.rerun()
                    except requests.RequestException as exc:
                        _show_backend_error(exc)