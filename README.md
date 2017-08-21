# 项目概述
从电影购票网站上获取近期上映电影及影院信息，
根据输入的条件（城市、影片、影院），
列出百度糯米和淘票票的票价对比 。

# 项目文件：  

## 1.taopiaopiao_.py

### 文件作用
    根据用户输入的城市，电影院和电影名称得到淘票票网站的票价信息
### 文件逻辑：
    根据last_url = 'https://h5.m.taobao.com/app/movie/pages/index/show-list.html?cinemaid=4288&showid=186599'思路获取cinemeid和showid
    1.  获取淘票票的城市列表和id，保存在字典city_list中，可以根据用户输入的城市得到城市id，
    2.  根据城市得到电影院名称和id，保存在字典cinema_list中，可以根据用户输入的电影院名称得到相应的cinemaid
    3.  获取电影名称和id，保存在字典movie_list，可以根据用户输入的电影名称得到showid
    4.  得到最终url，获取票价信息


## 2.nuomi.py

### 文件作用
    根据用户输入的城市，电影院和电影名称得到百度糯米网站的票价信息

### 文件逻辑
    1. 访问https://dianying.nuomi.com/common/city/citylist?hasLetter=false&isjson=false&channel=&client=，保存所有的城市信息（城市名称和城市id），保存在mongo数据库中
    2. 通过用户输入的城市信息得到热映列表信息（电影名称和电影id），保存在mongo数据库中
    3. 将获得的电影信息保存在mongo数据库中
    4. 通过电影名称查找电影id
    5. 获得电影院信息（电影院名称和电影院id），保存在字典cinema_dict中，可以根据用户输入的电影院名称得到cinemaid
    6. 通过用户输入的城市名称，电影名称，电影院名称得到相应id，最终拼接成last_url

# 项目使用说明
    1. mongod  启动mongo数据库
    2. nuomi.py 执行主程序，根据提示输入城市，电影名称，电影院名称得到百度糯米和淘票票的票价信息