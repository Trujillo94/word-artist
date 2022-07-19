from src.utils.toolbox import load_env_var


class SlackWordArtistUserMessages:

    loading_text: str = 'Generating a fabulous WordArt...'
    loading_img_url: str = 'https://media2.giphy.com/media/RHEqKwRZDwFKE/giphy.gif?cid=ecf05e478xqsyjskmocp8bbw1b43olpd4j070sge6gzkl75y&rid=giphy.gif&ct=g'
    error_text: str = 'Oops! Something went wrong.'
    error_img_url: str = 'https://media3.giphy.com/media/YDj8Ot6mIbJYs/giphy.gif?cid=ecf05e47fn4ptkyy52ocl3a3h305wyjawoa82snb48ad47br&rid=giphy.gif&ct=g'

    def generate_loading_message(self) -> dict:
        text = self.loading_text
        img_url = self.loading_img_url
        msg = {
            "blocks": [
                {
                    "type": "image",
                    "alt_text": text,
                    "image_url": img_url
                }
            ]
        }
        return msg

    def generate_error_message(self, e: Exception) -> dict:
        msg = {
            "blocks": [
                {
                    "type": "image",
                    "alt_text": self.error_text,
                    "image_url": self.error_img_url
                },
                {
                    "type": "actions",
                    "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Close",
                                    "emoji": True
                                },
                                "value": "cancel",
                                "action_id": "cancel"
                            }
                    ]
                }
            ],
            "status": "error",
        }
        env = load_env_var('ENV')
        if env is not None and env.lower() == 'dev':
            text = str(e)
            msg['blocks'].append({
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": text
                }
            })
        return msg
