import streamlit as st
import pandas as pd
from fishki import data_store, csv_io
from fishki.ui import set_toast, toast_notifications

st.set_page_config(page_title="Manage Decks", page_icon="🗂️", layout="wide")

# Initialize data from CSV files into session state
if 'decks_df' not in st.session_state or 'cards_df' not in st.session_state:
    st.session_state.decks_df, st.session_state.cards_df = data_store.load_data()

st.header("🗂️ Manage Decks and Cards")

# Load data from session state
decks_df = st.session_state.decks_df
cards_df = st.session_state.cards_df
toast_notifications()

# Deck Management
st.subheader("Decks")
decks = data_store.get_decks(decks_df)
deck_options = {d['id']: d['name'] for d in decks} if decks else {}

col1, col2 = st.columns(2)
with col1:
    selected_deck_id = st.selectbox(
        "Select a deck to view:",
        options=list(deck_options.keys()),
        format_func=lambda x: deck_options.get(x, "No decks"),
        index=0 if deck_options else None
    )

with col2:
    with st.expander("Create New Deck"):
        with st.form("new_deck_form"):
            new_deck_name = st.text_input("Deck Name")
            new_deck_desc = st.text_area("Description (optional)")
            if st.form_submit_button("Create Deck"):
                if new_deck_name:
                    st.session_state.decks_df = data_store.add_deck(decks_df, new_deck_name, new_deck_desc)
                    data_store.save_data(st.session_state.decks_df, cards_df)
                    set_toast(f"Deck '{new_deck_name}' created!")
                    st.rerun()
                else:
                    st.error("Deck name is required.")

if not selected_deck_id:
    st.info("Create a deck to start adding cards.")
    st.stop()

deck_name = deck_options.get(selected_deck_id, "Unknown")
st.write(f"### Cards in '{deck_name}'")

# Card Management
if st.button("➕ Add New Card"):
    # Using a simple form in an expander instead of a modal dialog for simplicity
    with st.expander("Add a New Card", expanded=True):
        with st.form("new_card_form"):
            de = st.text_input("German (DE)")
            en = st.text_input("English (EN)")
            example = st.text_area("Example Sentence")
            tags = st.text_input("Tags (comma-separated)")
            notes = st.text_area("Notes")
            
            if st.form_submit_button("Save Card"):
                if de and en:
                    new_card_data = {
                        "deck_id": selected_deck_id, "de": de, "en": en,
                        "example": example, "tags": tags, "notes": notes
                    }
                    st.session_state.cards_df = data_store.add_card(cards_df, new_card_data)
                    data_store.save_data(decks_df, st.session_state.cards_df)
                    set_toast("Card added successfully.")
                    st.rerun()
                else:
                    st.error("German and English fields are required.")

# Display Cards
cards = data_store.get_cards(cards_df, deck_id=selected_deck_id)
if cards:
    display_df = pd.DataFrame(cards)
    st.dataframe(display_df[['de', 'en', 'example', 'tags', 'box', 'due_date']], width='stretch')
else:
    st.write("No cards in this deck yet.")

# Actions
st.subheader("Deck Actions")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("🗑️ Delete Current Deck", type="primary"):
        decks_df, cards_df = data_store.delete_deck(decks_df, cards_df, selected_deck_id)
        st.session_state.decks_df, st.session_state.cards_df = decks_df, cards_df
        data_store.save_data(decks_df, cards_df)
        set_toast(f"Deck '{deck_name}' deleted.", icon="🗑️")
        st.rerun()

with c2:
    with st.expander("📤 Export to CSV"):
        csv_data = csv_io.write_csv(cards)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"fishki_deck_{deck_name.replace(' ','_')}.csv",
            mime="text/csv",
        )

with c3:
    with st.expander("📥 Import from CSV"):
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv", key="csv_uploader")

        # Check if a file has been uploaded and not yet processed
        if uploaded_file is not None and st.session_state.get('last_uploaded_file_id') != uploaded_file.file_id:
            try:
                imported_cards = csv_io.read_csv(uploaded_file)
                temp_cards_df = cards_df
                for card_data in imported_cards:
                    card_data['deck_id'] = selected_deck_id
                    temp_cards_df = data_store.add_card(temp_cards_df, card_data)
                
                st.session_state.cards_df = temp_cards_df
                data_store.save_data(decks_df, st.session_state.cards_df)
                
                # Mark this file as processed by storing its unique ID
                st.session_state.last_uploaded_file_id = uploaded_file.file_id
                
                set_toast(f"Imported {len(imported_cards)} cards.")
                st.rerun()
            except Exception as e:
                st.error(f"Error during import: {e}")
                # Reset on error to allow re-uploading the same file after fixing it
                if 'last_uploaded_file_id' in st.session_state:
                    del st.session_state.last_uploaded_file_id
