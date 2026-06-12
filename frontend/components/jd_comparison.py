# This file is the Job Description (JD) comparison display component for our ATS Resume Scorer app.
# Its job is to take the backend’s JD comparison results (resume vs. job description analysis) and render them in Streamlit with metrics, progress bars, and keyword lists.


from typing import Any, Dict, Optional

import streamlit as st


def display_jd_comparison(jd_comparison: Optional[Dict[str, Any]]) -> None:
    if not jd_comparison:
        return  # caller decides whether to render the section at all


    st.markdown("### 🎯 Job Description Match")

    match_pct = float(jd_comparison.get("match_percentage", 0))
    semantic = float(jd_comparison.get("semantic_similarity", 0))
    matched = jd_comparison.get("matched_keywords", []) or []
    missing = jd_comparison.get("missing_keywords", []) or []
    gap = jd_comparison.get("skills_gap", []) or []

    top_l, top_r = st.columns(2)

    with top_l:
        # Displays a labeled metric box. Title: "Match Percentage".
        # Value: match_pct formatted as a whole number percentage (e.g., 82%).
        # This is the overall alignment score between resume and JD.
        st.metric("Match Percentage", f"{match_pct:.0f}%")
        # Shows a horizontal progress bar. match_pct / 100.0 converts the percentage into a fraction between 0 and 1.
        # min(max(..., 0.0), 1.0) clamps the value so it never goes below 0 or above 1.
        # Example: 82.5% → 0.825 → progress bar ~82% filled.
        st.progress(min(max(match_pct / 100.0, 0.0), 1.0))
        st.metric("Semantic Similarity", f"{semantic * 100:.0f}%")
        st.progress(min(max(semantic, 0.0), 1.0))
    
    with top_r:
        st.markdown("**✅ Matched keywords**")
        st.markdown(", ".join(matched[:15]) if matched else "_None matched yet_")


    st.markdown("---")

    bot_l, bot_r = st.columns(2)

    with bot_l:
        st.markdown("**❌ Missing keywords**")

        if missing:
            for kw in missing[:10]:
                st.markdown(f"- {kw}")
        else:
            st.markdown("_All key terms are present!_")
    
    with bot_r:
        st.markdown("**📊 Skills gap**")
    
        if gap:
            for skill in gap[:10]:
                st.markdown(f"- {skill}")
        else:
            st.markdown("_No significant skills gap detected_")