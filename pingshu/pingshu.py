import re
import os
import time
import urllib.parse

from lxml import etree
from requests.exceptions import ConnectionError
import requests

RESOURCE_PATH = 'resources/'
BASE_URL = 'http://mp3.5ips.net/pingshu/'

headers = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Mobile Safari/537.36',
    'Accept-Encoding': 'gzip, deflate'
}


def refresh_token() -> str:
    """
    刷新mp3文件访问token。经测试，token只有时限，不关联cookie，没有文件特异性
    :return:
    """
    url = 'http://www.5ips.net/down_20_001.htm'
    token = None

    while not token:
        resp = requests.get(url, headers=headers)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)

        script_html = html.xpath("//script[contains(text(), 'url[3]')]")
        if len(script_html) > 0:
            script_text = script_html[0].text
            token = re.search('url\[3.*".*key=(.*)"', script_text).group(1)
        time.sleep(5)

    return token


def download(title, left=1) -> tuple:
    start_time = time.time()
    aim_dir_path = os.path.join(RESOURCE_PATH, title)
    if not os.path.exists(aim_dir_path):
        os.makedirs(aim_dir_path)

    url = urllib.parse.urljoin(BASE_URL, title)
    status = True
    num = left

    try:
        resp = requests.get(url, headers=headers)
        resp.encoding = resp.apparent_encoding
        html = etree.HTML(resp.text)
        hrefs = html.xpath('//a/@href')
        if len(hrefs) == 0:
            raise ConnectionError
        hrefs = sorted(hrefs[left:])
        print(f'* 共计 {len(hrefs)} 段')

        token = None
        for i, href in enumerate(hrefs):
            time.sleep(5)
            num = i + left
            item_url = urllib.parse.urljoin(BASE_URL, href)
            if i % 10 == 0:
                token = refresh_token()
                print(f'* 更新 token: {token}')

            resp = requests.get(item_url, headers=headers, params={'key': token})

            file_name = urllib.parse.unquote(href).split('/')[-1]
            file_path = os.path.join(aim_dir_path, file_name)
            with open(file_path, 'wb') as wf:
                wf.write(resp.content)

            print('* {} 已下载完成'.format(file_name))
    except ConnectionError:
        status = False
    except Exception as e:
        raise e
    return status, num


def main():
    print('********************** Pingshu Downloader **********************')
    print(f'* 目录地址：{BASE_URL}')
    title = input('* 请输入评书标题：')
    left = input('* 请输入起始编号(默认为1)：') or 1
    left = int(left)
    is_completed = False
    while not is_completed:
        print(f'* 开始下载评书 <{title}>，从第 {left} 段开始...')
        is_completed, left = download(title, left)
        if not is_completed:
            print('* 链接中断，正在重启...')
    print(f'* <{title}> 下载完成')


if __name__ == '__main__':
    main()