import datetime
import io

import requests
from PIL import Image


def get_kyosin_data():
    checktime = datetime.datetime.now()

    response = None
    for i in range(10):
        checktime = (checktime - datetime.timedelta(seconds=i))
        url = "http://www.kmoni.bosai.go.jp/webservice/hypo/eew/{}.json".format(checktime.strftime("%Y%m%d%H%M%S"))
        response = requests.get(url)
        if response.status_code == 200:
            break

    if response is None or response.status_code != 200:
        return None

    return {
        "time": checktime,
        "data": response.json()
    }


def get_realtime_surface_jma_img(checktime):
    """
    リアルタイム震度地図 (地表)

    :return:
    """
    base_url = "http://www.kmoni.bosai.go.jp/data/map_img"

    img = Image.open("img/base_map_w.png").convert("RGBA")

    # 地表
    jma_s_img_url = "{base_url}/RealTimeImg/jma_s/{ymd}/{time}.jma_s.gif".format(
        base_url=base_url,
        ymd=checktime.strftime("%Y%m%d"),
        time=checktime.strftime("%Y%m%d%H%M%S")
    )
    jma_s_response = requests.get(jma_s_img_url)

    if jma_s_response.status_code != 200:
        return None

    img = img_alpha_paste(img, Image.open(io.BytesIO(jma_s_response.content)).convert("RGBA"))

    # 震度表示図
    shindo_img_url = "{base_url}/EstShindoImg/eew/{ymd}/{time}.eew.gif".format(
        base_url=base_url,
        ymd=checktime.strftime("%Y%m%d"),
        time=checktime.strftime("%Y%m%d%H%M%S")
    )

    shindo_response = requests.get(shindo_img_url)
    if shindo_response.status_code == 200:
        img = img_alpha_paste(img, Image.open(io.BytesIO(shindo_response.content)).convert("RGBA"))

    # P/S波表示図
    wave_img_url = "{base_url}/PSWaveImg/eew/{ymd}/{time}.eew.gif".format(
        base_url=base_url,
        ymd=checktime.strftime("%Y%m%d"),
        time=checktime.strftime("%Y%m%d%H%M%S")
    )

    wave_response = requests.get(wave_img_url)
    if wave_response.status_code == 200:
        img = img_alpha_paste(img, Image.open(io.BytesIO(wave_response.content)).convert("RGBA"))

    jma_scale_img = Image.open("img/nied_jma_s_w_scale.gif").convert("RGBA")
    img = img_alpha_paste(img, jma_scale_img, (305, 99))

    # img.save("test.png", quality=95)
    return img


def get_realtime_under_jma_img(checktime):
    """
    リアルタイム震度地図 (地中)

    :return:
    """
    base_url = "http://www.kmoni.bosai.go.jp/data/map_img"

    img = Image.open("img/base_map_w.png").convert("RGBA")

    # 地中
    jma_b_img_url = "{base_url}/RealTimeImg/jma_b/{ymd}/{time}.jma_b.gif".format(
        base_url=base_url,
        ymd=checktime.strftime("%Y%m%d"),
        time=checktime.strftime("%Y%m%d%H%M%S")
    )
    jma_b_response = requests.get(jma_b_img_url)

    if jma_b_response.status_code != 200:
        return None

    img = img_alpha_paste(img, Image.open(io.BytesIO(jma_b_response.content)).convert("RGBA"))

    # P/S波表示図
    wave_img_url = "{base_url}/PSWaveImg/eew/{ymd}/{time}.eew.gif".format(
        base_url=base_url,
        ymd=checktime.strftime("%Y%m%d"),
        time=checktime.strftime("%Y%m%d%H%M%S")
    )

    wave_response = requests.get(wave_img_url)
    if wave_response.status_code == 200:
        img = img_alpha_paste(img, Image.open(io.BytesIO(wave_response.content)).convert("RGBA"))

    jma_scale_img = Image.open("img/nied_jma_s_w_scale.gif").convert("RGBA")
    img = img_alpha_paste(img, jma_scale_img, (305, 99))

    # img.save("test.png", quality=95)
    return img


def img_alpha_paste(base_img, paste_img, box=(0, 0)):
    img = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    img.paste(paste_img, box)
    return Image.alpha_composite(base_img, img)
