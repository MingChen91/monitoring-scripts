#!/usr/bin/env python3

from elasticsearch import ElasticSearch

#
#
# def format_datetime_to_str(d: datetime) -> str:
#     return d.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]  # Remove last 3 digits
#
#
# def format_time_stamp(days_from_now=0, hours_from_now=0) -> str:
#     finish = datetime.now(timezone.utc)
#     # finish = datetime.timestamp()
#     d = timedelta(days=days_from_now, hours=hours_from_now)
#     offset = timedelta(days=3)
#     start = finish - d
#     formatted = f"timestamp:[{format_datetime_to_str(start - offset)} TO {format_datetime_to_str(finish - offset)}] AND "
#     return formatted
#
#
# def collars_checked_into_wifi_last_day():
#     timestamp = format_time_stamp(days_from_now=1)
#     print(timestamp)
#     query = f'{timestamp}serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "WIFI_CHECKIN"'
#     return query_elastic_search(query)
#
#
# def collars_checked_into_lora_last_hour():
#     timestamp = format_time_stamp(hours_from_now=1)
#     query = f'{timestamp}serialNumber:004\-00\* AND context.farmId:"4ef316f1-4628-4457-9468-1a294d1e7769" AND _exists_:context.cattleId AND "LORA_CHECKIN"'
#     return query_elastic_search(query)


if __name__ == "__main__":
    prod_es = ElasticSearch("dev")
    result = prod_es.query('es_query = serialNumber:"002-0012-00028" AND metricName:OTA_EVENT ')
    print(result)

    # list_wifi_collars = set()
    # wifi_collars = collars_checked_into_wifi_last_day()
    # for wifi_collar in wifi_collars:
    #     list_wifi_collars.add(wifi_collar['data']['serialNumber'])
    #
    # list_lora_collars = set()
    # lora_collars = collars_checked_into_lora_last_hour()
    # for lora_collar in lora_collars:
    #     list_lora_collars.add(lora_collar['data']['serialNumber'])
    #
    # filtered_set = list_lora_collars - list_wifi_collars
    # print(filtered_set)
