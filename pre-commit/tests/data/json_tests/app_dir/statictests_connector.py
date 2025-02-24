# File: frictionlessconnectors_connector.py
#
# Copyright (c) 2025 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

import json
from typing import Any, Optional

import phantom.app as phantom
import requests
from bs4 import BeautifulSoup
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector
from requests.models import Response

from statictests_consts import (
    CLOUD_HOST,
    GET_HOSTS_ENDPOINT,
    HEADERS,
    NETWORK_OBJECTS_ENDPOINT,
    OBJECT_TYPES,
    STATE_FILE_CORRUPT_ERR,
)


class RetVal(tuple):
    def __new__(cls, val1, val2=None):
        return tuple.__new__(RetVal, (val1, val2))


class FP_Connector(BaseConnector):
    def __init__(self):
        """
        Instance variables
        """
        # Call the BaseConnectors init first
        super().__init__()

        self.firepower_host = ""
        self.headers = HEADERS
        self.default_firepower_domain = None
        self.domains = []

    def _reset_state_file(self) -> None:
        """
        This method resets the state file.
        """
        self.debug_print("Resetting the state file with the default format")
        self._state = {"app_version": self.get_app_json().get("app_version")}
        self.save_state(self._state)

    def initialize(self) -> bool:
        """
        Initializes the global variables and validates them.

        This is an optional function that can be implemented by the
        AppConnector derived class. Since the configuration dictionary
        is already validated by the time this function is called,
        it's a good place to do any extra initialization of any internal
        modules. This function MUST return a value of either
        phantom.APP_SUCCESS or phantom.APP_ERROR.  If this function
        returns phantom.APP_ERROR, then AppConnector::handle_action
        will not get called.
        """
        self._state = self.load_state()
        config = self.get_config()

        if not isinstance(self._state, dict):
            self.debug_print(STATE_FILE_CORRUPT_ERR)
            self._reset_state_file()

        ret_val = self.authenicate_cloud_fmc(config)

        if phantom.is_fail(ret_val):
            return self.get_status()

        return phantom.APP_SUCCESS

    def authenicate_cloud_fmc(self, config: dict[str, Any]) -> bool:
        """
        This method updates the headers and sets the firepower host
        based on the users region when connecting to a cloud FMC.
        """
        region = config["region"]
        api_key = config["api_key"]
        self.firepower_host = CLOUD_HOST.format(region=region.lower())
        self.headers.update({"Authorization": f"Bearer {api_key}"})
        return phantom.APP_SUCCESS

    def _process_empty_response(self, response, action_result) -> RetVal:
        if response.status_code == 200:
            return RetVal(phantom.APP_SUCCESS, {})

        return RetVal(
            action_result.set_status(
                phantom.APP_ERROR, "Empty response and no information in the header"
            ),
            None,
        )

    def _process_html_response(self, response, action_result) -> RetVal:
        # A html response, treat it like an error
        status_code = response.status_code

        try:
            soup = BeautifulSoup(response.text, "html.parser")
            error_text = soup.text
            split_lines = error_text.split("\n")
            split_lines = [x.strip() for x in split_lines if x.strip()]
            error_text = "\n".join(split_lines)
        except Exception as e:
            error_text = f"Cannot parse error detail: {e}"

        message = f"Status Code: {status_code}. Data from server:\n{error_text}\n"

        message = message.replace("{", "{{").replace("}", "}}")
        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_json_response(self, r: Response, action_result: ActionResult) -> RetVal:
        # Try a json parse
        try:
            resp_json = r.json()
        except Exception as e:
            return RetVal(
                action_result.set_status(
                    phantom.APP_ERROR,
                    f"Unable to parse JSON response. Error: {e!s}",
                ),
                None,
            )

        if 200 <= r.status_code < 399:
            return RetVal(phantom.APP_SUCCESS, resp_json)

        # You should process the error returned in the json
        message = "Error from server"

        return RetVal(action_result.set_status(phantom.APP_ERROR, message), None)

    def _process_response(self, r: Response, action_result: ActionResult) -> RetVal:
        # store the r_text in debug data, it will get dumped in the logs if the action fails
        if hasattr(action_result, "add_debug_data"):
            action_result.add_debug_data({"r_status_code": r.status_code})
            action_result.add_debug_data({"r_text": r.text})
            action_result.add_debug_data({"r_headers": r.headers})

        # Process each 'Content-Type' of response separately

        # Process a json response
        if "json" in r.headers.get("Content-Type", ""):
            return self._process_json_response(r, action_result)

        # Process an HTML response, Do this no matter what the api says.
        # There is a high chance of a PROXY in between phantom and the rest of
        # world, in case of errors, PROXY's return HTML, this function parses
        # the error and adds it to the action_result.
        if "html" in r.headers.get("Content-Type", ""):
            return self._process_html_response(r, action_result)

        # it's not content-type that is to be parsed, handle an empty response
        if not r.text:
            return self._process_empty_response(r, action_result)

        # everything else is actually an error at this point
        msg = "Can't process response from server."

        return RetVal(action_result.set_status(phantom.APP_ERROR, msg), None)

    def _make_rest_call(
        self,
        method: str,
        endpoint: str,
        action_result: ActionResult,
        json_body: Optional[dict[str, Any]] = None,
        headers_only: bool = False,
        first_try: bool = True,
        params: Optional[dict[str, Any]] = None,
    ) -> tuple[bool, Any]:
        """Function that makes the REST call to the app.
        :param method: REST method
        :param endpoint: REST endpoint to be called
        :param action_result: object of ActionResult class
        :param json_body: JSON object
        :param headers_only: wether to only return response headers
        :param headers: request headers
        :param first_try: if the request is eligible to be retried
        :param params: request parameters
        :param auth: basic auth if passed in. This is only needed with the generatetoken endpoint
        :return: status phantom.APP_ERROR/phantom.APP_SUCCESS(along with appropriate message),
        response obtained by making an API call
        """
        request_method = getattr(requests, method)
        url = f"https://{self.firepower_host}{endpoint}"
        if json_body:
            self.headers.update({"Content-type": "application/json"})

        try:
            result = request_method(
                url, headers=self.headers, json=json_body, params=params, timeout=10
            )
        except Exception as e:
            return action_result.set_status(
                phantom.APP_ERROR, f"Error connecting to server. {e!s}"
            ), None

        if not (200 <= result.status_code < 399):
            if result.status_code == 401 and first_try:
                self.debug_print(
                    f"Re-running endpoint that failed because of token error {endpoint}"
                )
                return self._make_rest_call(
                    method, endpoint, action_result, json_body, headers_only, first_try=False
                )

            message = "Error from server"
            return action_result.set_status(phantom.APP_ERROR, message), None

        if headers_only:
            return phantom.APP_SUCCESS, result.headers

        return self._process_response(result, action_result)

    def _handle_test_connectivity(self, param: dict[str, Any]) -> bool:
        action_result = ActionResult(dict(param))
        self.add_action_result(action_result)

        self.save_progress("Testing connectivity")

        url = GET_HOSTS_ENDPOINT.format(domain_id="default")
        ret_val, _ = self._make_rest_call("get", url, action_result)
        if phantom.is_fail(ret_val):
            self.save_progress("Connectivity test failed")
            return action_result.get_status()

        self.save_progress("Connectivity test passed")
        return action_result.set_status(phantom.APP_SUCCESS)

    def get_network_objects_of_type(
        self,
        object_type: str,
        domain_uuid: str,
        action_result: ActionResult,
        name: Optional[str] = None,
    ) -> bool:
        """Helper to get network objects of a particular type.
        Args:
            object_type (str): Network object type (Network, Host, Range)
            domain_uuid (str): Domain to be queried
            action_result (ActionResult): object of ActionResult class
            name (str): Name of the object
        Returns:
            bool: If lookup was successfull
        """
        url = NETWORK_OBJECTS_ENDPOINT.format(domain_id=domain_uuid, type=object_type.lower() + "s")

        offset = 0
        limit = 50
        params = {"limit": limit}
        while True:
            params["offset"] = offset
            ret_val, response = self._make_rest_call("get", url, action_result, params=params)
            if phantom.is_fail(ret_val):
                return action_result.get_status()

            try:
                network_obj_list = response.get("items", [])
                for item in network_obj_list:
                    if name and name != item["name"]:
                        continue

                    action_result.add_data(item)

            except Exception as e:
                message = "An error occurred while processing network objects"
                self.debug_print(f"{message}. {e!s}")
                return action_result.set_status(phantom.APP_ERROR, str(e))

            if "paging" in response and "next" in response["paging"]:
                offset += limit
            else:
                break

        return phantom.APP_SUCCESS

    def get_domain_id(self, domain_name: str) -> str:
        """Helper to get a domain_name id.
        Args:
            domain_name (str): Name of domain
        Returns:
            str: domain_id
        """
        domain_name = domain_name or self.default_firepower_domain

        # multitenancy on cloud achieved through seperate tenants not domains
        if not domain_name or self.is_cloud_deployment():
            return "default"

        for domain in self.domains:
            leaf_domain = domain["name"].lower().split("/")[-1]
            if domain_name.lower() == leaf_domain:
                return domain["uuid"]

    def _handle_list_network_objects(self, param: dict[str, Any]) -> bool:
        self.save_progress(f"In action handler for: {self.get_action_identifier()}")

        action_result = self.add_action_result(ActionResult(dict(param)))

        domain_uuid = self.get_domain_id(param.get("domain_name"))
        obj_type = param["type"]
        param.pop("type")
        param.pop("type", None)
        name = param.get("name")

        if obj_type:
            ret_val = self.get_network_objects_of_type(obj_type, domain_uuid, action_result, name)
            if phantom.is_fail(ret_val):
                return action_result.get_status()

        else:
            for object_type in OBJECT_TYPES:
                ret_val = self.get_network_objects_of_type(
                    object_type, domain_uuid, action_result, name
                )
                if phantom.is_fail(ret_val):
                    return action_result.get_status()

        action_result.update_summary({"total_objects_returned": len(action_result.get_data())})
        self.save_progress("test")
        return action_result.set_status(phantom.APP_SUCCESS)

    def handle_action(self, param: dict[str, Any]) -> bool:
        ret_val = phantom.APP_SUCCESS

        # Get the action that we are supposed to execute for this App Run
        action_id = self.get_action_identifier()

        self.debug_print("action_id", self.get_action_identifier())

        if action_id == "test_connectivity":
            ret_val = self._handle_test_connectivity(param)
        elif action_id == "list_network_objects":
            self._handle_list_network_objects(param)

        return ret_val


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("No test json specified as input")
        sys.exit(0)

    # input a json file that contains data like the configuration and action parameters
    with open(sys.argv[1]) as f:
        in_json = f.read()
        in_json = json.loads(in_json)
        print(json.dumps(in_json, indent=4))

        connector = FP_Connector()
        connector.print_progress_message = True
        ret_val = connector._handle_action(json.dumps(in_json), None)
        print(json.dumps(json.loads(ret_val), indent=4))

    sys.exit(0)
