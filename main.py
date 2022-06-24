import logging

from src.word_artist.slack_word_artist import SlackWordArtist

logger = logging.getLogger("main")


def handler(event, context):
    logger.info(f'event: {event}')
    logger.info(f'context: {context}')
    text = event['text']
    style = event.get('style', None)
    img_url = SlackWordArtist().compute(text, style=style)
    logger.info("Successful execution")
    return img_url


if __name__ == "__main__":
    event = {
        "text": "Hello World"
    }
    "token=I2qr45qIMQ9Hce8swoGrUbCc&team_id=T03HZL7AGSF&team_domain=slackappsdeve-kb84670&channel_id=C03HZLDDFPD&channel_name=development-of-slack-apps&user_id=U03HWRB6U5B&user_name=trujillo.oriol&command=%2Fwordart&text=onewordonly&api_app_id=A03J268R2S0&is_enterprise_install=false&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT03HZL7AGSF%2F3712406858244%2FcXesp5cUf08PBqZret1FNCQo&trigger_id=3695402847383.3611687356899.6bb73995435ff94f853519e2df070ca9"
    "token=I2qr45qIMQ9Hce8swoGrUbCc&team_id=T03HZL7AGSF&team_domain=slackappsdeve-kb84670&channel_id=C03HZLDDFPD&channel_name=development-of-slack-apps&user_id=U03HWRB6U5B&user_name=trujillo.oriol&command=%2Fwordart&text=two+fcking+words&api_app_id=A03J268R2S0&is_enterprise_install=false&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT03HZL7AGSF%2F3703541738070%2Fm6Y15hDp5g2T1nXTT6Igi1jD&trigger_id=3695548331959.3611687356899.47cc2468376cb7c6ef8de4e525c43cc2"
    response = handler(event, {})
    print(response)
