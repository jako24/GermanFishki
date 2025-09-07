import streamlit as st
from datetime import date, datetime
from fishki import data_store
from fishki.srs import grade_card

st.set_page_config(page_title="Learn New Cards", page_icon="📚", layout="centered")

st.header("📚 Learn New Cards")

# Load data from session state
decks_df = st.session_state.decks_df
cards_df = st.session_state.cards_df

decks = data_store.get_decks(decks_df)
if not decks:
    st.info("You haven't created any decks yet. Go to the 'Decks' page to create one.")
    st.stop()

deck_options = {d['id']: d['name'] for d in decks}
selected_deck_id = st.selectbox(
    "Choose a deck to learn from:",
    options=list(deck_options.keys()),
    format_func=lambda x: deck_options[x]
)

if not selected_deck_id:
    st.stop()

new_cards = data_store.get_new_cards(cards_df, deck_id=selected_deck_id)

if not new_cards:
    st.success("🎉 No new cards left in this deck! Switch to Review or add more cards.")
    st.stop()

# Initialize session state for learning
if "learn_idx" not in st.session_state or st.session_state.get("learn_deck_id") != selected_deck_id:
    st.session_state.learn_idx = 0
    st.session_state.learn_deck_id = selected_deck_id

idx = st.session_state.learn_idx % len(new_cards)
card_dict = new_cards[idx]

# Convert card dict to an object for compatibility with srs.grade_card
class CardObject:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        # Ensure numeric types are correct
        self.box = int(self.box) if self.box else 1
        self.ease = float(self.ease) if self.ease else 2.5
        self.interval_days = int(self.interval_days) if self.interval_days else 1
        self.reps = int(self.reps) if self.reps else 0
        self.lapses = int(self.lapses) if self.lapses else 0

card = CardObject(**card_dict)

direction = st.radio("Direction", ["DE → EN", "EN → DE"], horizontal=True, key="learn_direction")
front = card.de if direction == "DE → EN" else card.en
back = card.en if direction == "DE → EN" else card.de

st.subheader(f"Card {idx + 1}/{len(new_cards)}")
st.markdown(f"**{front}**")

show_answer = st.toggle("Show answer", value=False, key=f"show_ans_{card.id}")
if show_answer:
    st.success(back)
    if card.example: st.caption(f"Example: {card.example}")
    if card.notes: st.text(f"Notes: {card.notes}")

    col1, col2 = st.columns(2)

    def grade_and_advance(grade: int):
        grade_card(card, grade, date.today())
        # Convert due_date back to string for saving
        card.due_date = card.due_date.isoformat()
        
        st.session_state.cards_df = data_store.update_card(
            cards_df, card.id, card.__dict__
        )
        data_store.save_data(decks_df, st.session_state.cards_df)
        st.session_state.learn_idx += 1
        st.rerun()

    if col1.button("❌ I was wrong", use_container_width=True):
        grade_and_advance(1)

    if col2.button("✅ I was right", use_container_width=True):
        grade_and_advance(3)
