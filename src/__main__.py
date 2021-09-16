import datetime
import io
import json
import re
import time

import schedule as schedule
from PIL import Image

from src import jma, kmoni, lib, nhk


def kmoni_watcher():
    init = lib.is_init("kmoni")
    with open("config.json") as f:
        config = json.load(f)

    is_discord_enable = lib.get_settings(config, "discord", "early", "enable")
    is_twitter_enable = lib.get_settings(config, "twitter", "early", "enable")
    print("kmoni_watcher(): ", is_discord_enable, is_twitter_enable)
    if not is_discord_enable and not is_twitter_enable:
        return

    data = kmoni.get_kyosin_data()
    if "alertflg" not in data["data"]:
        return  # 新規データなし

    print("[{alertflg}] {region_name} - 震度{calcintensity}, 深さ{depth}, マグニチュード{magunitude}M".format(
        alertflg=data["data"]["alertflg"],
        region_name=data["data"]["region_name"],
        calcintensity=data["data"]["calcintensity"],
        depth=data["data"]["depth"],
        magunitude=data["data"]["magunitude"]
    ))

    # レポートIDと震度、最終判定で新規判定。震度が変わったら通知
    check_id = data["data"]["report_id"] + "_" + data["data"]["calcintensity"] + "_" + str(data["data"]["is_final"])
    print("check_id:", check_id)

    if data["data"]["calcintensity"] != "不明" and int(data["data"]["calcintensity"][0]) < 4:  # 震度4未満
        return
    print("DEBUG: intensity >= 4")

    if data["data"]["calcintensity"] == "不明" and float(data["data"]["magunitude"]) < 5:  # 震度不明の場合マグニチュード5以上
        return
    print("DEBUG: OR mag >= 5")

    if lib.is_checked("kmoni", check_id):
        return
    print("Not checked")

    checktime = data["time"]
    img_output = io.BytesIO()
    surface_img = kmoni.get_realtime_surface_jma_img(checktime)
    under_img = kmoni.get_realtime_under_jma_img(checktime)
    while surface_img is None or under_img is None:
        time.sleep(0.5)
        if surface_img is None:
            surface_img = kmoni.get_realtime_surface_jma_img(checktime)
        if under_img is None:
            under_img = kmoni.get_realtime_under_jma_img(checktime)
    print("Got image")

    img = Image.new("RGBA", (surface_img.size[0] + under_img.size[0], surface_img.size[1]), (255, 255, 255, 0))
    img.paste(surface_img, (0, 0))
    img.paste(under_img, (surface_img.size[0] + 1, 0))

    img.save(img_output, format='png')
    print("Generated image")

    files = {
        "file": ("output.png", img_output.getvalue())
    }

    embed = {
        "title": "地震情報（" + ("最終報" if data["data"]["is_final"] else "速報") + "）",
        "description": "強震モニタによる地震速報をお知らせします。\n機能製作者(Tomachi)は、この機能に起因するあらゆる損害について一切の責任を負いません。",
        "url": "http://www.kmoni.bosai.go.jp/",
        "timestamp": datetime.datetime.now().isoformat(),
        "color": 0xff0000,
        "fields": [
            {
                "name": "震央地名",
                "value": "`{}`".format(data["data"]["region_name"]),
                "inline": True
            },
            {
                "name": "最大予測震度",
                "value": "震度{}程度".format(data["data"]["calcintensity"]),
                "inline": True
            },
            {
                "name": "マグニチュード",
                "value": "{}M".format(data["data"]["magunitude"]),
                "inline": True
            },
            {
                "name": "深さ",
                "value": data["data"]["depth"],
                "inline": True
            },
            {
                "name": "ステータス",
                "value": data["data"]["alertflg"],
                "inline": False
            },
            {
                "name": "発表日時",
                "value": data["data"]["report_time"],
                "inline": False
            },
            {
                "name": "最終報判定フラグ",
                "value": str(data["data"]["is_final"]),
                "inline": False
            },
            {
                "name": "デバッグ用データ",
                "value": "```\n識別ID: {}\n配信番号: {}\n```".format(
                    data["data"]["report_id"],
                    data["data"]["report_num"]
                ),
                "inline": False
            }
        ],
        "image": {
            "url": "attachment://output.png"
        }
    }

    if not init:
        print("Not init")
        token = lib.get_settings(config, "discord", "early", "token")
        channel = lib.get_settings(config, "discord", "early", "channel")
        webhook_url = lib.get_settings(config, "discord", "early", "webhook_url")

        if is_discord_enable:
            if token is not None and channel is not None:
                print("Sending discord(channel)")
                lib.send_to_discord(token, channel, "", embed, files)
            elif webhook_url is not None:
                print("Sending discord(webhook)")
                lib.send_to_discord_webhook(webhook_url, "", embed, files)

        if is_twitter_enable:
            print("Sending twitter")
            consumer_key = lib.get_settings(config, "twitter", "early", "consumer_key")
            consumer_secret = lib.get_settings(config, "twitter", "early", "consumer_secret")
            access_token = lib.get_settings(config, "twitter", "early", "access_token")
            access_token_secret = lib.get_settings(config, "twitter", "early", "access_token_secret")
            message = "【地震情報】{region_name} {calcintensity}\n深さ: {depth}\nマグニチュード: {magunitude}M\nステータス: {status}".format(
                region_name=data["data"]["region_name"],
                calcintensity=data["data"]["calcintensity"],
                depth=data["data"]["depth"],
                magunitude=data["data"]["magunitude"],
                status=data["data"]["alertflg"]
            )
            lib.send_to_twitter(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret,
                message,
                img_output
            )

    print("Add checked")
    lib.add_checked("kmoni", check_id)
    print("Added checked")


