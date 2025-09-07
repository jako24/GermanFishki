import streamlit as st
import random
import time
import pandas as pd
from fishki import data_store, utils, audio

st.set_page_config(page_title="Quiz Yourself", page_icon="📝", layout="centered")

# Initialize data from CSV files into session state
if 'decks_df' not in st.session_state or 'cards_df' not in st.session_state:
    st.session_state.decks_df, st.session_state.cards_df = data_store.load_data()

st.header("📝 Quiz Yourself")

# Load data from session state
decks_df = st.session_state.decks_df
cards_df = st.session_state.cards_df

# Deck selection
decks = data_store.get_decks(decks_df)
if not decks:
    st.info("No decks available. Please create a deck first.")
    st.stop()

deck_options = {d['id']: d['name'] for d in decks}
selected_deck_id = st.selectbox(
    "Choose a deck to quiz on:",
    options=list(deck_options.keys()),
    format_func=lambda x: deck_options.get(x, "N/A")
)

if not selected_deck_id:
    st.stop()

# --- Quiz Logic ---
def setup_quiz():
    cards = data_store.get_cards(cards_df, deck_id=selected_deck_id)
    if len(cards) < 4:
        st.warning("Not enough cards in this deck for a quiz (minimum 4 needed).")
        st.session_state.quiz_cards = []
    else:
        st.session_state.quiz_cards = random.sample(cards, k=len(cards))
    st.session_state.quiz_idx = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answer_submitted = None

if 'quiz_cards' not in st.session_state or st.session_state.get('quiz_deck_id') != selected_deck_id:
    setup_quiz()
    st.session_state.quiz_deck_id = selected_deck_id

idx = st.session_state.get('quiz_idx', 0)
if not st.session_state.quiz_cards:
    st.stop()

if idx >= len(st.session_state.quiz_cards):
    st.success(f"🎉 Quiz Complete! Your score: {st.session_state.quiz_score}/{len(st.session_state.quiz_cards)}")
    if st.button("Restart Quiz"):
        setup_quiz()
        st.rerun()
    st.stop()

card = st.session_state.quiz_cards[idx]
direction = st.radio("Direction", ["DE → EN", "EN → DE"], horizontal=True, key="quiz_direction")
question = card['de'] if direction == "DE → EN" else card['en']
correct_answer = card['en'] if direction == "DE → EN" else card['de']

# --- Quiz UI ---
def show_result(was_correct):
    if was_correct: st.success("Correct!")
    else: st.error(f"Incorrect. The correct answer is: **{correct_answer}**")
    
    time.sleep(1)
    st.session_state.quiz_idx += 1
    st.session_state.quiz_answer_submitted = None
    st.rerun()

typing_tab, mcq_tab = st.tabs(["Typing Test", "Multiple Choice"])

with typing_tab:
    st.subheader(f"Question {idx+1}: What is the translation of '{question}'?")
    if audio.is_tts_available() and st.button("🔊 Play Audio"):
        audio.speak(card['de'])
    
    with st.form("typing_quiz"):
        user_answer = st.text_input("Your answer:", key=f"typing_answer_{card['id']}")
        threshold = st.slider("Fuzzy Match Threshold", 50, 100, 85)
        if st.form_submit_button("Submit"):
            is_correct = utils.fuzzy_match(user_answer, correct_answer, threshold)
            if is_correct: st.session_state.quiz_score += 1
            st.session_state.quiz_answer_submitted = True
            st.session_state.last_was_correct = is_correct

    if st.session_state.quiz_answer_submitted:
        show_result(st.session_state.last_was_correct)

with mcq_tab:
    st.subheader(f"Question {idx+1}: Select the correct translation for '{question}'")
    # A simple mock Card object for the MCQ generator
    class MockCard:
        def __init__(self, **kwargs): self.__dict__.update(kwargs)
    
    # We need to adapt the get_mcq_options to work with DataFrames
    all_cards_in_deck = data_store.get_cards(cards_df, selected_deck_id)
    potential_distractors = [c for c in all_cards_in_deck if c['id'] != card['id']]
    
    if len(potential_distractors) >= 3:
        distractors = random.sample(potential_distractors, k=3)
        options = [d['en'] for d in distractors] + [correct_answer]
        random.shuffle(options)
    else:
        options = [c['en'] for c in potential_distractors] + [correct_answer]
        random.shuffle(options)

    for option in options:
        if st.button(option, key=f"mcq_{card['id']}_{option}", use_container_width=True):
            is_correct = (option == correct_answer)
            if is_correct: st.session_state.quiz_score += 1
            show_result(is_correct)
