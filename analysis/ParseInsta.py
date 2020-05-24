proxies = open('openproxy.txt').read().split('\n')
ua = open('useragents.txt', 'r').read().split('\n')
import json
import random
from requests import get
from traceback import print_exc
from requests.auth import HTTPProxyAuth
from threading import Thread
from time import sleep
import requests


def generate_ua():
    u = ua[random.randint(0, len(ua) - 1)]

    return u


def prx_convert(proxy_string):
    splitted = proxy_string.split(':')
    return splitted[2] + ':' + splitted[3] + '@' + splitted[0] + ':' + splitted[1]


def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results


def extract_information(user_id, is_id):
    """Get all the information for the given username"""
    uag = generate_ua()
    headers = {
        'User-Agent': uag,
    }
    proxy = random.choice(proxies)
    proxy = proxy.replace('\n', '').replace(" ", "")
    uproxy = {
        'http': 'http://' + proxy,
        'https': 'http://' + proxy
    }
    s = requests.Session()
    s.trust_env = False
    s.proxies = uproxy
    s.auth = HTTPProxyAuth(proxy.split('@')[0].split(":")[0], proxy.split('@')[0].split(":")[1])
    s.headers.update(headers)
    print('setup proxy')

    try:
        if is_id:
            resp = dict(s.get('https://i.instagram.com/api/v1/users/{}/info/'.format(str(user_id))).json())
            username = resp["user"]['username']
        else:
            username = user_id
        profile = dict(s.get('https://www.instagram.com/{}/?__a=1'.format(username), proxies=uproxy).json())['graphql'][
            'user']
        photos = []
        caption = []
        likes = []
        taken_at = ""
        root = profile["edge_owner_to_timeline_media"]["edges"]
        try:
            taken_at = root[0]["node"]["taken_at_timestamp"]
        except:
            pass
        for node in root:
            try:
                photos.append(node["node"]["display_url"])
            except:
                pass
            try:
                caption.append(node["node"]["edge_media_to_caption"]["edges"][0]["node"]["text"])
            except:
                pass
            try:
                likes.append(node["node"]["edge_liked_by"]["count"])
            except:
                pass

        data = {
            'user_id': profile['id'],
            'avatar': profile['profile_pic_url_hd'],
            'full_name': profile["full_name"],
            'media_count': profile["edge_owner_to_timeline_media"]["count"],
            'biography': profile["biography"],
            'follower_count': profile["edge_followed_by"]["count"],
            'following_count': profile["edge_follow"]["count"],
            'username': username,
            'last_post_at': taken_at,
            'photo_urls': photos,
            'caption': caption,
            'likes': likes
        }
        print(proxy, 'succ')
        return data


    except Exception:
        print_exc()
        return None