import logging as logger

from phantom import BaseConnector as Base


class Connector(Base):
    def __init__(self):
        # ruleid: soar-standard-logging
        print("foobar")
        # ruleid: soar-standard-logging
        logger.info("foobar")
        # ruleid: soar-standard-logging
        logger.getLogger().info("foobar")

        # ok: soar-standard-logging
        self.debug_print("foobar")
        # ok: soar-standard-logging
        self.save_progress("foobar")
