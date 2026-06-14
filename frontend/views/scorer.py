# This file shows the web page for our ATS Resume Scorer — the main interface where users upload resumes, optionally add a job description, run analysis, and export results.


from typing import Optional

import requests
import streamlit as st

# Here we are importing a custom module called api_client from our project’s frontend/services package.
from frontend.services import api_client
# here we are actually importing this api_client.py file so that we can directly use any of the functions that we define inside that.

from frontend.components.dashboard import display_results_dashboard




# This function is a helper that standardizes job description (JD) input into a plain text string for your backend analysis
def _read_jd(jd_file, jd_text: str) -> str:
    """
    Turn whatever the user provided into a plain JD string for the backend.

    For .txt files we decode in-process — that's a trivial operation, no need
    for a backend round-trip. For PDF/DOCX, we'd need the backend's parser;
    we don't have a public endpoint for that, so we ask the user to paste text
    instead for non-txt JDs.
    """
    # SO it means that we are only allowing user to either upload the text file for JD or either paste the JD text & not some PDF or DOCX file.

    if jd_text:     # If user pasted JD text
        # If the user typed or pasted text into a text area, return that directly. .strip() removes leading/trailing whitespace.
        return jd_text.strip()
    

    # If neither text nor file is provided, return an empty string. This signals “no job description” to the backend.
    if jd_file is None:
        return ""
    
    # If JD file is a .txt
    # If the uploaded file ends with .txt, read its contents directly. Decodes the raw bytes into a UTF‑8 string.
    # Ignores any decoding errors to avoid crashes.
    if jd_file.name.lower().endswith(".txt"):
        # jd_file is the uploaded file object from Streamlit’s st.file_uploader. .getvalue() reads the entire file contents into memory as raw bytes.
        return jd_file.getvalue().decode("utf-8", errors="ignore")
        # .decode("utf-8", errors="ignore") :- Converts those raw bytes into a string using UTF‑8 encoding. UTF‑8 is the standard encoding for text files.
        # errors="ignore" means: If there are invalid byte sequences (e.g., corrupted characters), they are silently skipped. Prevents the app from crashing due to decoding errors.
    
    st.warning(
        "Job description files must be `.txt`, so for now — paste the JD text instead "
        "if you have a PDF or DOCX."
    )
    
    return ""




def _show_backend_error(exc: Exception) -> None:
    """Translate a `requests` exception into a friendly Streamlit error."""
    
    if isinstance(exc, requests.ConnectionError):
        st.error("Could not reach the backend. Check URL is valid or not?")
    elif isinstance(exc, requests.Timeout):
        st.error("The backend took too long to respond. Try a smaller resume or check the server logs.")
    elif isinstance(exc, requests.HTTPError) and exc.response is not None:
        # This branch runs if the backend responded with an HTTP error (like 400, 404, 500). exc.response contains the actual HTTP response object from the backend.
        try:
            # Attempts to parse the backend’s response body as JSON. If JSON parsing succeeds, it looks for a "detail" field (common in FastAPI error responses).
            # If parsing fails (response isn’t JSON), it falls back to the raw response text.
            # This ensures the user sees a meaningful error message regardless of format.
            detail = exc.response.json().get("detail", exc.response.text)
        except ValueError:
            detail = exc.response.text
        
        st.error(f"Backend returned {exc.response.status_code}: {detail}")
    else:
        st.error(f"Unexpected error: {exc}")




# Takes an analysis dictionary (the backend’s resume analysis result).
# Returns a string summary formatted for download.
def _summary_text(analysis: dict) -> str:
    """Tiny client-side text summary for the Download button."""

    score = analysis.get("ATS_score", analysis.get("ats_score", 0))

    # First line: ATS score (rounded to nearest integer).
    # Second line: blank for spacing
    lines = [f"ATS Score: {score:.0f}/100", ""]

    if analysis.get("strengths"):
        # If strengths exist, adds a section header. Each strength is listed with a bullet (-). Adds a blank line after.
        lines.append("STRENGTHS:")
        lines.extend(f"  - {s}" for s in analysis["strengths"])
        lines.append("")
    
    if analysis.get("critical_issues"):
        lines.append("CRITICAL ISSUES:")
        lines.extend(f"  - {s}" for s in analysis["critical_issues"])
        lines.append("")
    
    if analysis.get("suggestions"):
        lines.append("SUGGESTIONS:")
        lines.extend(f"  - {s}" for s in analysis["suggestions"])
    
    # Joins all lines with newline characters.
    # Produces a clean, readable text block.
    return "\n".join(lines)

