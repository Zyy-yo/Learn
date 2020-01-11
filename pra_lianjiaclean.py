import numpy as np 
import pandas as pd 
import pymongo
import re
import warnings

warnings.filterwarnings('ignore')

'''
北京二手房房源信息清洗
'''


def clean1(table1, table1_cleaned):
    # 清洗北京二手房房源数据
    data1 = list(table1.find())
    df1 = pd.DataFrame(data1)

    df1.replace('', np.nan, inplace=True)
    df1['标题'] = df1['标题'].str.rstrip('必看好房')
    df1['面积'] = df1['面积'].str.rstrip('平米').astype('float')
    df1['建成年份'][df1['建成年份'].notnull()] = df1['建成年份'][df1['建成年份'].notnull()].str.rstrip('年建')
    df1['发布时间'] = df1['发布时间'].str.lstrip()
    df1['总价'] = df1['总价'].str.rstrip('万').astype('float')
    df1.rename(columns={'总价':'总价_万'}, inplace=True)
    df1['单价'] = df1['单价'].astype('float')
    df1['关注人数'] = df1['关注人数'].astype('int')
    
    df1['总层高'] = np.nan
    for i in range(len(df1)):
        df1['总层高'].iloc[i] = re.search(r'(\d+)层', df1['楼层'].iloc[i]).group(1)
        lc = re.search(r'(\D*)楼层', df1['楼层'].iloc[i])
        if lc:
            df1['楼层'].iloc[i] = lc.group(1)
        else:
            df1['楼层'].iloc[i] = np.nan
    
    data = df1.to_dict('records')
    table1_cleaned.insert_many(data)


def clean2(table2, table2_cleaned):
    # 清洗北京二手房房源-含经纬度数据
    data2 = list(table2.find())
    df2 = pd.DataFrame(data2)

    df2.replace('暂无数据', np.nan, inplace=True)
    df2['建筑面积'] = df2['建筑面积'].str.rstrip('㎡').astype('float')
    df2['套内面积'] = df2['套内面积'].str.rstrip('㎡').astype('float')
    df2['房屋朝向'] = df2['房屋朝向'].str.replace(' ', '')
    df2['lng'] = df2['lng'].astype('float')
    df2['lat'] = df2['lat'].astype('float')

    df2['总层高'] = np.nan
    for i in range(len(df2)):
        df2['总层高'].iloc[i] = re.search(r'(\d+)层', df2['所在楼层'].iloc[i]).group(1)
        lc = re.search(r'(\D*)楼层', df2['所在楼层'].iloc[i])
        if lc:
            df2['所在楼层'].iloc[i] = lc.group(1)
        else:
            df2['所在楼层'].iloc[i] = np.nan
    
    data = df2.to_dict('records')
    table2_cleaned.insert_many(data)


if __name__ == '__main__':

    # 连接数据库
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['链家']

    table1 = db['北京二手房房源']
    table1_new = db['北京二手房源cleaned']

    table2 = db['北京二手房房源-含经纬度']
    table2_new = db['北京二手房源_含经纬度cleaned']

    # 数据清洗
    print('start')

    clean1(table1, table1_new)
    clean2(table2, table2_new)

    print('end')
