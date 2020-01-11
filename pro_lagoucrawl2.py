import numpy as np 
import pymongo
import re
import time
from selenium import webdriver

'''拉勾网公司信息采集'''

def access(ul, username, password):
    
    driver.get(ul)
    # 登录
    driver.find_element_by_xpath('//*[@id="lg_tbar"]/div/div[2]/ul/li[3]/a').click()  # 登录/注册选择登录
    account = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[1]/div/input')
    passw = driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[2]/div/input')
    account.send_keys(username)
    passw.send_keys(password)
    driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[2]').click()  # 登录
    time.sleep(30)        # 暂停30秒，留出验证找图片的时间


def get_data(driver, table):
    # 每页数据采集
    lis = driver.find_element_by_id('company_list').find_elements_by_tag_name('li')
    n = 0
    for li in lis:
        try:
            i = lis.index(li) + 1
            if i == 1:
                elem = driver.find_element_by_tag_name("html")
                elem.send_keys(webdriver.common.keys.Keys.SPACE)        # 空格键滚动屏幕
                time.sleep(1)
            dic = {}
            dic['公司名称'] = li.find_element_by_tag_name('h3').text
            info1 = li.find_element_by_class_name('indus-stage').text     # 公司，融资，规模
            dic['行业'] = info1.split('/')[0]
            dic['融资情况'] = info1.split('/')[1]
            dic['人数规模'] = info1.split('/')[2]
            dic['企业简介'] = li.find_element_by_class_name('advantage').text # 公司简介
            dic['面试评价'] = li.find_element_by_xpath('//*[@id="company_list"]/ul/li[%i]/div[2]/a[1]/p[1]'%i).text
            dic['在招职位'] = li.find_element_by_xpath('//*[@id="company_list"]/ul/li[%i]/div[2]/a[2]/p[1]'%i).text
            dic['简历处理率'] = li.find_element_by_xpath('//*[@id="company_list"]/ul/li[%i]/div[2]/a[3]/p[1]'%i).text
            table.insert_one(dic)
            n += 1
            time.sleep(np.random.uniform(1,3))
            # 加入滚屏
            if i % 8 == 0:
                elem = driver.find_element_by_tag_name("html")
                elem.send_keys(webdriver.common.keys.Keys.SPACE)        # 空格键滚动屏幕
                time.sleep(1)
        except:
            continue
    return n

if __name__ == '__main__':

    ul = 'https://www.lagou.com/gongsi/'
    username = '18201185468'
    password = 'liangjie0509'

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
    table = db['公司采集']

    # 采集前10页数据
    count = 0
    for i in range(1, 11):
        try:
            count += get_data(driver, table)
            print('采集数据%i条，第%i页采集完成'%(count, i))
            time.sleep(np.random.uniform(1,3))
            if i < 5:
                driver.find_element_by_xpath('//*[@id="company_list"]/div/div/span[%i]'%(i + 2)).click() # 选择下一页
                print('进入第%i页'%(i+1))     
            elif i >= 5 and i < 10:
                driver.find_element_by_xpath('//*[@id="company_list"]/div/div/span[6]').click() # 选择下一页
                print('进入第%i页'%(i+1))
        except:
            print('第%i页采集失败'%i)
    driver.close()
    driver.quit()
    print('采集完毕')
