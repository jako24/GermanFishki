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

def save_word_widget(german="", english="", context="", source="Manual"):
    """A reusable widget for saving words to the saved words collection."""
    with st.expander("💾 Save Word", expanded=False):
        with st.form("save_word_form"):
            col1, col2 = st.columns(2)
            with col1:
                german_input = st.text_input("German", value=german, key="save_german")
            with col2:
                english_input = st.text_input("English", value=english, key="save_english")
            
            context_input = st.text_area("Context/Example", value=context, key="save_context")
            notes_input = st.text_area("Notes", placeholder="Any additional notes...", key="save_notes")
            source_input = st.selectbox("Source", ["Manual", "Learn", "Review", "Quiz", "Other"], 
                                      index=["Manual", "Learn", "Review", "Quiz", "Other"].index(source) if source in ["Manual", "Learn", "Review", "Quiz", "Other"] else 0,
                                      key="save_source")
            
            if st.form_submit_button("💾 Save Word", type="primary"):
                if german_input and english_input:
                    from fishki import data_store
                    
                    word_data = {
                        "german": german_input,
                        "english": english_input,
                        "context": context_input,
                        "notes": notes_input,
                        "source": source_input
                    }
                    
                    # Add to saved words
                    st.session_state.saved_words_df = data_store.add_saved_word(
                        st.session_state.saved_words_df, word_data
                    )
                    
                    # Save data
                    data_store.save_data(
                        st.session_state.decks_df, 
                        st.session_state.cards_df, 
                        st.session_state.saved_words_df
                    )
                    
                    set_toast(f"Word '{german_input}' saved successfully!")
                    st.rerun()
                else:
                    st.error("German and English fields are required.")

def quick_save_word_button(german="", english="", context="", source="Manual"):
    """A quick save button that saves the word with minimal interaction."""
    if st.button("💾 Quick Save", help="Save this word for later review"):
        if german and english:
            from fishki import data_store
            
            word_data = {
                "german": german,
                "english": english,
                "context": context,
                "source": source
            }
            
            # Add to saved words
            st.session_state.saved_words_df = data_store.add_saved_word(
                st.session_state.saved_words_df, word_data
            )
            
            # Save data
            data_store.save_data(
                st.session_state.decks_df, 
                st.session_state.cards_df, 
                st.session_state.saved_words_df
            )
            
            set_toast(f"Word '{german}' saved quickly!")
            st.rerun()
        else:
            st.error("Cannot save: German and English are required.")
