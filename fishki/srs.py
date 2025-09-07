from __future__ import annotations
from datetime import date, timedelta
from typing import Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from fishki.models import Card

Grade = Literal[1,2,3,4]  # Again, Hard, Good, Easy

def clamp(x, lo, hi): 
    return max(lo, min(hi, x))

def next_schedule(ease: float, interval: int, box: int, grade: Grade) -> tuple[float,int,int]:
    if grade == 1:  # Again
        ease = clamp(ease - 0.2, 1.3, 3.0)
        interval = 1
        box = 1
    elif grade == 2:  # Hard
        ease = clamp(ease - 0.15, 1.3, 3.0)
        interval = max(1, round(max(1, interval) * 1.2))
        # box does not advance on 'Hard'
    elif grade == 3:  # Good
        interval = max(1, round(max(1, interval) * ease))
        box = min(5, box + 1)
    else:  # Easy
        ease = clamp(ease + 0.15, 1.3, 3.0)
        interval = round(max(1, interval) * (ease + 0.2))
        box = min(5, box + 1)
    return ease, interval, box

def grade_card(card: "Card", grade: Grade, today: date) -> None:
    prev_box = card.box
    card.ease, card.interval_days, card.box = next_schedule(card.ease or 2.5, card.interval_days or 1, card.box or 1, grade)
    card.due_date = today + timedelta(days=card.interval_days)
    card.reps = (card.reps or 0) + 1
    if grade == 1 and (prev_box or 1) > 1:
        card.lapses = (card.lapses or 0) + 1
