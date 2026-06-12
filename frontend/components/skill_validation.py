# This file is the Skill Validation display component in our ATS Resume Scorer app. 
# It takes the backend’s skill_validation_details and renders them in Streamlit so users can see which skills were validated against projects/experience and which weren’t.



from typing import Any, Dict

import streamlit as st


def display_skill_validation(analysis: Dict[str, Any]) -> None:
    details = analysis.get("skill_validation_details") or {}

    validated = details.get("validated", [])
    unvalidated = details.get("unvalidated", [])
    total = details.get("total", len(validated) + len(unvalidated))
    pct = details.get("validation_pct", 0.0)

    st.markdown("### ✅ Skill Validation")

    if total == 0:
        st.info("No skills detected on the resume.")
        return

    c1, c2, c3 = st.columns(3)

    # Here we have three side‑by‑side metric cards in Streamlit to summarize skill validation results
    # Displays a metric card labeled “Total Skills”.
    # Shows the numeric value of total (the total number of skills detected in the resume).
    c1.metric("Total Skills", total)
    c2.metric("Validated", len(validated))
    c3.metric("Validation %", f"{pct:.0f}%")

    # It is rendering a progress bar in Streamlit to visually show the skill validation percentage, while making sure the value stays within valid bounds:
    st.progress(min(max(pct / 100.0, 0.0), 1.0))

    if validated:
        with st.expander(f"✅ Validated skills ({len(validated)})", expanded=False):
            for entry in validated:
                skill = entry.get("skill", "?")
                projects = entry.get("projects", []) or []
                similarity = entry.get("similarity")

                project_text = ", ".join(projects[:3]) if projects else "experience section"
                
                sim_text = f" ({similarity * 100:.0f}% match)" if isinstance(similarity, (int, float)) else ""
                st.markdown(f"- **{skill}**{sim_text} — demonstrated in: {project_text}")

    if unvalidated:
        with st.expander(f"⚠️ Unvalidated skills ({len(unvalidated)})", expanded=False):
            st.caption("These skills are listed but not tied to a project or experience bullet.")
            
            for skill in unvalidated:
                st.markdown(f"- ❌ {skill}")