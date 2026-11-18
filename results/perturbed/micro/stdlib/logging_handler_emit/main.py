import logging

class q92bb_0(logging.Handler):
    def q92bb_1(self, record):
        record.getMessage()

logger = logging.getLogger("bench")
logger.addHandler(q92bb_0())
logger.warning("hello")
