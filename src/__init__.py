import logging
import sys

sys.path.append('.')
sys.path.append('./')

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()]
)
