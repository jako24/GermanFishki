from __future__ import annotations

import streamlit as st

def card_editor_modal(card_data: dict, deck_id: int):
    """A modal dialog to edit card details."""
    with st.form(key=f"edit_card_{card_data.get('id', 'new')}"):
        st.subheader("Edit Card")
        de = st.text_input("German (DE)", value=card_data.get("de", ""))
        en = st.text_input("English (EN)", value=card_data.get("en", ""))
        example = st.text_area("Example Sentence", value=card_data.get("example", ""))
        tags = st.text_input("Tags (comma-separated)", value=card_data.get("tags", ""))
        notes = st.text_area("Notes", value=card_data.get("notes", ""))
        
        submitted = st.form_submit_button("Save Card")
        
        if submitted:
            if not de or not en:
                st.error("German and English fields are required.")
                return None
            
            return {
                "deck_id": deck_id,
                "de": de,
                "en": en,
                "example": example,
                "tags": tags,
                "notes": notes,
                "id": card_data.get("id")
            }
    return None

def grade_buttons():
    """Display SRS grading buttons."""
    st.write("How well did you remember?")
    cols = st.columns(4)
    grade = 0
    if cols[0].button("Again (1)", use_container_width=True):
        grade = 1
    if cols[1].button("Hard (2)", use_container_width=True):
        grade = 2
    if cols[2].button("Good (3)", use_container_width=True):
        grade = 3
    if cols[3].button("Easy (4)", use_container_width=True):
        grade = 4
    return grade

def toast_notifications():
    if 'toast' in st.session_state:
        message, icon = st.session_state.toast
        st.toast(message, icon=icon)
        del st.session_state['toast']

def set_toast(message: str, icon: str = "✅"):
    st.session_state.toast = (message, icon)
