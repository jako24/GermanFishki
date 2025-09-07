from datetime import date
import pytest

# A simple mock object for a Card
class MockCard:
    def __init__(self, box=1, ease=2.5, interval_days=1, reps=0, lapses=0, due_date=None):
        self.box = box
        self.ease = ease
        self.interval_days = interval_days
        self.reps = reps
        self.lapses = lapses
        self.due_date = due_date

def test_good_increases_interval_and_box():
    from fishki.srs import grade_card
    c = MockCard()
    today = date(2025, 1, 1)
    grade_card(c, 3, today)  # Grade 3 = Good
    assert c.box == 2
    assert c.interval_days > 1
    assert c.reps == 1
    assert c.lapses == 0
    assert c.due_date > today

def test_again_resets_box_and_interval():
    from fishki.srs import grade_card
    c = MockCard(box=3, interval_days=10, reps=5)
    today = date(2025, 1, 1)
    grade_card(c, 1, today) # Grade 1 = Again
    assert c.box == 1
    assert c.interval_days == 1
    assert c.reps == 6
    assert c.lapses == 1
    assert c.due_date == date(2025, 1, 2)

def test_easy_increases_interval_more():
    from fishki.srs import grade_card
    card_good = MockCard()
    card_easy = MockCard()
    today = date(2025, 1, 1)
    
    grade_card(card_good, 3, today) # Good
    grade_card(card_easy, 4, today) # Easy

    assert card_easy.box == card_good.box # Both advance by 1
    assert card_easy.interval_days > card_good.interval_days
    assert card_easy.ease > card_good.ease

def test_hard_increases_interval_less():
    from fishki.srs import grade_card
    card_good = MockCard()
    card_hard = MockCard()
    today = date(2025, 1, 1)

    grade_card(card_good, 3, today) # Good
    grade_card(card_hard, 2, today) # Hard

    assert card_hard.box < card_good.box
    assert card_hard.interval_days < card_good.interval_days
    assert card_hard.ease < card_good.ease
    assert card_hard.box == 1 # Box does not advance on Hard

def test_lapses_counter():
    from fishki.srs import grade_card
    c = MockCard(box=2)
    today = date(2025,1,1)
    grade_card(c, 1, today) # 'Again' on a card that is not new
    assert c.lapses == 1
    grade_card(c, 1, today) # 'Again' on a card that is now in box 1
    assert c.lapses == 1 # Should not increment again
