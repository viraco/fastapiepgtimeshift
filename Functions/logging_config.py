import logging
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:     %(name)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)
    logger.info("Logging setup complete")
