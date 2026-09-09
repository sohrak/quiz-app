from main import build_home


def test_build_home() -> None:
    text = build_home()

    assert text.value == "Hello, world!"
    assert text.size == 32