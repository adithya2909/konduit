# utils/logger.py
import logging
def get_logger(name="rag"):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    return logging.getLogger(name)
