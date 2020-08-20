import requests
import sys
import re
import json
import csv


def getData(username, proxies):
    r = requests.get(f'https://www.instagram.com/{username}/', proxies=proxies)
    data = re.search(r'window._sharedData = (\{.+?});</script>', r.text).group(1)
    data = json.loads(data)

    return data['entry_data']['ProfilePage'][0]['graphql']['user']



if __name__=="__main__":
    if len(sys.argv)<2:
        print("Usage : python testGetData.py <username> <options optional)>")
        sys.exit()

    with open('proxies.csv', 'r') as f:
        data = csv.reader(f)
        for i in data:
            if i[0]==('proxy' or 'IP'):
                continue
            if 'socks' in i[2].lower():
                continue
            proxies = {
                "http": "http://{}:{}".format(i[0], i[1]),
                "https": "http://{}:{}".format(i[0], i[1]),
            }
            try:
                data = getData(sys.argv[1], proxies)
                # print(json.dumps(data))
                print("proxy {} PASS".format(proxies))
            except:
                print("proxy {} FAILED".format(proxies))
'''
    if len(sys.argv)>2:
        for i in sys.argv[2:]:
            print(f"\n\n{i} - {data[i]}")
'''
