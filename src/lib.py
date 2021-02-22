import requests
import json
import src
import os
import tweepy

module_path = src.__path__


def send_to_discord(token, channelId, message, embed=None, files=None):
    if files is None:
        files = {}
    headers = {
        "Authorization": "Bot {token}".format(token=token),
        "User-Agent": "Bot"
    }
    params = {
        "payload_json": json.dumps({
            "content": message,
            "embed": embed
        })
    }
    response = requests.post(
        "https://discord.com/api/channels/{channelId}/messages".format(channelId=channelId), headers=headers,
        data=params, files=files)
    print(response.status_code)
    print(response.json())


def send_to_discord_webhook(webhook_url, message, embed=None, files=None):
    if files is None:
        files = {}
    headers = {
        "Content-Type": "multipart/form-data"
    }
    params = {
        "payload_json": json.dumps({
            "content": message,
            "embed": embed
        })
    }
    response = requests.post(
        webhook_url, headers=headers,
        data=params, files=files)
    print(response.status_code)
    print(response.json())


def send_to_twitter(consumer_key, consumer_secret, access_token, access_token_secret, message, file=None,
                    reply_to=None):
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    if file is not None:
        img = api.media_upload(filename="output.png", file=file)
        tweet = api.update_status(status=message, media_ids=[img.media_id], in_reply_to_status_id=reply_to)
    else:
        tweet = api.update_status(status=message, in_reply_to_status_id=reply_to)
    return tweet


def get_settings(config, service, notify_type, setting_name):
    """
    個別設定内に設定があればそれを返し、なければグローバル設定を返します。

    :param config: コンフィグデータ
    :param service: discord or twitter
    :param notify_type: early, jma or nhk
    :param setting_name: enable, channel or webhook_url
    :return: 設定内容。存在しなければNone
    """
    if notify_type in config[service] and setting_name in config[service][notify_type]:
        return config[service][notify_type][setting_name]

    if setting_name not in config[service]:
        return None

    return config[service][setting_name]


def is_checked(name, data_id):
    checked_path = os.path.join(module_path, name + ".json")
    if not os.path.exists(checked_path):
        return False
    with open(checked_path, "r") as f:
        checked = json.load(f)

    return data_id in checked


def add_checked(name, data_id):
    checked_path = os.path.join(module_path, name + ".json")
    checked = []
    if os.path.exists(checked_path):
        with open(checked_path, "r") as f:
            checked = json.load(f)

    checked.append(data_id)

    with open(checked_path, "w") as f:
        f.write(json.dumps(checked))


def is_init(name):
    checked_path = os.path.join(module_path, name + ".json")
    return not os.path.exists(checked_path)
