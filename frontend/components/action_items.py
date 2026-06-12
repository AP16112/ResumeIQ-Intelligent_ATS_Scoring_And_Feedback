# This file is a helper module for collecting and displaying “action items” in our ATS Resume Scorer app.
# It takes the backend’s analysis dictionary and turns it into a clear, prioritized list of improvements for the user.


from typing import Any, Dict, List, Tuple

import streamlit as st


SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _collect_action_items(analysis: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Return list of (severity, source_title, action_text)."""

    items: List[Tuple[str, str, str]] = []

    for issue in analysis.get("detailed_feedback") or []:
        level = (issue.get("severity_level") or "low").lower()
        title = issue.get("issue_title", "")

        for action in issue.get("action_items") or []:
            items.append((level, title, action))


    if not items:
        # If no action items were collected (empty list): Falls back to general suggestions from the analysis.
        # Marks them as "medium" severity. Uses "General" as the source title. Ensures the user always gets at least some improvement steps.
        for suggestion in analysis.get("suggestions") or []:
            items.append(("medium", "General", suggestion))

    # It is sorting the collected action items list by severity, so the most urgent issues appear first.
    # items.sort(...) sorts the list in place. By default, .sort() arranges items in ascending order.
    # Here, we provide a custom key function to decide the sort order.
    # For each tuple row in items:
    # row[0] is the severity string ("critical", "high", "medium", "low").
    # SEVERITY_RANK.get(row[0], 99) looks up its numeric rank in the dictionary:
    items.sort(key=lambda row: SEVERITY_RANK.get(row[0], 99))
    # If the severity isn’t found, it defaults to 99 (so unknown severities go last).
    # Since lower numbers come first:
    # "critical" (0) → appears at the top.
    # "high" (1) → next.
    # "medium" (2) → after that.
    # "low" (3) → last.
    # This ensures the most urgent issues are shown first in the UI.

    return items



def display_action_items(analysis: Dict[str, Any]) -> None:
    items = _collect_action_items(analysis)

    if not items:
        return

    st.markdown("### ⚡ Action Items")
    st.caption("Concrete steps to improve your score, sorted by urgency.")

    for level, source, action in items:
        icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(level, "🟢")
        
        st.markdown(f"- {icon} **[{source}]** {action}")