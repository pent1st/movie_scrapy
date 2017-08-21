# coding=utf-8
# 根据输入的条件（城市、影片、日期），列出不同网站（至少2个）的票价对比 。
# 百度糯米

import requests
import pymongo
from lxml import etree
from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
import taopiaopiao_ as tpp

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36',
}

# 连接数据库，数据库为movie_scrapy, city_list表保存城市信息
client = pymongo.MongoClient()
db = client.movie_scrapy
city_collections = db.city_list
movie_collections = db.movie_msg

# 获取城市信息保存在数据库中
def print_city_msg():
    adr_url = 'https://dianying.nuomi.com/common/city/citylist?hasLetter=false&isjson=false&channel=&client='
    adr = requests.get(adr_url, headers=headers)
    all_data = adr.json()
    city_list = all_data['data']['all']

    #  打印出用户可选城市列表
    for i in city_list:
        print i['name'],

    # 将城市信息插入到数据库中
    # city_collections.insert_many(city_list)

# 根据用户输入的城市信息得到百度糯米的电影链接
def get_city_id(city_name):
    try:
        city_id = city_collections.find_one({'name':city_name})['id']
    except Exception as e:
        print '城市不存在，请重新输入'.decode('utf-8')
    else:
        return city_id
    return False

# 根据城市id的电影链接得到"正在热映"列表电影名称和评分
def get_movies(city_id):
    movie_url = 'https://dianying.nuomi.com/index?cityId=' + str(city_id)
    html = requests.get(movie_url, headers=headers)
    tree = etree.HTML(html.text)
    hot_movie_div = tree.xpath('//div[@id="flexslider1"]')[0]
    # print hot_movie_div[0]
    hot_movies = hot_movie_div.xpath('.//li')
    for hot_movie in hot_movies:
        movie_name = hot_movie.xpath('.//p[@class="text font14"]/text()')[0]
        movie_score = hot_movie.xpath('.//span[@class="fr record nuomi-orange"]/text()')[0]
        print movie_name, movie_score



# 保存电影id等信息
def save_movie_msg():
    ranklist_url = 'https://dianying.nuomi.com/common/ranklist?sortType=1&date=1502525303386&channel=&client='
    res = requests.get(ranklist_url, headers=headers)
    movie_datas = res.json()
    movie_data = movie_datas['data']['movies']
    for movie in movie_data:
        movie_collections.update_one({'movieId':movie['movieId']}, { '$set': movie}, upsert = True)


def get_movie_id(movie_name):
    # movie_name = raw_input('\n输入你需要看的电影名称：\n').encode('utf-8')
    try:
        movie_detail = movie_collections.find_one({'movieName': movie_name})
        movie_id = movie_detail['movieId']
    except Exception as e:
        print '电影名不正确，请重新输入电影名称：'.decode('utf-8')
    else:
        return movie_id
    return False


# 获取电影院id
cinema_dict = {}
def get_cinema_id(url):
    # driver = webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
    driver = webdriver.PhantomJS()
    driver.get(url)
    sleep(3)

    while True:
        driver.find_element_by_id("moreCinema").click()
        sleep(1)
        try:
            result = driver.find_elements_by_xpath('//div[@id="moreCinema"]')[0].text
            if result == u'没有更多结果了':
                break
        except Exception as e:
            pass

    page_source = driver.page_source
    cinema_tree = etree.HTML(page_source)
    cinema_lis = cinema_tree.xpath('//div[@id="pageletCinemalist"]/li')

    for cinema_li in cinema_lis:
        cinema_name = cinema_li.xpath('.//span[@class="name"]')[0].text
        cinema_id = cinema_li.xpath('.//p[@class="title"]/@data-data')[0].strip('{}').split(':')[1]
        print cinema_name,cinema_id
        cinema_dict[cinema_name] = cinema_id
    driver.close()


# 根据city_id, movie_id, cinema_id 获取票价等信息
def get_price_msg(city_id, cinema_id, movie_id):
    print '\n百度糯米：\n'.decode('utf-8')
    last_url = 'https://mdianying.baidu.com/cinema/detail?cityId='+ str(city_id)+'&cinemaId='+ str(cinema_id) + '&movieId=' + str(movie_id)
    res = requests.get(last_url, headers=headers)
    soup = BeautifulSoup(res.text, 'lxml')
    play_list_div = soup.find('div', class_='daily-schedule-list')
    try:
        play_list = play_list_div.find_all('div', 'daily-schedule touching ')
        for play in play_list:
            print play.find('div', class_='start').text,
            print play.find('div', class_='end').text,
            print play.find('div', class_='lan').text,
            print play.find('div', class_='theater ').text,
            print play.find('div', class_='price').text.strip(' \n&yen')[:-len(str(play.find('s').text))]
    except Exception as e:
        print '无放映信息'.decode('utf-8')


def main():
    print '\n可选的城市列表：\n'.decode('utf-8')
    print_city_msg()

    flag = False
    while not flag:
        city_name = raw_input('\n请输入你的城市:\n'.decode('utf-8')).encode('utf-8')
        flag = city_id = get_city_id(city_name)
    tpp.city_name = city_name
    tpp.get_cinema_id(city_name)


    print '\n正在热映的电影列表:\n'.decode('utf-8')
    get_movies(city_id)
    save_movie_msg()


    flag = False
    while not flag:
        movie_name = raw_input('\n请输入你想看的电影名称：\n'.decode('utf-8')).encode('utf-8')
        flag = movie_id = get_movie_id( movie_name)
    tpp.movie_name = movie_name
    tpp.get_movie_id()
    tpp.movie_id = tpp.movie_list[movie_name.decode('utf-8')]
    # print 'movie_id', movie_id

    # 根据输入的城市和电影名称拼接出url，
    url = 'https://dianying.nuomi.com/movie/detail?cityId=' + str(city_id) + '&movieId=' + str(movie_id)
    # print url

    get_cinema_id(url)
    # for cinema_name,cinema_id in cinema_dict.items():
    #     print cinema_name

    flag = False
    while not flag:
        try:
            cinema_name = raw_input('\n请输入你想看的电影院名称：\n'.decode('utf-8')).encode('utf-8')
            flag = cinema_id = cinema_dict[cinema_name.decode('utf-8')]
        except Exception as e:
            print '\n输入错误或不存在，请重新输入电影院名称：\n'.decode('utf-8')
        else:
            break
    tpp.cinema_name = cinema_name
    tpp.cinema_id = tpp.cinema_list[cinema_name.decode('utf-8')]

    get_price_msg(city_id, cinema_id, movie_id)
    tpp.main()

    # get_cinema_id(url)
    # for cinema_name,cinema_id in cinema_dict.items():
    #     print cinema_name
    #     get_price_msg(city_id, cinema_id, movie_id)


if __name__ == '__main__':
    main()

