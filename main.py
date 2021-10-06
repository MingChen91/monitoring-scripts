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


def format_time_stamp(days_from_now=0, hours_from_now=0) -> str:
    finish = datetime.now(timezone.utc)
    # finish = datetime.timestamp()
    d = timedelta(days=days_from_now, hours=hours_from_now)
    offset = timedelta(days=3)
    start = finish - d
    formatted = f"timestamp:[{format_datetime_to_str(start - offset)} TO {format_datetime_to_str(finish - offset)}] AND "
    return formatted


def collars_checked_into_wifi_last_day():
    timestamp = format_time_stamp(days_from_now=1)
    print(timestamp)
    query = f'{timestamp}serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "WIFI_CHECKIN"'
    return query_elastic_search(query)


def collars_checked_into_lora_last_hour():
    timestamp = format_time_stamp(hours_from_now=1)
    query = f'{timestamp}serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "LORA_CHECKIN"'
    return query_elastic_search(query)


if __name__ == "__main__":
    list_wifi_collars = set()
    wifi_collars = collars_checked_into_wifi_last_day()
    for wifi_collar in wifi_collars:
        list_wifi_collars.add(wifi_collar['data']['serialNumber'])

    list_lora_collars = set()
    lora_collars = collars_checked_into_lora_last_hour()
    for lora_collar in lora_collars:
        list_lora_collars.add(lora_collar['data']['serialNumber'])

    filtered_set = list_lora_collars - list_wifi_collars
    print(filtered_set)
