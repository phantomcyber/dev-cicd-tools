# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import logging


def configure_auth():
    pass


class Connector:
    def main(self):
        # ruleid: logging-sensitive-data
        print(self._secret)
        # ok: logging-sensitive-data
        print("foobar")

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
        logging.info("foobar")

        # ruleid: logging-sensitive-data
        self.debug_print(self._secret)
        # ruleid: logging-sensitive-data
        self.error_print(self._secret)
        # ruleid: logging-sensitive-data
        self.save_progress(self._secret)
        # ruleid: logging-sensitive-data
        self.send_progress(self._secret)
        # ok: logging-sensitive-data
        self.send_progress("foobar")

        self.auth = configure_auth()

        # ruleid: logging-sensitive-data
        self.debug_print(self.auth)

        self.debug_print("password")
