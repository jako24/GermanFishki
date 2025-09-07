from __future__ import annotations
import pandas as pd
import os
from datetime import date, datetime
from typing import TypedDict, List
import streamlit as st
import uuid

DATA_DIR = "data"
DECKS_FILE = os.path.join(DATA_DIR, "decks.csv")
CARDS_FILE = os.path.join(DATA_DIR, "cards.csv")

class Card(TypedDict):
    id: str
    deck_id: str
    de: str
    en: str
    example: str
    tags: str
    notes: str
    box: int
    ease: float
    interval_days: int
    reps: int
    lapses: int
    due_date: str
    created_at: str
    updated_at: str

class Deck(TypedDict):
    id: str
    name: str
    description: str
    created_at: str

def _ensure_data_files_exist():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DECKS_FILE):
        pd.DataFrame(columns=["id", "name", "description", "created_at"]).to_csv(
            DECKS_FILE, index=False
        )
    if not os.path.exists(CARDS_FILE):
        pd.DataFrame(columns=list(Card.__annotations__.keys())).to_csv(
            CARDS_FILE, index=False
        )

@st.cache_data(ttl=10) # Short TTL to allow for re-reading after changes
def load_data():
    _ensure_data_files_exist()
    decks_df = pd.read_csv(DECKS_FILE)
    cards_df = pd.read_csv(CARDS_FILE)
    return decks_df, cards_df

def save_data(decks_df: pd.DataFrame, cards_df: pd.DataFrame):
    decks_df.to_csv(DECKS_FILE, index=False)
    cards_df.to_csv(CARDS_FILE, index=False)
    st.cache_data.clear()

def get_decks(decks_df: pd.DataFrame) -> List[Deck]:
    return decks_df.to_dict('records')

def get_cards(cards_df: pd.DataFrame, deck_id: str | None = None) -> List[Card]:
    if deck_id:
        return cards_df[cards_df["deck_id"] == deck_id].to_dict('records')
    return cards_df.to_dict('records')

def add_deck(decks_df: pd.DataFrame, name: str, description: str) -> pd.DataFrame:
    new_deck = {
        "id": str(uuid.uuid4()),
        "name": name,
        "description": description,
        "created_at": datetime.utcnow().isoformat()
    }
    return pd.concat([decks_df, pd.DataFrame([new_deck])], ignore_index=True)

def add_card(cards_df: pd.DataFrame, card_data: dict) -> pd.DataFrame:
    new_card = {
        "id": str(uuid.uuid4()),
        "deck_id": card_data["deck_id"],
        "de": card_data["de"],
        "en": card_data["en"],
        "example": card_data.get("example", ""),
        "tags": card_data.get("tags", ""),
        "notes": card_data.get("notes", ""),
        "box": 1,
        "ease": 2.5,
        "interval_days": 1,
        "reps": 0,
        "lapses": 0,
        "due_date": date.today().isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    return pd.concat([cards_df, pd.DataFrame([new_card])], ignore_index=True)

def update_card(cards_df: pd.DataFrame, card_id: str, updates: dict) -> pd.DataFrame:
    idx = cards_df.index[cards_df['id'] == card_id]
    if not idx.empty:
        for key, value in updates.items():
            cards_df.loc[idx, key] = value
        cards_df.loc[idx, 'updated_at'] = datetime.utcnow().isoformat()
    return cards_df

def delete_deck(decks_df: pd.DataFrame, cards_df: pd.DataFrame, deck_id: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    decks_df = decks_df[decks_df["id"] != deck_id]
    cards_df = cards_df[cards_df["deck_id"] != deck_id]
    return decks_df, cards_df

def delete_card(cards_df: pd.DataFrame, card_id: str) -> pd.DataFrame:
    return cards_df[cards_df["id"] != card_id]

def get_due_cards(cards_df: pd.DataFrame, deck_id: str) -> List[Card]:
    today_str = date.today().isoformat()
    due_df = cards_df[(cards_df["deck_id"] == deck_id) & (cards_df["due_date"] <= today_str)]
    return due_df.to_dict('records')

def get_new_cards(cards_df: pd.DataFrame, deck_id: str) -> List[Card]:
    new_df = cards_df[(cards_df["deck_id"] == deck_id) & (cards_df["reps"] == 0)]
    return new_df.to_dict('records')
