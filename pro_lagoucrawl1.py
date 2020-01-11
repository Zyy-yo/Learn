import numpy as np 
import pymongo
import re
from selenium import webdriver
import time 

'''拉勾网上海地区数据挖掘职位搜索信息采集'''

def access(ul, username, password):

    driver.get(ul)
    driver.find_element_by_xpath('//*[@id="changeCityBox"]/ul/li[2]/a').click()   # 选择城市，这里选择上海

    # 登录
    driver.find_element_by_xpath('//*[@id="lg_tbar"]/div/div[2]/ul/li[3]/a').click()  # 登录/注册选择登录
    account = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[1]/div/input')
    passw = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[2]/div/input')
    account.send_keys(username)
    passw.send_keys(password)
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[2]').click()  # 点击登录
    time.sleep(30)    # 暂停30秒，留出验证找图片的时间

    # 搜索‘数据挖掘’
    search = driver.find_element_by_xpath('//*[@id="search_input"]')  
    search.send_keys('数据挖掘')  
    driver.find_element_by_xpath('//*[@id="search_button"]').click() 
    driver.find_element_by_class_name('body-btn').click()  # 关闭新页面跳出的弹窗


def get_data(driver, table):
    # 每一页数据采集
    n = 0
    for i in range(1, 16):
        try:
            if i == 1:
                elem = driver.find_element_by_tag_name("html")
                elem.send_keys(webdriver.common.keys.Keys.SPACE)        # 空格键滚动屏幕
                time.sleep(1)
            dic = {}
            dic['post'] = driver.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[%i]/div[1]/div[1]/div[1]/a/h3'%i).text   # 职位
            dic['addr'] = driver.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[%i]/div[1]/div[1]/div[1]/a/span/em'%i).text  # 位置
            dic['company'] = driver.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[%i]/div[1]/div[2]/div[1]/a'%i).text  # 公司
            info1 = driver.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[%i]/div[1]/div[1]/div[2]/div'%i).text  # 薪水，学历要求，经验要求
            info2 = driver.find_element_by_xpath('//*[@id="s_position_list"]/ul/li[%i]/div[1]/div[2]/div[2]'%i).text  # 行业，融资情况，公司规模

            dic['salary'] = re.search(r'(\d*k-\d*k) ', info1).group(1) # 薪水
            dic['exper'] = re.search(r' (.*) /', info1).group(1) # 经验
            dic['edu'] = re.search(r'/ (\D*)', info1).group(1) # 学历

            dic['indust'] = re.search(r'(.*?) /', info2).group(1) # 行业
            dic['rongzi'] = re.search(r'/ (.*) /', info2).group(1)  # 融资情况
            dic['guimo-ren'] = re.search(r'/ ([\d-]*)人', info2).group(1) # 人数规模
            table.insert_one(dic)
            n += 1
            time.sleep(np.random.uniform(1,3))
            if i % 4 == 0 or i == 15:
                elem = driver.find_element_by_tag_name("html")
                elem.send_keys(webdriver.common.keys.Keys.SPACE)       # 空格键滚动屏幕
                time.sleep(1)
        except:
            continue
    return n

if __name__ == '__main__':

    ul = 'https://www.lagou.com/'
    
    # 用户名/密码
    username = 'xxxxx'
    password = 'xxxxx'

    option = webdriver.ChromeOptions()
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    driver = webdriver.Chrome(options=option)
    driver.maximize_window()        # 窗口最大化
    time.sleep(2)

    # 访问网页
    access(ul, username, password)

    # 连接数据库
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client['拉勾网']
    table = db['上海-数据挖掘职位采集']

    # 采集前10页
    count = 0
    for i in range(1,11): 
        try:
            count += get_data(driver, table)
            print('采集数据%i条，第%i页采集完成'%(count, i))
            time.sleep(np.random.uniform(1,3))
            if i < 5:
                driver.find_element_by_xpath('//*[@id="s_position_list"]/div[2]/div/span[%i]'%(i + 2)).click() # 选择下一页
                print('进入第%i页'%(i+1))  
            elif i >= 5 and i < 10:
                driver.find_element_by_xpath('//*[@id="s_position_list"]/div[2]/div/span[6]').click() # 选择下一页
                print('进入第%i页'%(i+1))
        except:
            print('第%i页采集失败'%i)
    driver.close()
    driver.quit()
    print('采集完毕')


