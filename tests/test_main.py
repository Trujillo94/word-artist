from main import handler


def test_main():
    event = {
        "text": "Hello World",
        "style": None
    }
    handler(event, {})


if __name__ == "__main__":
    test_main()
