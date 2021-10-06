import json
import subprocess
from collections import OrderedDict
from urllib import parse

import requests


class ElasticSearch:
    def __init__(self, env: str):
        self.__env = env
        self.__read_only_key = self.__get_read_only_key()
        pass

    def __get_read_only_key(self) -> str:
        output = subprocess.run(
            f"aws-vault exec halter-{self.__env} -- aws secretsmanager get-secret-value --secret-id halter/auth/readonly/support",
            shell=True, check=True, capture_output=True).stdout

        secret = json.loads(output)
        read_only_key = secret["SecretString"]
        return read_only_key

    def query(self, query: str) -> str:
        query_string = parse.urlencode(OrderedDict(esQuery=query))

        url = f"https://halter-core.{self.__env}.halter.io/v1/bff-debug-tool/device-metrics?{query_string}"

        payload = {}
        headers = {
            'Authorization': 'ReadOnly ' + self.__read_only_key
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        response_json = json.loads(response.text)

        # for response in response_json["items"]:
        #     print(response)

        return response_json