# e.g it will look like this :- 
# ATS Score: 85/100

# STRENGTHS:
#   - Strong keyword optimization
#   - Error-free grammar

# CRITICAL ISSUES:
#   - Poor formatting
#   - Missing project evidence

# SUGGESTIONS:
#   - Add quantifiable achievements
#   - Improve ATS compatibility





# It shows the start of the upload area UI in our ATS Resume Scorer page
# Defines a helper function that builds the resume and job description upload section of the page.
# Takes analysis_mode as input (either "General ATS Score" or "Job Description Comparison").
# Returns three values:
# resume_file: the uploaded resume file.
# jd_file: the uploaded job description file (if .txt).
# jd_text: the pasted job description text.
def _render_upload_area(analysis_mode: str):
    """Two-column upload widgets. Returns (resume_file, jd_file, jd_text)."""
    
    left, right = st.columns(2)

    with left:
        st.markdown("### 📄 Upload Resume")

        resume_file = st.file_uploader(
            "Choose your resume file",
            type=["pdf", "doc", "docx"],
            help="Supported: PDF, DOC, DOCX (max 5 MB)",     # Shows a tooltip (help) explaining supported formats and size limit.
            key="resume_upload",   # Uses a unique key ("resume_upload") so Streamlit can track this widget across reruns.
        )
        # Returns a file object if the user uploads something, otherwise None.

        if resume_file:
            #  .size (bytes), and .getvalue() (raw file content).
            # Its size, converted from bytes to kilobytes (/ 1024) and formatted to one decimal place.
            st.success(f"✅ {resume_file.name} ({resume_file.size / 1024:.1f} KB)")


    # jd_file: Optional[object] = None :- Declares a variable jd_file that may hold an uploaded file object (from st.file_uploader).
    # Uses a type hint Optional[object]: Means jd_file can either be a file object or None. Starts with None because no file is uploaded yet.
    # If the user uploads job.txt, jd_file will be that file object.
    jd_file: Optional[object] = None
    jd_text = ""

    with right:
        if analysis_mode == "Job Description Comparison":
            st.markdown("### 📋 Job Description")
            
            # Displays a set of options as radio buttons (only one can be selected at a time). Returns the selected option as a string, stored in jd_method.
            jd_method = st.radio(
                "Input method:",
                ["Paste Text", "Upload .txt File"],
                horizontal=True,   # Displays the radio buttons side by side (horizontally) instead of stacked vertically.
                key="jd_input_method",
            )

            if jd_method == "Upload .txt File":
                jd_file = st.file_uploader(
                    "Choose JD file (.txt only)",
                    type=["txt"],
                    key="jd_upload",
                )

                if jd_file:
                    st.success(f"✅ {jd_file.name}")
            else:
                jd_text = st.text_area(
                    "Paste job description text:",
                    height=200,
                    placeholder="Paste the JD here...",
                    key="jd_text",
                )

                if jd_text:
                    st.success(f"✅ {len(jd_text)} characters")
        else:
            st.markdown("### 📋 Job Description")

            st.info("Switch to 'Job Description Comparison' mode to enable JD matching.")

    return resume_file, jd_file, jd_text





