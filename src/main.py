import flet as ft


def build_home() -> ft.Text:
    return ft.Text(
        "Hello, world!",
        size=32,
    )


def main(page: ft.Page) -> None:
    page.title = "Hello Flet"

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    page.add(build_home())


if __name__ == "__main__":
    ft.run(main)