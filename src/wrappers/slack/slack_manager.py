

class SlackManager:

    # Public:
    def __init__(self) -> None:
        self.__connect()

    def send_message(self, payload: dict) -> None:
        try:
            # Call the conversations.list method using the WebClient
            result = client.chat_postMessage(
                channel=channel_id,
                text="Hello world!"
                # You could also use a blocks[] array to send richer content
            )
            # Print result, which includes information about the message (like TS)
            print(result)

        except SlackApiError as e:
            print(f"Error: {e}")

    # Private:
