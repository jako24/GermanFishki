import streamlit as st
import pandas as pd
from datetime import date, timedelta
from fishki import data_store

st.set_page_config(page_title="Statistics", page_icon="📊", layout="wide")

# Initialize data from CSV files into session state
if 'decks_df' not in st.session_state or 'cards_df' not in st.session_state:
    st.session_state.decks_df, st.session_state.cards_df = data_store.load_data()

st.header("📊 Statistics Dashboard")

# Load data from session state
decks_df = st.session_state.decks_df
cards_df = st.session_state.cards_df

if cards_df.empty:
    st.info("No card data available yet. Add some cards to see stats.")
    st.stop()
    
# --- Data Preparation ---
df = cards_df.copy()
# Convert dates, handling potential errors
df['due_date'] = pd.to_datetime(df['due_date'], errors='coerce').dt.date
df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce').dt.date
today = date.today()

# --- Global Stats ---
st.subheader("Overall Progress")
col1, col2, col3 = st.columns(3)
col1.metric("Total Cards", len(df))
due_today_count = len(df[df['due_date'] == today])
col2.metric("Reviews Due Today", due_today_count)
learned_today_count = len(df[df['created_at'] == today])
col3.metric("Learned Today", learned_today_count)

# --- Per-Deck Stats ---
st.subheader("Deck Breakdown")
deck_names = {d['id']: d['name'] for d in data_store.get_decks(decks_df)}
df['deck_name'] = df['deck_id'].map(deck_names).fillna("Unassigned")

# Ensure 'box' column is numeric
df['box'] = pd.to_numeric(df['box'], errors='coerce').fillna(1).astype(int)

box_counts = df.groupby('deck_name')['box'].value_counts().unstack(fill_value=0)
st.bar_chart(box_counts)

# --- Due Date Heatmap ---
st.subheader("Upcoming Reviews (Next 30 Days)")
future_due_dates_df = df[
    (df['due_date'].notna()) &
    (df['due_date'] >= today) & 
    (df['due_date'] < today + timedelta(days=30))
]

if not future_due_dates_df.empty:
    heatmap_data = future_due_dates_df['due_date'].value_counts().reset_index()
    heatmap_data.columns = ['date', 'count']
    heatmap_data = heatmap_data.sort_values('date')
    st.bar_chart(heatmap_data.set_index('date'))
else:
    st.write("No upcoming reviews in the next 30 days.")
