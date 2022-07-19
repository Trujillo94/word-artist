from src.utils.toolbox import load_env_var


class SlackWordArtistUserMessages:

    loading_text: str = 'Generating a fabulous WordArt...'
    loading_img_url: str = 'https://media0.giphy.com/media/XXH77SsudU3HW/giphy.gif?cid=790b76113f7e1b9f0e6117c95a1a3bbdde66fa6948828e6b&rid=giphy.gif&ct=g'
    error_text = 'Oops! Something went wrong.'
    error_img_url = 'https://media3.giphy.com/media/YDj8Ot6mIbJYs/giphy.gif?cid=ecf05e47fn4ptkyy52ocl3a3h305wyjawoa82snb48ad47br&rid=giphy.gif&ct=g'

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
                                    "text": "Okay",
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
        if load_env_var('ENV') == 'dev':
            text = str(e)
            msg['blocks'].append({
                "type": "section",
                "text": {
                        "type": "mrkdwn",
                        "text": text
                }
            })
        return msg
