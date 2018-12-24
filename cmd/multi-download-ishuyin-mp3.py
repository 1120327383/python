import requests
import json
from bs4 import BeautifulSoup

s = requests.Session()
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Host": "www.ishuyin.com",
    "Referer": "https://www.ishuyin.com/show-19248.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
}


def parse(url):
    ret = s.get(url=url, headers=headers)
    soup = BeautifulSoup(ret.content, "html.parser")
    d = soup.select("#urlDown")[0]
    h = d.attrs["href"].split("*")
    r = "".join([chr(int(x)) for x in h if x != ""])
    return r


def download(link, index):
    ss = requests.Session()
    ret = ss.get(link)
    with open("mp3/{}.mp3".format(index), 'wb') as file:
        file.write(ret.content)


if __name__ == '__main__':
    for i in range(1, 123):
        url = "https://www.ishuyin.com/player.php?mov_id=19248&look_id={}&player=down".format(i)
        link = parse(url)
        download(link, i)
        print(u"第{}集下载完成".format(i))
