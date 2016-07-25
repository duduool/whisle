# coding: utf-8
import io
import json
import redis
from random import choice

import PIL.Image
from PIL import ImageTk
from urllib2 import urlopen

redis_con = redis.StrictRedis(host='192.168.50.202', port=6379, db=1)

CONTENTS = [
    "赤壁矶头，一番过、一番怀古。",
    "想当时，周郎年少，气吞区宇。",
    "万骑临江貔虎噪，千艘列炬鱼龙怒。",
    "卷长波、一鼓困曹瞒，今如许？",
    "江上渡，江边路。",
    "形胜地，兴亡处。",
    "览遗踪，胜读史书言语。",
    "几度东风吹世换，千年往事随潮去。",
    "问道傍、杨柳为谁春，摇金缕。",
]

ZQ_STATUS = {
    "0": "未开始",
    "1": "上半场",
    "2": "中场休息",
    "3": "下半场",
    "4": "完场",
    "5": "取消",
    "6": "改期",
    "7": "腰斩",
    "8": "中断",
    "9": "待定",
    "10": "加时赛开始",
    "11": "加时结束",
    "12": "点球开始",
    "13": "点球结束"
}

def make_thumb(im):
    """生成缩略图"""
    width, height = im.size
    size = 30
    # 裁剪图片成正方形
    if width > height:
        delta = (width - height) / 2
        box = (delta, 0, delta+height, height)
        region = im.crop(box)
    elif height > width:
        delta = (height - width) / 2
        box = (0, delta, width, delta+width)
        region = im.crop(box)
    else:
        region = im

    thumb = region.resize((size, size), PIL.Image.ANTIALIAS)
    thumb = circle(thumb)
    return thumb


def circle(ima):
    size = ima.size
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        ima = ima.resize((r2, r2), PIL.Image.ANTIALIAS)
    imb = PIL.Image.new('RGBA', (r2, r2), (255,255,255,0))
    pima = ima.load()
    pimb = imb.load()
    r = float(r2/2) # 圆心横坐标
    for i in range(r2):
        for j in range(r2):
            lx = abs(i-r+0.5)  # 到圆心距离的横坐标
            ly = abs(j-r+0.5)  # 到圆心距离的纵坐标
            l  = pow(lx, 2) + pow(ly, 2)
            if l <= pow(r, 2):
                pimb[i, j] = pima[i, j]
    return imb


def get_tk_image(url, resize=(400, 150), iscircle=False):
    url = url or "http://img.m.500.com/esun/avatar/20/a8/20a86cceeeea11e4adac.jpg"
    image_bytes = urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = PIL.Image.open(data_stream)
    pil_image = pil_image.resize(resize)
    if iscircle:
        pil_image = circle(pil_image)
    tk_image = ImageTk.PhotoImage(pil_image)
    return tk_image

def get_user_photo(url):
    url = url or "http://img.m.500.com/esun/avatar/20/a8/20a86cceeeea11e4adac.jpg"
    image_bytes = urlopen(url).read()
    data_stream = io.BytesIO(image_bytes)
    pil_image = PIL.Image.open(data_stream)
    pil_image = make_thumb(pil_image)
    tk_image = ImageTk.PhotoImage(pil_image)
    return tk_image


def get_comment_list(fid):
    url = "http://ews.500.com/sns/score/commentlist?vtype=1&fid=%s" % fid
    data = urlopen(url, timeout=10).read()
    items = json.loads(data).get("data", {}).get("commentlist", [])
    infos = [{
        "date":     item.get("date"),
        "photo":    get_user_photo(item.get("photo", {}).get("fullsize")),
        "username": item.get("nickname"),
        "content":  item.get("content", choice(CONTENTS))
    } for item in items]
    return infos

def get_record_list(fid):
    pams = json.loads(redis_con.get("TOUCH_CACHE_PAMS"))
    pams = pams.get(fid, {})
    TOUCH_ZQ_HISTROY = "touch_score:zq:history_data:{}_{}_{}_{}_{}_{}"
    hid = pams.get("hid")
    aid = pams.get("aid")
    matchdate = pams.get("matchdate")
    stid = pams.get("stid")
    data = redis_con.get(TOUCH_ZQ_HISTROY.format(hid, matchdate, stid, "-1", "0", "10"))
    if not data: return []
    items = json.loads(data)
    if not items: return []
    infos = [{
        "simpleleague": item.get("simplegbname"),
        "homesxname": item.get("homesxname"),
        "awaysxname": item.get("awaysxname"),
        "matchdate": item.get("matchdate"),
        "result": item.get("result1"),
        "score": "%s:%s" % (item.get("homescore"), item.get("awayscore"))
    } for item in items.get("matches")]
    return infos

def get_match_list(expect=""):
    url = "http://ews.500.com/score/zq/info?expect=%s" % expect
    import time
    t1 = time.time()
    data = urlopen(url, timeout=10).read()
    items = json.loads(data).get("data", {}).get("matches", [])
    t2 = time.time()
    print t2 - t1

    infos = [{
        "fid": item.get("fid"),
        "order": item.get("order"),
        "status": item.get("status"),
        "matchtime": item.get("matchtime"),
        "status_desc": item.get("status_desc"),
        "simpleleague": item.get("simpleleague"),
        "homesxname": item.get("homesxname"),
        "awaysxname": item.get("awaysxname"),
        "homescore": item.get("homescore") if item.get("status") in ["1", "2", "3", "4", "10", "11", "12", "13"] else "",
        "awayscore": item.get("awayscore") if item.get("status") in ["1", "2", "3", "4", "10", "11", "12", "13"] else "",
        "homelogo": get_tk_image(item.get("homelogo"), resize=(40, 40), iscircle=True),
        "awaylogo": get_tk_image(item.get("awaylogo"), resize=(40, 40), iscircle=True),
    } for item in items]
    return infos
