import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import requests
import re
import datetime


def get_jishin_report():
    response = requests.get("https://www3.nhk.or.jp/sokuho/jishin/data/JishinReport.xml")
    if response.status_code != 200:
        return None
    response.encoding = "shift-jis"

    result = []

    root = ET.fromstring(response.text)
    for record in root:
        date = record.attrib["date"]
        match = re.search(r"^([0-9]{4})年([0-9]{2})月([0-9]{2})日$", date)
        dates = {
            "year": match.group(1),
            "month": match.group(2),
            "day": match.group(3),
        }
        for item in record:
            time = item.attrib["time"]
            match = re.search(r"^([0-9]{2})時([0-9]{2})分ごろ$", time)
            times = {
                "hour": match.group(1),
                "minute": match.group(2),
            }
            shindo = item.attrib["shindo"]
            url = item.attrib["url"]
            jid = re.search(r".+/([A-Za-z0-9_]+)\.xml$", url).group(1)

            dt = datetime.datetime(
                year=int(dates["year"]),
                month=int(dates["month"]),
                day=int(dates["day"]),
                hour=int(times["hour"]),
                minute=int(times["minute"]),
                second=0
            )
            result.append({
                "jid": jid,  # jishin id
                "datetime": dt,
                "shindo": shindo,
                "url": url
            })

    return result


def get_jishin_report_details(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    response.encoding = "shift-jis"

    result = {
        "timestamp": "",
        "earthquake": {
            "eid": "",
            "time": "",
            "intensity": "",
            "epicenter": "",
            "latitude": "",
            "longitude": "",
            "magnitude": "",
            "depth": "",
            "image": {
                "detail": "",
                "local": "",
                "global": ""
            },
            "relative": []
        }
    }
    root: Element = ET.fromstring(response.text)

    result["timestamp"] = root.find("Timestamp").text
    for (key, value) in root.find("Earthquake").attrib.items():
        if key == "Id":
            key = "eid"
        result["earthquake"][key.lower()] = value

    result["earthquake"]["image"]["detail"] = \
        "https://www3.nhk.or.jp/sokuho/jishin/{}".format(root.find("Earthquake").find("Detail").text)
    result["earthquake"]["image"]["local"] = \
        "https://www3.nhk.or.jp/sokuho/jishin/{}".format(root.find("Earthquake").find("Local").text)
    result["earthquake"]["image"]["global"] = \
        "https://www3.nhk.or.jp/sokuho/jishin/{}".format(root.find("Earthquake").find("Global").text)

    for group in root.find("Earthquake").find("Relative"):
        areas = []
        for area in group:
            areas.append(area.attrib["Name"])

        result["earthquake"]["relative"].append({
            "intensity": group.attrib["Intensity"],
            "area": areas
        })

    return result
