import numpy as np 
import pandas as pd 
import os
import re


'''
上海租房租金预测第一部分：数据初步清洗

通过探查数据发现数据问题：
    面积和房租字段含有字符，为字符型；
    租赁方式字段相同类别部分含有字符；
    租赁方式中分整租和合租，合租所对应的房屋面积部分为真实合租面积，部分为整屋面积
    公交站字段含有多种信息，可以提取单独成列
    户型可以分割单独成列
    地址中含有非上海房源信息，数据量非常小
    朝向中大部分数据朝南
    面积、朝向等含有缺失值

初步清洗中清洗字段：
    面积、房租字段提取数字，转为浮点型
    统一租赁方式字段中的类别
    提取公交车站中的地铁线、地铁站名和距离信息
    分割户型字段
    填充面积缺失值
    将朝向字段制作为哑变量
    为了方便获取地理编码，对地址做一下处理
'''

def area_rent(s):
    '''
    清洗面积和房租字段，提取数字，转为浮点型
    '''
    if pd.isnull(s):
        return s
    else:
        return float(re.match(r'(\d*)', s).group(1))


def stations(s):
    '''
    清洗公交站字段，提取地铁线路/地铁站/距离
    '''
    if pd.notnull(s):
        station_match = re.match(r'距(\d+)号线(\D+)站约(\d+)米', s)
        if station_match:
            return station_match.groups()
        else:
            return np.nan
    else:
        return s


def house_type(s):
    '''
    清洗户型字段，提取数字
    '''
    ht_match = re.match(r'(\d+)室(\d+)厅', s)
    if ht_match:
        return ht_match.groups()



if __name__ == '__main__':

    os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习10_住宅租金预测')

    # 建立空dataframe
    df_all = pd.DataFrame()

    # pd.set_option('display.max_columns', None)

    # 读取文件
    for f in os.walk(r'data'):
        flis = f[2]
    
    # 循环读取单个csv文件，清洗数据，合并
    print('cleaning...')
    for f in flis:
        df = pd.read_csv('data/' + f)

        # 清洗面积字段
        df['area'] = df['面积'].map(area_rent)
        
        # 清洗房租字段
        df['rent_month'] = df['房租'].map(area_rent)

        # 清洗户型字段
        df['rooms'] = df['户型'].map(house_type).str[0]
        df['halls'] = df['户型'].map(house_type).str[1]

        # 清洗朝向字段
        df['sorth_ori'] = df['朝向'].map(lambda x: 1 if x == '朝南' else 0)

        # 清洗公交站字段
        df['sub_line'] = df['公交站'].map(stations).str[0]
        df['sub_station'] = df['公交站'].map(stations).str[1]
        df['sub_distance'] = df['公交站'].map(stations).str[2].astype('float')

        # 清洗租赁方式字段
        df['lease_mode'] = df['租赁方式'].str.rstrip('㎡')

        # 地址
        df['address'] = df['城市'] + '市' + df['区域'] + '区' + df['地段']

        # 填充面积缺失值
        df['area'].fillna(df['area'].median(), inplace=True)


        # 提取需要的字段
        df_sel = df.copy()[['area', 'rent_month', 'rooms', 'halls', 'lease_mode', 'sorth_ori', 'address', '区域', 'sub_line', 'sub_station', 'sub_distance']]

        # 合并dataframe
        df_all = pd.concat([df_sel, df_all])

    # 保存到本地
    df_all.to_csv('data_cleaned.csv', index=False)
    print('clean done!')
