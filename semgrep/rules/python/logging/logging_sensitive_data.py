import logging


class Connector:
    def main(self):
        # ruleid: logging-sensitive-data
        print(self._secret)
        # ok: logging-sensitive-data
        print('foobar')

        # ruleid: logging-sensitive-data
        logging.debug(self._secret)
        # ruleid: logging-sensitive-data
        logging.info(self._secret)
        # ruleid: logging-sensitive-data
        logging.warning(self._secret)
        # ruleid: logging-sensitive-data
        logging.error(self._secret)
        # ruleid: logging-sensitive-data
        logging.critical(self._secret)
        # ruleid: logging-sensitive-data
        logging.fatal(self._secret)
        # ruleid: logging-sensitive-data
        logging.exception(self._secret)
        # ruleid: logging-sensitive-data
        logging.log(logging.INFO, self._secret)
        # ok: logging-sensitive-data
        logging.info('foobar')

        # ruleid: logging-sensitive-data
        self.debug_print(self._secret)
        # ruleid: logging-sensitive-data
        self.error_print(self._secret)
        # ruleid: logging-sensitive-data
        self.save_progress(self._secret)
        # ruleid: logging-sensitive-data
        self.send_progress(self._secret)
        # ok: logging-sensitive-data
        self.send_progress('foobar')