# It is the start of the export section in our ATS Resume Scorer page. It sets up the UI where users can download their analysis results:
def _render_export_buttons(analysis: dict) -> None:
    st.markdown("### 📥 Export Results")

    c1, c2 = st.columns(2)

    with c1:
        # Lazy: only call the backend the first time the user clicks this button.
        if st.button("📑 Generate PDF Report", use_container_width=True, type="primary"):
            try:
                # Shows a loading spinner with the message while the backend is working. Keeps the user informed that the system is busy generating the PDF.
                with st.spinner("Generating PDF on backend..."):
                    # Calls your backend API to generate a PDF report from the analysis dictionary. Uses the user’s access_token for authentication. Returns raw PDF bytes (pdf_bytes).
                    pdf_bytes = api_client.generate_pdf(
                        analysis,
                        access_token=st.session_state["access_token"],
                    )

                # Saves the generated PDF in Streamlit’s session state.
                # This allows the app to later show a Download button without regenerating the PDF, we already have the pdf bytes report in session state.
                st.session_state["scorer_pdf_bytes"] = pdf_bytes
            except requests.RequestException as exc:
                _show_backend_error(exc)

        if "scorer_pdf_bytes" in st.session_state:
            st.download_button(
                "⬇️ Download PDF",
                data=st.session_state["scorer_pdf_bytes"],
                file_name="ats_resume_report.pdf",
                mime="application/pdf",
                use_container_width=True,
                key="download_pdf_report",
            )

    with c2:
        st.download_button(
            "📄 Download Summary (.txt)",
            data=_summary_text(analysis),
            file_name="ats_summary.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_summary",
        )





def render() -> None:
    st.title("🎯 ATS Resume Score")

    st.markdown("Upload your resume — and optionally a job description — for a comprehensive analysis.")

    with st.sidebar:
        st.markdown("---")
        st.markdown("## 📊 Analysis Options")
        st.info(
            "**General ATS Score**: resume only — overall compatibility.\n\n"
            "**JD Comparison**: resume + job description — targeted match analysis."
        )

    st.markdown("---")

    analysis_mode = st.radio(
        "Select Analysis Mode:",
        ["General ATS Score", "Job Description Comparison"],
        horizontal=True,
    )

    st.markdown("---")

    resume_file, jd_file, jd_text = _render_upload_area(analysis_mode)

    st.markdown("---")

    if not resume_file:
        st.info("👆 Upload your resume to begin.")

        # If we have a prior result in session, render it again.
        # Checks if there’s a cached analysis result stored in st.session_state.
        # If yes, it calls display_results_dashboard(...) to show that result again.
        # This way, users can still see their last analysis even if they haven’t uploaded a new file yet.
        if st.session_state.get("scorer_analysis"):
            display_results_dashboard(st.session_state["scorer_analysis"])
        
        return


    access_token = st.session_state.get("access_token")

    if not access_token:
        st.warning("⚠️ Sign in from the sidebar to analyze a resume.")
        return


    # The function returns three column objects. We only care about the middle column, so:
    # _ (underscore) is used as a throwaway variable for the left and right columns. mid stores the middle column object.
    _, mid, _ = st.columns([1, 2, 1])

    with mid:
        analyze = st.button("🚀 Analyze Resume", use_container_width=True, type="primary")


    # Runs when the user hasn’t clicked the button yet.
    # Also runs on Streamlit reruns (e.g., after generating a PDF), since the button isn’t actively pressed.
    if not analyze:
        # Re-show previous result on rerun (e.g. after PDF generation).
        if st.session_state.get("scorer_analysis"):
            display_results_dashboard(st.session_state["scorer_analysis"])
        
            _render_export_buttons(st.session_state["scorer_analysis"])
        
        return


    # Fresh analysis — drop any cached PDF/result.
    st.session_state.pop("scorer_pdf_bytes", None)
    st.session_state.pop("scorer_analysis", None)

    job_description = _read_jd(jd_file, jd_text) if analysis_mode == "Job Description Comparison" else ""


    try:
        with st.spinner("Analyzing your resume... this can take 10–30 seconds."):
            analysis = api_client.analyze_resume(
                resume_file=resume_file,
                access_token=access_token,
                job_description=job_description,
            )
    except requests.RequestException as exc:
        _show_backend_error(exc)

        return


    st.session_state["scorer_analysis"] = analysis
    st.success("✅ Analysis complete!")

    display_results_dashboard(analysis)

    _render_export_buttons(analysis)

