# This file is a Streamlit component for showing general resume improvement suggestions.
# It’s simpler than the detailed feedback modules — it just lists high‑level recommendations provided by the backend analysis.


from typing import Any, Dict

import streamlit as st


def display_recommendations(analysis: Dict[str, Any]) -> None:
    suggestions = analysis.get("suggestions") or []

    if not suggestions:
        return

    st.markdown("### 💡 Recommendations")

    for suggestion in suggestions:
        st.markdown(f"- {suggestion}")