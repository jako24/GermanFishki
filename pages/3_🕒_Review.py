import streamlit as st
import random
from datetime import date
from fishki import data_store, ui
from fishki.srs import grade_card

st.set_page_config(page_title="Review Due Cards", page_icon="🕒", layout="centered")

# Initialize data from CSV files into session state
if 'decks_df' not in st.session_state or 'cards_df' not in st.session_state:
    st.session_state.decks_df, st.session_state.cards_df = data_store.load_data()

st.header("🕒 Review Due Cards")

# Load data from session state
decks_df = st.session_state.decks_df
cards_df = st.session_state.cards_df
ui.toast_notifications()

# Deck selection
decks = data_store.get_decks(decks_df)
if not decks:
    st.info("No decks available. Please create a deck first.")
    st.stop()

deck_options = {d['id']: d['name'] for d in decks}
selected_deck_id = st.selectbox(
    "Choose a deck to review:",
    options=list(deck_options.keys()),
    format_func=lambda x: deck_options[x]
)

if not selected_deck_id:
    st.stop()

# Load or initialize review queue
session_key = f"review_queue_{selected_deck_id}"
if session_key not in st.session_state or not st.session_state[session_key] or st.button("Reload queue"):
    due_cards = data_store.get_due_cards(cards_df, deck_id=selected_deck_id)
    random.shuffle(due_cards)
    st.session_state[session_key] = [card['id'] for card in due_cards]
    st.session_state.review_idx = 0

queue = st.session_state.get(session_key, [])

if not queue:
    st.success("🎉 No cards are due for review in this deck today!")
    st.stop()

# Main review loop
idx = st.session_state.get("review_idx", 0)
if idx >= len(queue):
    st.success("🎉 You've reviewed all due cards in this deck!")
    st.session_state[session_key] = [] # Clear queue
    st.stop()

card_id = queue[idx]
card_dict = cards_df[cards_df['id'] == card_id].to_dict('records')[0]

# Convert card dict to an object for compatibility with srs.grade_card
class CardObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.box = int(self.box) if self.box else 1
        self.ease = float(self.ease) if self.ease else 2.5
        self.interval_days = int(self.interval_days) if self.interval_days else 1
        self.reps = int(self.reps) if self.reps else 0
        self.lapses = int(self.lapses) if self.lapses else 0

card = CardObject(**card_dict)

st.subheader(f"Card {idx + 1}/{len(queue)}")
direction = st.radio("Direction", ["DE → EN", "EN → DE"], horizontal=True, key="review_direction")
front = card.de if direction == "DE → EN" else card.en
back = card.en if direction == "DE → EN" else card.de

st.markdown(f"**{front}**")

show_answer = st.toggle("Show answer", value=False, key=f"show_ans_review_{card.id}")
if show_answer:
    st.success(back)
    if card.example: st.caption(f"Example: {card.example}")
    if card.notes: st.text(f"Notes: {card.notes}")
    
    grade = ui.grade_buttons()
    if grade > 0:
        grade_card(card, grade, date.today())
        card.due_date = card.due_date.isoformat()
        
        st.session_state.cards_df = data_store.update_card(
            cards_df, card.id, card.__dict__
        )
        data_store.save_data(decks_df, st.session_state.cards_df)
        
        ui.set_toast(f"Next review in {card.interval_days} day(s).")
        st.session_state.review_idx += 1
        st.rerun()
