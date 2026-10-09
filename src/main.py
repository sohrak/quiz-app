import random
from dataclasses import dataclass, field

import flet as ft


@dataclass(frozen=True)
class FlashCard:
    front: str
    back: str


@dataclass
class Deck:
    name: str
    cards: list[FlashCard] = field(default_factory=list)


class PlaceholderDeckStorage:
    def __init__(self) -> None:
        self.decks = [
            Deck(
                "Starter Deck",
                [
                    FlashCard("Card 1", "First card in the deck"),
                    FlashCard("Card 2", "Second card in the deck"),
                    FlashCard("Card 3", "Third card in the deck"),
                ],
            )
        ]

    def add_deck(self, deck: Deck) -> None:
        self.decks.append(deck)

    def delete_deck(self, deck: Deck) -> None:
        self.decks.remove(deck)


class FlashCardSession:
    def __init__(self, deck: Deck) -> None:
        self.deck_name = deck.name
        self.cards = deck.cards.copy()
        random.shuffle(self.cards)
        self.index = 0
        self.showing_front = True

    @property
    def current_card(self) -> FlashCard:
        return self.cards[self.index]

    @property
    def current_text(self) -> str:
        if self.showing_front:
            return self.current_card.front
        return self.current_card.back

    def flip(self) -> None:
        self.showing_front = not self.showing_front

    def next_card(self) -> None:
        if self.index == len(self.cards) - 1:
            random.shuffle(self.cards)
            self.index = 0
        else:
            self.index += 1
        self.showing_front = True


class QuizApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.is_ios = page.platform == ft.PagePlatform.IOS
        self.storage = PlaceholderDeckStorage()
        self.session: FlashCardSession | None = None

    def action_button(
        self,
        text: str,
        icon: ft.IconData,
        on_click,
        *,
        filled: bool = True,
    ) -> ft.Control:
        if self.is_ios:
            button = ft.CupertinoFilledButton if filled else ft.CupertinoButton
            return button(content=text, icon=icon, on_click=on_click)
        if filled:
            return ft.FilledButton(text, icon=icon, on_click=on_click)
        return ft.OutlinedButton(text, icon=icon, on_click=on_click)

    def text_field(
        self,
        label: str,
        *,
        autofocus: bool = False,
    ) -> ft.CupertinoTextField | ft.TextField:
        if self.is_ios:
            return ft.CupertinoTextField(
                placeholder_text=label,
                autofocus=autofocus,
                padding=12,
            )
        return ft.TextField(label=label, autofocus=autofocus)

    def show(self, content: ft.Control) -> None:
        self.page.clean()
        self.page.add(content)
        self.page.update()

    def show_home(self) -> None:
        self.session = None
        self.show(self.build_home())

    def build_home(self) -> ft.Control:
        deck_list = ft.ListView(expand=True, spacing=10)
        deck_list.controls.extend(self.build_deck_row(deck) for deck in self.storage.decks)
        header_controls: list[ft.Control] = [
            ft.Text(
                "Study",
                size=34 if self.is_ios else 32,
                weight=ft.FontWeight.BOLD,
            ),
            self.action_button("New deck", ft.Icons.ADD, self.open_create_deck),
        ]
        home_controls: list[ft.Control] = [
            ft.Row(
                controls=header_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Text(
                f"{len(self.storage.decks)} decks ready to study",
                color="#667085",
            ),
            ft.Divider(height=20),
            deck_list,
        ]

        return ft.Container(
            content=ft.Column(
                controls=home_controls,
                expand=True,
                spacing=12,
            ),
            padding=24,
            expand=True,
        )

    def build_deck_row(self, deck: Deck) -> ft.Control:
        delete_button = (
            ft.CupertinoButton(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip="Delete deck",
                icon_color="#B42318",
                visible=False,
                on_click=lambda _: self.delete_deck(deck),
            )
            if self.is_ios
            else ft.IconButton(
                icon=ft.Icons.DELETE_OUTLINE,
                tooltip="Delete deck",
                icon_color="#B42318",
                visible=False,
                on_click=lambda _: self.delete_deck(deck),
            )
        )

        row = ft.GestureDetector(
            on_tap=lambda _: self.open_deck(deck),
            content=ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.STYLE,
                                color="#007AFF" if self.is_ios else "#147D72",
                            ),
                            bgcolor="#E5F1FF" if self.is_ios else "#E3F3EF",
                            padding=12,
                            border_radius=8,
                        ),
                        ft.Column(
                            controls=[
                                ft.Text(deck.name, weight=ft.FontWeight.BOLD),
                                ft.Text(
                                    f"{len(deck.cards)} cards",
                                    size=13,
                                    color="#667085",
                                ),
                            ],
                            spacing=4,
                            expand=True,
                        ),
                        delete_button,
                        ft.Icon(ft.Icons.CHEVRON_RIGHT, color="#667085"),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=12,
                bgcolor="#FFFFFF",
                border=ft.Border.all(0.5 if self.is_ios else 1, "#D1D1D6" if self.is_ios else "#E4E7EC"),
                border_radius=10 if self.is_ios else 8,
            ),
        )

        return ft.Dismissible(
            key=deck.name,
            content=row,
            background=ft.Container(
                content=ft.Row(
                    controls=[ft.Icon(ft.Icons.DELETE_OUTLINE), ft.Text("Delete")],
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                bgcolor="#FEE4E2",
                padding=16,
                border_radius=8,
            ),
            on_dismiss=lambda _: self.delete_deck(deck),
        )

    def open_create_deck(self) -> None:
        name_field = self.text_field("Deck name", autofocus=True)
        front_field = self.text_field("First card front")
        back_field = self.text_field("First card back")
        error_text = ft.Text(color="#B42318", visible=False)

        def create() -> None:
            name = name_field.value.strip()
            front = front_field.value.strip()
            back = back_field.value.strip()
            if not name or not front or not back:
                error_text.value = "Enter a name and both sides of the first card."
                error_text.visible = True
                self.page.update()
                return
            if any(deck.name.casefold() == name.casefold() for deck in self.storage.decks):
                error_text.value = "A deck with that name already exists."
                error_text.visible = True
                self.page.update()
                return

            self.storage.add_deck(Deck(name, [FlashCard(front, back)]))
            self.page.pop_dialog()
            self.show_home()

        dialog_actions: list[ft.Control] = [
            (
                ft.CupertinoButton(
                    content="Cancel",
                    on_click=lambda: self.page.pop_dialog(),
                )
                if self.is_ios
                else ft.TextButton("Cancel", on_click=lambda: self.page.pop_dialog())
            ),
            (
                ft.CupertinoButton(content="Create", on_click=create)
                if self.is_ios
                else ft.FilledButton("Create", on_click=create)
            ),
        ]
        dialog_content = ft.Column(
            controls=[name_field, front_field, back_field, error_text],
            tight=True,
            spacing=12,
        )
        if self.is_ios:
            dialog = ft.CupertinoAlertDialog(
                modal=True,
                title=ft.Text("Create a deck"),
                content=dialog_content,
                actions=dialog_actions,
            )
        else:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Create a deck"),
                content=dialog_content,
                actions=dialog_actions,
                actions_alignment=ft.MainAxisAlignment.END,
            )
        self.page.show_dialog(dialog)

    def delete_deck(self, deck: Deck) -> None:
        self.storage.delete_deck(deck)
        self.show_home()

    def open_deck(self, deck: Deck) -> None:
        if not deck.cards:
            return
        self.session = FlashCardSession(deck)
        self.show_quiz()

    def show_quiz(self) -> None:
        session = self.session
        if session is None:
            return

        card_text = ft.Text(
            session.current_text,
            size=30,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER,
        )
        progress = ft.Text(
            f"{session.index + 1} of {len(session.cards)}",
            color="#667085",
        )

        def flip() -> None:
            session.flip()
            card_text.value = session.current_text
            self.page.update()

        def next_card() -> None:
            session.next_card()
            card_text.value = session.current_text
            progress.value = f"{session.index + 1} of {len(session.cards)}"
            self.page.update()

        study_controls: list[ft.Control] = [
            self.action_button("Flip", ft.Icons.FLIP, flip, filled=False),
            progress,
            self.action_button("Next", ft.Icons.ARROW_FORWARD, next_card),
        ]
        quiz_controls: list[ft.Control] = [
            ft.Row(
                controls=[
                    (
                        ft.CupertinoButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Back to decks",
                            on_click=lambda: self.show_home(),
                        )
                        if self.is_ios
                        else ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Back to decks",
                            on_click=lambda: self.show_home(),
                        )
                    ),
                    ft.Text(self.session_title(session), weight=ft.FontWeight.BOLD),
                    ft.Container(expand=True),
                ],
            ),
            ft.Container(
                content=ft.Column(
                    controls=[card_text],
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    spacing=20,
                ),
                bgcolor="#FFFFFF",
                border=ft.Border.all(0.5 if self.is_ios else 1, "#D1D1D6" if self.is_ios else "#E4E7EC"),
                border_radius=14 if self.is_ios else 12,
                padding=32,
                expand=True,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Row(
                controls=study_controls,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        ]

        self.show(
            ft.Container(
                content=ft.Column(
                    controls=quiz_controls,
                    expand=True,
                    spacing=16,
                ),
                padding=20,
                expand=True,
            )
        )

    def session_title(self, session: FlashCardSession) -> str:
        return session.deck_name


def main(page: ft.Page) -> None:
    is_ios = page.platform == ft.PagePlatform.IOS
    page.title = "Study"
    page.bgcolor = "#F2F2F7" if is_ios else "#F7F8F6"
    page.padding = 0
    page.theme = ft.Theme(color_scheme_seed="#007AFF" if is_ios else "#147D72")
    QuizApp(page).show_home()


if __name__ == "__main__":
    ft.run(main)