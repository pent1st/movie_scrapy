# encoding=utf-8

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import re


# 获取城市列表和id
city_list = {}

def get_city_id():
    url = 'https://dianying.taobao.com/'
    # driver = webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
    driver = webdriver.PhantomJS()
    driver.get(url)
    driver.find_element_by_id('cityName').click()
    sleep(1)

    # print driver.page_source
    soup = BeautifulSoup(driver.page_source, 'lxml')
    city_div = soup.find('div', class_="M-cityList scrollStyle")
    city_list_a = city_div.find_all('a')

    for city in city_list_a:
        city_list[city.text] = city.get('data-id')
    driver.close()


    # try:
    #     city_id = city_list[city_name]
    # except Exception as e:
    #     print '城市不存在'
    # else:
    #     return city_id

# get_city_id('杭州'.decode('utf-8'))
# https://h5.m.taobao.com/app/moviemain/pages/cinema-list/index.html



# 获取所选城市的电影院列表和id
cinema_list = {}
def get_cinema_id(city_name):
    url = 'https://h5.m.taobao.com/app/moviemain/pages/cinema-list/index.html'
    # driver = webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
    driver = webdriver.PhantomJS()
    driver.get(url)
    sleep(5)
    driver.find_element_by_id('citySelecter').click()
    # selenium 每次模拟点击后最好sleep(3),防止页面还未完全加载导致后面语句出错
    sleep(3)
    driver.find_elements_by_link_text(city_name.decode('utf-8'))[0].click()
    sleep(3)
    #　用find_elements_by_class_name 失败， 采用bs
    soup = BeautifulSoup(driver.page_source, 'lxml')
    cinema_lis = soup.find_all('li', class_='list-item list-normal')
    for cinema in cinema_lis:
        cinema_name = cinema.find('span', class_="list-title").text
        cinema_id = re.findall('&cinemaid=(\w*)&', cinema.find('div', class_="list-item-in").get('data-href'))[0]
        cinema_list[cinema_name] = cinema_id

    driver.close()




movie_list = {}
def get_movie_id():
    url = 'https://dianying.taobao.com/showList.htm'
    res = requests.get(url)

    soup = BeautifulSoup(res.text, 'lxml')

    movie_div = soup.find_all('div', class_="tab-movie-list")[0]
    movie_lists = soup.find_all('div', class_="movie-card-wrap")
    for movie in movie_lists:
        movie_url = movie.find_all('a', class_="movie-card")[0].get_attribute_list('href')[0]
        movie_name = movie.find_all('span', class_="bt-l")[0].text
        movie_id = re.findall('\?showId=(\w*)&', movie_url)[0]
        movie_list[movie_name] = movie_id



# 得到最终url，获取票价信息
def main():
    print '\n淘票票：\n'.decode('utf-8')
    last_url = 'https://h5.m.taobao.com/app/movie/pages/index/show-list.html?cinemaid=' + str(cinema_id) + '&showid=' + str(movie_id)
    # driver = webdriver.Chrome(executable_path='C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe')
    driver = webdriver.PhantomJS()
    driver.get(last_url)
    sleep(3)

    soup = BeautifulSoup(driver.page_source, 'lxml')
    movie_ul = soup.find('ul', class_="schedules-item-wrap")
    for movie in movie_ul.find_all('li')[1:]:
        if  not movie.find('div', class_='time-line'):
            print movie.find('span', class_="item-clock").text,
            print movie.find('span', class_="item-end").text,
            print movie.find('span', class_="item-type").text,
            print movie.find('span', class_="item-price").text[1:]
    driver.close()


if __name__ == '__main__':
    main()