def jma_watcher():
    init = lib.is_init("jma")
    with open("config.json") as f:
        config = json.load(f)

    is_discord_enable = lib.get_settings(config, "discord", "jma", "enable")
    is_twitter_enable = lib.get_settings(config, "twitter", "jma", "enable")
    print("jma_watcher(): ", is_discord_enable, is_twitter_enable)
    if not is_discord_enable and not is_twitter_enable:
        return

    message_template = "地震情報（震源・震度情報）\n" \
                       "{DATETIME} {PUBLISH}発表\n" \
                       "\n" \
                       "{HEADLINE}\n" \
                       "震源地は、{HYPOCENTER}で、震源の深さは約{DEPTH}、地震の規模（マグニチュード）は{MAGNITUDE}と推定されます。\n" \
                       "\n" \
                       "{FORECAST_COMMENT}" \
                       "\n" \
                       "この地震により観測された最大震度は震度{MaxInt}です。\n" \
                       "\n" \
                       "震度{MaxInt}	{MaxIntLocations}"

    items = jma.getQuakeList()
    for item in items:
        eid = item["eid"]
        print(eid)
        message = message_template

        if item["en_ttl"] != "Earthquake and Seismic Intensity Information":
            continue  # 震源・震度情報ではない

        if int(item["maxi"][0]) < 4:  # 震度4未満
            continue

        if lib.is_checked("jma", eid):
            continue

        lib.add_checked("jma", eid)

        json_name = item["json"]
        details = jma.getQuakeDetails(json_name)
        _datetime = datetime.datetime.fromisoformat(details["Control"]["DateTime"].replace("Z", "+09:00"))
        publish = details["Control"]["PublishingOffice"]

        headline = details["Head"]["Headline"]["Text"]
        hypocenter = details["Body"]["Earthquake"]["Hypocenter"]["Area"]["Name"]
        coords = details["Body"]["Earthquake"]["Hypocenter"]["Area"]["Coordinate"]
        coords = re.search(r"\+([0-9.]+)\+([0-9.]+)-([0-9]+)/", coords).groups()
        depth = int(int(coords[2]) / 1000)
        magnitude = details["Body"]["Earthquake"]["Magnitude"]
        maxInt = details["Head"]["Headline"]["Information"][0]["Item"][0]["Kind"]["Name"]
        maxIntLocations = details["Head"]["Headline"]["Information"][0]["Item"][0]["Areas"]["Area"]
        if isinstance(maxIntLocations, list):
            maxIntLocations = list(map(lambda x: x["Name"], maxIntLocations))
        else:
            maxIntLocations = [maxIntLocations["Name"]]

        forecastComment = details["Body"]["Comments"]["ForecastComment"]["Text"]

        message = message.format(
            DATETIME=_datetime.strftime("%Y/%m/%d %H:%M:%S"),
            PUBLISH=publish,
            HEADLINE=headline,
            HYPOCENTER=hypocenter,
            DEPTH=depth,
            MAGNITUDE=magnitude,
            FORECAST_COMMENT=forecastComment,
            MaxInt=maxInt,
            MaxIntLocations=" ".join(maxIntLocations)
        )
        print(message)

        embed = {
            "title": "気象庁 地震情報",
            "description": "気象庁による地震情報をお伝えします。\n機能製作者(Tomachi)は、この機能に起因するあらゆる損害について一切の責任を負いません。",
            "url": "https://www.jma.go.jp/bosai/",
            "timestamp": datetime.datetime.now().isoformat(),
            "color": 0xffff00,
            "fields": [
                {
                    "name": "情報",
                    "value": "```\n{}\n```".format(message),
                    "inline": True
                },
            ]
        }

        token = lib.get_settings(config, "discord", "jma", "token")
        channel = lib.get_settings(config, "discord", "jma", "channel")
        webhook_url = lib.get_settings(config, "discord", "jma", "webhook_url")

        if is_discord_enable:
            if token is not None and channel is not None:
                lib.send_to_discord(token, channel, "", embed)
            elif webhook_url is not None:
                lib.send_to_discord_webhook(webhook_url, "", embed)

        if is_twitter_enable:
            consumer_key = lib.get_settings(config, "twitter", "jma", "consumer_key")
            consumer_secret = lib.get_settings(config, "twitter", "jma", "consumer_secret")
            access_token = lib.get_settings(config, "twitter", "jma", "access_token")
            access_token_secret = lib.get_settings(config, "twitter", "jma", "access_token_secret")
            lib.send_to_twitter(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret,
                "【気象庁地震情報】" + message
            )


