import json
import subprocess
from collections import OrderedDict
from urllib import parse

import requests


class ElasticSearch:
    def __init__(self, env: str):
        """
        Connects to elastic search.
        Args:
            env (str):  environment to connect to, dev, staging, prod
        """
        self.__env = env
        self.__read_only_key = self.__get_read_only_key()

    def query(self, query: str) -> dict:
        """
        Sends a string query to elastic search and returns the result
        """
        query_string = parse.urlencode(OrderedDict(esQuery=query))

        # Elastic search needs IP to be whitelisted, use halter bff service instead so can be used by anyone
        url = f"https://halter-core.{self.__env}.halter.io/v1/bff-debug-tool/device-metrics?{query_string}"

        payload = {}
        headers = {
            'Authorization': 'ReadOnly ' + self.__read_only_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        response_json = json.loads(response.text)

        return response_json

    def __get_read_only_key(self) -> str:
        output = subprocess.run(
            f"aws-vault exec halter-{self.__env} -- aws secretsmanager get-secret-value --secret-id halter/auth/readonly/support",
            shell=True, check=True, capture_output=True).stdout

        secret = json.loads(output)
        read_only_key = secret["SecretString"]
        return read_only_key
