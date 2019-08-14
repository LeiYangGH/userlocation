# coding: utf-8
import pickle

import requests, re, time
from bs4 import BeautifulSoup
from random import randint

import os
from requests.adapters import HTTPAdapter
from usercity import extract_user_city

request_retry = HTTPAdapter(max_retries=2)  # 增加重连次


def get_lon_lat(user, search_loc):
    # 模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    session = requests.Session()
    session.mount('https://', request_retry)
    session.mount('http://', request_retry)
    session.keep_alive = False  # 关闭多余连接
    session.headers.update(headers)

    # 生成url接口,并获取内容
    url = "https://www.geonames.org/search.html?q=%s&country=" % search_loc
    try:  # 记录超时连接
        html = session.get(url, timeout=30)
    except:
        print("Timeout")
        fd_wrong_loc.write((user + "\t" + search_loc + "\r\n").encode('utf-8'))
        return False
    print("Html.code: %s" % html.status_code)
    if html.status_code == 200 and html.text:
        # print(html.text)
        soup = BeautifulSoup(html.text, 'lxml')
        table = soup.find('table', class_='restable')  # <class 'bs4.element.Tag'>
        if not table:
            palce_warn = soup.find('div', id='search')  # place 不存在,警告
            print("[!] No place: We have found no places with the name '%s'" % search_loc.encode('utf-8'))
            fd_wrong_loc.write((user + "\t" + search_loc + "\r\n").encode('utf-8'))
        else:
            red_warn = soup.find('font', color="red")  # 表格不存在，记录红色字体警告
            if red_warn:
                print("[!] No record: ", red_warn.find("small").text)
                fd_wrong_loc.write((user + "\t" + search_loc + "\r\n").encode('utf-8'))
            else:
                trs = table.find_all("tr")
                first_record = trs[2]  # 提取第一个城市
                tds = first_record.find_all("td")
                loc_name = tds[1].find("a").text if tds[1].a else "error"
                loc_latitude = tds[1].find("span", class_="latitude").text if tds[1].find("span",
                                                                                          class_="latitude") else "error"
                loc_longitude = tds[1].find("span", class_="longitude").text if tds[1].find("span",
                                                                                            class_="longitude") else "error"
                loc_country = tds[2].find("a").text if tds[2].a else "error"
                if tds[3].br:
                    tds[3].br.replace_with(":")
                loc_feature = tds[3].text.strip()
                line = [user, search_loc, loc_name, loc_country, loc_latitude, loc_longitude, loc_feature]
                print(("Record: " + "\t".join(line)).encode('utf-8'))
                fd_longitude.write(("\t".join([user, loc_latitude, loc_longitude])).encode('utf-8') + b"\r\n")
                fd_loc.write(("\t".join(line)).encode('utf-8') + b"\r\n")
    else:
        fd_wrong_loc.write((user + "\t" + search_loc + "\r\n").encode('utf-8'))
    return True


already_searched_lines = []
searched_history_file = r'output_searched'


def append_searched(line):
    with open(searched_history_file, 'a', encoding='utf-8') as file:
        file.write((line + "\n"))


def read__searched():
    if os.path.isfile(searched_history_file):
        with open(searched_history_file, 'r', encoding='utf-8') as file:
            return [l.strip for l in file.readlines()]
    else:
        data = []
    return data


if __name__ == "__main__":
    extract_user_city()
    already_searched_lines = read__searched()
    print(len(already_searched_lines))
    keyword = 'output'
    # keyword = "tmp"
    with open('user.location', "r", encoding="utf-8") as fr:
        data = fr.readlines()
    fd_longitude = open("%s_loc_longitude.txt" % keyword, "ab", buffering=0)
    fd_loc = open("%s_loc_detail.txt" % keyword, "ab", buffering=0)
    fd_wrong_loc = open("%s_loc_lost.txt" % keyword, "ab", buffering=0)
    print(len(data))
    for i in range(len(data)):
        print(i + 1, time.strftime('%Y-%m-%d: %H:%M:%S', time.localtime()))
        line = data[i].strip()
        if line == "":
            continue
        line = line.strip()
        if line in already_searched_lines:
            print('skip the line because already searched.')
            continue
        already_searched_lines.append(line)
        append_searched(line)

        # user = line[0:line.index(",")]
        splitbyspaces = line.split()
        if not splitbyspaces:
            continue
        user = splitbyspaces[0]
        exceptuser = line.replace(user, '').strip()
        if ',' in exceptuser:
            search_loc = exceptuser.split(',')[0].strip()
        else:
            search_loc = exceptuser
        if user.strip() == "":
            print("No user!")
            fd_wrong_loc.write("\t\n")
        elif search_loc.strip() == "":
            print("No loc! ", user)
            fd_wrong_loc.write(("%s\t\n" % (user)).encode('utf-8'))
        else:
            get_lon_lat(user, search_loc)

    fd_longitude.close()
    fd_loc.close()
    fd_wrong_loc.close()