def nhk_watcher():
    init = lib.is_init("nhk")
    with open("config.json") as f:
        config = json.load(f)

    is_discord_enable = lib.get_settings(config, "discord", "nhk", "enable")
    is_twitter_enable = lib.get_settings(config, "twitter", "nhk", "enable")
    print("nhk_watcher(): ", is_discord_enable, is_twitter_enable)
    if not is_discord_enable and not is_twitter_enable:
        return

    items = nhk.getJishinReport()
    for item in items:
        jid = item["jid"]
        date_time = item["datetime"]
        shindo = item["shindo"]
        url = item["url"]

        if int(item["shindo"][0]) < 4:  # 震度4未満
            return

        if lib.is_checked("nhk", jid):
            return

        lib.add_checked("nhk", jid)
        if init:
            return

        details = nhk.getJishinReportDetails(url)

        embed = {
            "title": "NHK 地震情報",
            "description": "NHKによる地震情報をお伝えします。\n機能製作者(Tomachi)は、この機能に起因するあらゆる損害について一切の責任を負いません。",
            "url": "https://www.nhk.or.jp/kishou-saigai/earthquake/",
            "timestamp": date_time.isoformat(),
            "color": 0xffa500,
            "fields": [
                {
                    "name": "震源地",
                    "value": details["earthquake"]["epicenter"],
                    "inline": True
                },
                {
                    "name": "最大震度",
                    "value": "震度{}".format(shindo),
                    "inline": True
                },
                {
                    "name": "深さ",
                    "value": details["earthquake"]["depth"],
                    "inline": True
                },
                {
                    "name": "規模（マグニチュード）",
                    "value": details["earthquake"]["magnitude"],
                    "inline": True
                }
            ],
            "image": {
                "url": "https://www3.nhk.or.jp/sokuho/jishin/{}".format(details["image"]["detail"])
            }
        }

        token = lib.get_settings(config, "discord", "nhk", "token")
        channel = lib.get_settings(config, "discord", "nhk", "channel")
        webhook_url = lib.get_settings(config, "discord", "nhk", "webhook_url")

        if is_discord_enable:
            if token is not None and channel is not None:
                lib.send_to_discord(token, channel, "", embed)
            elif webhook_url is not None:
                lib.send_to_discord_webhook(webhook_url, "", embed)

        if is_twitter_enable:
            consumer_key = lib.get_settings(config, "twitter", "nhk", "consumer_key")
            consumer_secret = lib.get_settings(config, "twitter", "nhk", "consumer_secret")
            access_token = lib.get_settings(config, "twitter", "nhk", "access_token")
            access_token_secret = lib.get_settings(config, "twitter", "nhk", "access_token_secret")
            message = "【NHK地震情報】\n" \
                      "震源地: {}\n" \
                      "深さ: {}" \
                      "規模（マグニチュード）: {}".format(
                            details["earthquake"]["epicenter"],
                            details["earthquake"]["depth"],
                            details["earthquake"]["magnitude"]
                        )
            lib.send_to_twitter(
                consumer_key,
                consumer_secret,
                access_token,
                access_token_secret,
                message
            )


if __name__ == "__main__":
    schedule.every(2).seconds.do(kmoni_watcher)  # 強震モニタは2秒毎チェック
    schedule.every(5).minutes.do(jma_watcher)  # 気象庁は5分毎チェック
    schedule.every(5).minutes.do(nhk_watcher)  # NHKは5分毎チェック

    while True:
        schedule.run_pending()
        time.sleep(1)
