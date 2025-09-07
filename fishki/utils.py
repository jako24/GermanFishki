from __future__ import annotations

import random
from typing import List, TYPE_CHECKING

from rapidfuzz import fuzz

if TYPE_CHECKING:
    from sqlmodel import Session
    from .models import Card
    from . import repo

def normalize_text(text: str) -> str:
    """Lowercase and remove leading/trailing whitespace."""
    return (text or "").lower().strip()


def fuzzy_match(s1: str, s2: str, threshold: int = 85) -> bool:
    """Check if two strings are similar enough based on a fuzzy ratio."""
    return fuzz.ratio(normalize_text(s1), normalize_text(s2)) >= threshold


def get_mcq_options(
    session: Session,
    correct_card: "Card",
    deck_id: int,
    distractors: int = 3,
) -> List[str]:
    """Generate multiple-choice options with one correct answer and N distractors."""
    # Get other cards from the same deck to use as distractors
    all_cards_in_deck = repo.list_cards(session, deck_id)
    
    # Filter out the correct card
    potential_distractors = [
        card for card in all_cards_in_deck if card.id != correct_card.id
    ]

    # Not enough cards for distractors, just return the correct one
    if len(potential_distractors) < distractors:
        return [correct_card.en]

    # Randomly select N distractors
    selected_distractors = random.sample(potential_distractors, k=distractors)
    
    # Combine correct answer with distractors and shuffle
    options = [d.en for d in selected_distractors] + [correct_card.en]
    random.shuffle(options)
    
    return options
