from main import Deck, FlashCard, FlashCardSession, PlaceholderDeckStorage


def test_placeholder_storage_has_the_three_starter_cards() -> None:
    storage = PlaceholderDeckStorage()

    assert len(storage.decks) == 1
    deck = storage.decks[0]
    assert deck.name == "Starter Deck"
    assert deck.cards == [
        FlashCard("Card 1", "First card in the deck"),
        FlashCard("Card 2", "Second card in the deck"),
        FlashCard("Card 3", "Third card in the deck"),
    ]


def test_flash_card_session_flips_and_advances_through_a_deck() -> None:
    deck = Deck("Test", [FlashCard("Front", "Back"), FlashCard("Next", "Answer")])
    session = FlashCardSession(deck)
    first_card = session.current_card

    assert session.showing_front
    assert session.current_text == first_card.front

    session.flip()
    assert session.current_text == first_card.back

    session.next_card()
    assert session.showing_front
    assert session.current_text == session.current_card.front
    assert session.current_card != first_card


def test_flash_card_session_restarts_after_the_last_card() -> None:
    deck = Deck("Test", [FlashCard("Only front", "Only back")])
    session = FlashCardSession(deck)
    session.flip()

    session.next_card()

    assert session.index == 0
    assert session.showing_front
    assert session.current_text == "Only front"