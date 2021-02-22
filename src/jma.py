import requests


def getQuakeList():
    response = requests.get("https://www.jma.go.jp/bosai/quake/data/list.json")
    if response.status_code != 200:
        return None

    return response.json()


def getQuakeDetails(json_name):
    response = requests.get("https://www.jma.go.jp/bosai/quake/data/{}".format(json_name))
    if response.status_code != 200:
        return None

    return response.json()
