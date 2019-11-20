import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt

'''
作业要求：
1、数据清洗 - 去除空值
2、问题1 知友全国地域分布情况，分析出TOP20
要求：
① 按照地域统计 知友数量、知友密度（知友数量/城市常住人口），不要求创建函数
② 知友数量，知友密度，标准化处理，取值0-100，要求创建函数
③	 通过多系列柱状图，做图表可视化
3、问题2 知友全国地域分布情况，分析出TOP20
要求：
① 按照学校（教育经历字段） 统计粉丝数（‘关注者’）、关注人数（‘关注’），并筛选出粉丝数TOP20的学校，不要求创建函数
② 通过散点图 → 横坐标为关注人数，纵坐标为粉丝数，做图表可视化
③ 散点图中，标记出平均关注人数（x参考线），平均粉丝数（y参考线）
'''

'''
read_csv来读取数据，读取之后数据就是dataframe格式了
删除重复id
填充缺失值
将知友表按照居住地分组求和，取id列
链接人口表地区字段
计算密度及标准化，输出新表和新的字段名，取前20
按照教育经历分组求和，取关注、关注者列，查看前20的数据，删除不要的数据，再取前20
'''

pd.set_option('display.max_columns', None)
df1 = pd.read_csv(r'D:\工作\数据分析\微专业\项目数据\知乎数据_201701.csv', encoding='ANSI')
df2 = pd.read_csv(r'D:\工作\数据分析\微专业\项目数据\六普常住人口数.csv', encoding='ANSI')


# 填充缺失值

def fil(df):
    df.drop_duplicates(subset='_id', inplace=True)
    for col in df.columns:
        if df[col].dtype == object:
            df[col].fillna('缺失数据', inplace=True)
        else:
            df[col].fillna(0, inplace=True)
    return df

df1_fil = fil(df1)

# 链接知友表和人口表

def mer():
    zy_count = df1_fil.groupby('居住地').count()['_id'].\
                        sort_values(ascending=False).drop('缺失数据')
    df2['市'] = df2['地区'].str[:-1]
    mer = pd.merge(zy_count, df2, left_index=True, right_on='市')
    mer['知友密度'] = mer['_id'] / mer['常住人口']
    return mer

zy_pop = mer()

# 计算密度及其标准化

def cal(df, *cols):
    colnames = []
    for col in cols:
        colname = col + 'nor'
        colnames.append(colname)
        df[colname]= (df[col] - df[col].min()) / (df[col].max() - df[col].min()) * 100
    return (df, colnames)

# 按前20名提取知友数量和密度标准化表，提取数量和密度标准化列

def y():
    cal_nor = cal(zy_pop, '_id','知友密度')
    resultdf = cal_nor[0]
    colsort = cal_nor[1]
    nor_sl = resultdf[['市', colsort[0]]][:20]
    nor_md = resultdf.sort_values(colsort[1], ascending=False)[['市', colsort[1]]][:20]
    y_sl = nor_sl[colsort[0]]
    y_md = nor_md[colsort[1]]
    return (nor_sl, nor_md, y_sl, y_md)

# 数量和密度标准化列作为纵坐标

y1, y2 = y()[2:]

# 绘图

fig1 = plt.figure(figsize=(10,6))
plt.title('全国知友数量top20')

plt.bar(np.arange(20), y1, facecolor='g', tick_label=y()[0]['市'])
for i, j in zip(np.arange(20), y1):
    plt.text(i-0.3, j, '%.1f'%j)
fig2 = plt.figure(figsize=(10,6))
plt.title('全国知友密度top20')
plt.bar(np.arange(20), y2, tick_label=y()[1]['市'])
for i, j in zip(np.arange(20), y2):
    plt.text(i-0.3, 1, '%.1f'%j, color='w')


# 教育经历分组

def edu(x):
    df_edu = x.groupby('教育经历').sum()[['关注','关注者']].\
                        sort_values('关注', ascending=False).\
                        drop(['缺失数据','大学','本科','大学本科'])
    return (df_edu[:20])

edu_g = edu(df1_fil)

ey1 = edu_g['关注']
ey2 = edu_g['关注者']

follow = ey1.mean()
fan = ey2.mean()

# 绘图

fig3 = plt.figure(figsize=(8,5))
plt.title('全国知友学校分布top20')

plt.scatter(ey1, ey2, s=ey2/1000, c=ey1, cmap='rainbow', label='学校')
plt.xlabel('关注人数')
plt.ylabel('粉丝数')
plt.axvline(follow, linestyle='--', color='b', label='平均关注人数%i'%follow, linewidth=1, alpha=0.5)
plt.axhline(fan, linestyle='--', color='r', label='平均粉丝数%i'%fan, linewidth=1, alpha=0.5)
for i, j, n in zip(ey1, ey2, edu_g.index):
    plt.text(i, j, n, fontsize=8)
plt.legend()

plt.show()