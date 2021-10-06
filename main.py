#!/usr/bin/env python3
import json
import subprocess
from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from urllib import parse

import requests

# global
env = "prod"


def get_read_only_key() -> str:
    output = subprocess.run(
        f"aws-vault exec halter-{env} -- aws secretsmanager get-secret-value --secret-id halter/auth/readonly/support",
        shell=True, check=True, capture_output=True).stdout

    secret = json.loads(output)
    read_only_key = secret["SecretString"]
    return read_only_key


def query_elastic_search(query: str) -> str:
    read_only_key = get_read_only_key()

    query_string = parse.urlencode(OrderedDict(esQuery=query))

    url = f"https://halter-core.{env}.halter.io/v1/bff-debug-tool/device-metrics?{query_string}"

    payload = {}
    headers = {
        'Authorization': 'ReadOnly ' + read_only_key
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    response_json = json.loads(response.text)

    # for response in response_json["items"]:
    #     print(response)

    return response_json["items"]


def format_datetime_to_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Remove last 3 digits


def get_last_day_timestamp() -> str:
    finish = datetime.now(timezone.utc)
    d = timedelta(days=1)
    start = finish - d
    formatted = f"timestamp:[{format_datetime_to_str(start)} TO {format_datetime_to_str(finish)}]"
    return formatted


def build_query_string(q: str) -> str:
    """Searches for the past 2 days"""
    return f"{get_last_day_timestamp()} AND {q}"


def collars_checked_into_wifi():
    raw_query = 'serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "WIFI_CHECKIN"'
    query = build_query_string(raw_query)
    return query_elastic_search(query)


def collars_checked_into_lora():
    raw_query = 'serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "LORA_CHECKIN"'
    query = build_query_string(raw_query)
    return query_elastic_search(query)


if __name__ == "__main__":
    # es_query = f"serialNumber:004\-00\* AND metricName:OTA_EVENT "
    # es_query = f"timestamp:[2021-10-04T00:00:00.000 TO 2021-10-04T23:59:59.000] AND serialNumber:004\-00\* AND metricName:OTA_EVENT "

    list_wifi_collars = set()
    wifi_collars = collars_checked_into_wifi()
    for wifi_collar in wifi_collars:
        list_wifi_collars.add(wifi_collar['data']['serialNumber'])

    list_lora_collars = set()
    lora_collars = collars_checked_into_lora()
    for lora_collar in lora_collars:
        list_lora_collars.add(lora_collar['data']['serialNumber'])

    filtered_set = list_lora_collars - list_wifi_collars
    print(filtered_set)
