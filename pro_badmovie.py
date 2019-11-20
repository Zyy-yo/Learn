import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models.annotations import BoxAnnotation
from scipy import stats
import os 
import warnings 

warnings.filterwarnings('ignore') 
os.chdir(r'D:\工作\数据分析\微专业\项目数据\考核项目05_国产烂片深度揭秘')

data = pd.read_excel('moviedata.xlsx')

'''
1、读取数据，以“豆瓣评分”为标准，看看电影评分分布，及烂片情况
    查看“豆瓣评分”数据分布，绘制直方图、箱型图
    判断“烂片标准” → 这里以上四分位数（该样本中所有数值由小到大排列后第25%的数字）评分为“烂片标准”
    筛选出烂片数据，并做排名，找到TOP20
'''

score = data.dropna(subset=['豆瓣评分'])[['电影名称', '豆瓣评分', '导演', '主演', '制片国家/地区']]
score = score[score['制片国家/地区'].str.contains('中国')]

def hist_box():
    # 绘制数据分布直方图和箱型图
    fig1 = plt.figure(figsize=(8,6))
    score['豆瓣评分'].plot.hist(bins=20, edgecolor='w', color='g', alpha=0.5, title='豆瓣评分直方图')
    plt.savefig('豆瓣评分直方图.jpg')

    fig2 = plt.figure(figsize=(5,6))
    color = dict(boxes='g', whiskers='black', medians='r', caps='b')
    score['豆瓣评分'].plot.box(color=color, title='豆瓣评分箱型图')
    plt.savefig('豆瓣评分箱型图.jpg')
hist_box()

def badfil(df):
    # 筛选烂片
    stan = df['豆瓣评分'].quantile(0.25)
    score_min = df[df['豆瓣评分'] < stan].sort_values('豆瓣评分').reset_index(drop=True)
    print('评分低于4.3分的电影数据量有：%i'%len(score_min))
    return score_min
badms = badfil(score)

def bad20_fig(df):
    # 烂片top20绘图
    bad20 = df[:20]
    f = bad20.plot.line(figsize=(13,5), xlim=[19,0], xticks=range(19,-1,-1), yticks=np.arange(2.1,2.5,0.1),\
        color='yellowgreen', lw=8, title='烂片top20')
    f.set_xticklabels(bad20['电影名称'][::-1].tolist(), rotation=45)
    plt.grid(ls='--', alpha=0.3, axis='x')
    plt.savefig('豆瓣评分烂片top20.jpg', bbox_inches='tight')
bad20_fig(badms)


'''
2、什么题材的电影烂片最多？
    按照“类型”字段分类，筛选不同电影属于什么题材
    整理数据，按照“题材”汇总，查看不同题材的烂片比例，并选取TOP20
    将得到的题材烂片比例TOP20制作散点图 → 横坐标为“题材”类型，纵坐标为烂片比例，点大小为样本数量
        用bokeh制图
        按照烂片比例做降序排列
'''

types = data[['类型', '豆瓣评分']].dropna()

def type_bad(df):
    # 按照电影类型计算烂片占比
    df['是否烂片'] = 0
    df['是否烂片'][df['豆瓣评分'] < 4.3] = 1      # 烂片标记1

    ss = df[['类型', '是否烂片']]
    ss = pd.concat([pd.Series(row['是否烂片'], row['类型'].split('/')) for _, row in ss.iterrows()])  # 将多个类型做分割
    ss.index.name = '类型'

    df2 = pd.DataFrame(ss, columns=['烂片量']).reset_index()
    df2['类型'] = df2['类型'].str.strip()

    df2_g = df2.groupby('类型').sum()                        # 按类型分组，统计烂片量
    df2_g['影片量'] = 0
    for i in df2_g.index.tolist():
        df2_g['影片量'][i] = len(df[df['类型'].str.contains(i)])         # 按类型计算各类型影片数量
    df2_g['烂片比例'] = df2_g['烂片量'] / df2_g['影片量']           # 计算各类型烂片比例

    return df2_g.sort_values('烂片比例', ascending=False)

typebad20 = type_bad(types)[:20]

def bok_sca(df):
    # 绘制不同题材电影烂片比例前20散点图
    df.columns = ['badcount', 'sumcount', 'bad_per']
    df.index.name = 'movietype'
    df['size'] = df['sumcount'] * 0.1
    inds = df.index.tolist()
    source = ColumnDataSource(df)
    output_file('电影题材烂片比例top20.html')
    hover = HoverTool(tooltips=[('影片量', '@sumcount'),
                                ('烂片量', '@badcount'),
                                ('烂片占比', '@bad_per')])
    p = figure(plot_width=800, plot_height=300, title='不同电影题材烂片比例前20', x_range=inds,
               tools=[hover, 'pan, box_select, wheel_zoom, box_zoom, reset, save'])
    p.circle(x='movietype', y='bad_per', source=source, size='size', color='red',
            alpha=0.8, line_color='gray', line_dash=[3,4])
    show(p)
bok_sca(typebad20)


'''
3、和什么国家合拍更可能产生烂片？
    筛选合作电影大于等于3部以上的国家
'''

country = data[['制片国家/地区', '豆瓣评分']].dropna()

def fil1(df):
    # 第一步筛选，筛掉未和其他国家或地区合拍的电影
    df = df[df['制片国家/地区'].str.contains('/')]       # 删除只有一个国家或地区的数据
    df['制片国家/地区'] = df['制片国家/地区'].str.replace(' ', '')       # 去除空格
    df = df[df['制片国家/地区'].str.contains('中国')]       # 筛选包含中国的值
    return df

cty = fil1(country)
cty_minscore = cty[cty['豆瓣评分'] < 4.3]         # 筛选评分低于4.3分的烂片

def takecountry(df):
    # 获取国家/地区
    ct = []
    for i in df['制片国家/地区']:
        i = i.split('/')
        ct.extend(i)
    cts = list(set(ct))
    for i in ['中国大陆', '中国', '香港', '台湾']:
        cts.remove(i)
    return cts
countries = takecountry(cty)

def cty_movie_bad():
    # 计算合作国家的电影量和烂片量，计算合拍电影烂片比例
    # 筛选合拍电影3部（含）以上的数据
    cdf = pd.DataFrame({'country': countries})
    cdf['moviecount'] = 0
    cdf['badmovie'] = 0
    for c in countries:
        cdf['moviecount'][cdf['country'] == c] = len(cty[cty['制片国家/地区'].str.contains(c)])
        cdf['badmovie'][cdf['country'] == c] = len(cty_minscore[cty_minscore['制片国家/地区'].str.contains(c)])
    cdf = cdf[cdf['moviecount'] >= 3]
    cdf['bad_per'] = cdf['badmovie'] / cdf['moviecount']
    cdf.sort_values('bad_per', ascending=False, inplace=True)
    return cdf

cooperate_bad = cty_movie_bad()


def bok_sca2(df):
    # 与他国合拍电影烂片占比散点图
    ran = df['country'].tolist()
    source = ColumnDataSource(df)
    output_file('与他国合拍电影烂片占比.html')
    hover = HoverTool(tooltips=[('合作量', '@moviecount'),
                                ('烂片量', '@badmovie'),
                                ('烂片占比', '@bad_per')])
    p = figure(plot_width=600, plot_height=300, title='与他国合拍电影3部及以上电影烂片占比', x_range=ran,
               tools=[hover, 'pan, wheel_zoom, box_select, reset, save'])
    p.circle(x='country', y='bad_per', source=source, size='moviecount', color='green', line_dash='dotted')
    show(p)
bok_sca2(cooperate_bad)


'''
卡司数量是否和烂片有关？
    计算每部电影的主演人数
    按照主演人数分类，并统计烂片率
        分类：'1-2人','3-4人','5-6人','7-9人','10以上'
    查看烂片比例最高的演员TOP20
'''

actor1 = data[['电影名称', '主演', '豆瓣评分']].dropna()
actor1['主演人数'] = 0
actor1['主演人数'] = actor1['主演'].str.split('/').str.len()     # 计算电影主演人数


def corre():
    # 查看主演人数与评分是否相关
    pfmean = actor1['豆瓣评分'].mean()      # 豆瓣评分字段均值和标准差
    pfstd = actor1['豆瓣评分'].std()
    rsmean = actor1['主演人数'].mean()       # 主演人数字段均值和标准差
    rsstd = actor1['主演人数'].std()

    print(stats.kstest(actor1['豆瓣评分'], 'norm', (pfmean, pfstd)))    # 进行正态性检验
    print(stats.kstest(actor1['主演人数'], 'norm', (rsmean, rsstd)))
    print(actor1.corr('spearman'))         #  查看主演人数和电影评分相关性，主演人数和电影评分不存在相关 

    plt.figure(figsize=(6,6))
    plt.scatter(actor1['豆瓣评分'], actor1['主演人数'])
    plt.savefig('主演人数和豆瓣评分散点图.jpg')
corre()

def classify(df):
    # 将主演人数按照'1-2人','3-4人','5-6人','7-9人','10人以上'进行分类，并计算每类别的烂片比例
    actor_cla = pd.cut(df['主演人数'], bins=[1,3,5,7,10,100], right=False, labels=['1-2人', '3-4人', '5-6人', '7-9人', '10人以上'])
    df['人数分类'] = actor_cla

    df2 = df[['人数分类', '豆瓣评分']]
    maj_ac = df2.groupby('人数分类').count()
    maj_ac = pd.DataFrame(maj_ac).rename(columns={'豆瓣评分': '电影数量'})
    maj_ac['烂片量'] = 0
    for i in ['1-2人', '3-4人', '5-6人', '7-9人', '10人以上']:
        maj_ac['烂片量'][i] = len(df2[(df2['人数分类'] == i) & (df2['豆瓣评分'] < 4.3)])
    maj_ac['烂片占比'] = maj_ac['烂片量'] / maj_ac['电影数量']
    return maj_ac
actor_num = classify(actor1)
# print(actor_num.head())

def pol(df):
    # 绘制不同主演人数分类的烂片占比图示
    plt.figure(figsize=(5,5))
    ax = plt.subplot(111, projection='polar')
    ax.set_title('不同主演人数分类的烂片占比')
    th = np.arange(0, 2*np.pi, 2*np.pi/5)

    ax.bar(th, df['电影数量'], color='burlywood')
    ax.bar(th, df['烂片量'], color='chocolate')
    plt.legend(['电影数量', '烂片量'], loc=(0.83, 0.9))

    for i, j in zip(th, df['烂片占比']):
        plt.text(i, 300, '%.1f%%'%(j*100), color='brown')
    
    plt.thetagrids(np.arange(0, 360, 72), labels=['1-2人','3-4人','5-6人','7-9人','10人以上'])
    plt.savefig('不同主演人数分类的烂片占比.jpg')
pol(actor_num)

actor2 = data[['电影名称', '主演', '豆瓣评分']].dropna()
actor2['主演'] = actor2['主演'].str.replace(' ', '')

def takeactor(df):
    # 获取主演名称唯一值
    acts=[]
    for i in df['主演']:
        i = i.split('/')
        acts.extend(i)
    acts = list(set(acts))
    return acts
actors = takeactor(actor2)

def act_scor():
    # 获取电影10部以上主演烂片率
    df = pd.DataFrame(actors, columns=['actor_name'])
    df['moviesum'] = 0
    df['badmovie'] = 0
    df.set_index('actor_name', inplace=True)
    for i in actors:
        df['moviesum'][i] = len(actor2[actor2['主演'].str.contains(i)])
        df['badmovie'][i] = len(actor2[actor2['主演'].str.contains(i) & (actor2['豆瓣评分'] < 4.3)])
    df['bad_per'] = df['badmovie'] / df['moviesum']
    df = df[df['moviesum'] >= 10]
    df.sort_values('bad_per', ascending=False, inplace=True)
    return df

act_badper = act_scor()[:20]      # 电影总量10部以上主演烂片率前20


def barstack(df):
    # 演员烂片率top20绘图
    plt.figure(figsize=(12,5))
    df['moviesum'].plot.bar(rot=10, title='影片10部以上演员的烂片占比前20', color='lightseagreen')
    df['badmovie'].plot.bar(rot=10, color='lightskyblue')
    plt.legend(['影片量', '烂片量'])
    for i, j in zip(range(0,20), df['bad_per']):
        plt.text(i-0.3, 1, '%.1f%%'%(j*100))
    plt.savefig('影片10部以上演员的烂片占比前20.jpg', bbox_inches='tight')
barstack(act_badper) 


'''
不同导演每年电影产量情况是如何的？
    通过“上映日期”筛选出每个电影的上映年份
    查看不同导演的烂片比例、这里去除掉拍过10次电影以下的导演
    查看不同导演每年的电影产量制作散点图 → 横坐标为年份，纵坐标为每年电影平均分，点大小该年电影数量
        用bokeh制图
        横坐标限定为2007-2017年
        绘制散点图只需要用产出过烂片的导演数据
'''

direc = data[['导演', '豆瓣评分', '上映日期', '电影名称']]

def cfirst(df):
    # 处理上映日期，得到上映年份，删除空值数据
    df['年份'] = df['上映日期'].str.strip().str[:4]
    df['年份'].replace(['暂无', '不详'], np.nan, inplace=True)
    df.dropna(inplace=True)
    return df
direc = cfirst(direc)


def direc_split(df):
    # 将导演字段进行分割
    df1 = df[['导演', '豆瓣评分', '年份']].copy().set_index('导演')

    s1 = pd.concat([pd.Series(row['豆瓣评分'], i.split('/')) for i, row in df1.iterrows()])
    s2 = pd.concat([pd.Series(row['年份'], i.split('/')) for i, row in df1.iterrows()])

    df2 = pd.concat([s1,s2], axis=1, keys=['score', 'year'])
    df2.index.name = 'direcname'
    df2.reset_index(inplace=True)
    df2['direcname'] = df2['direcname'].str.replace(' ','')
    return df2
direc_1 = direc_split(direc)


def dire_bad(df):
    # 计算电影在10部以上的导演的烂片率
    df1 = df.copy()
    df1['badmovie'] = 0
    df1['badmovie'][df1['score'] < 4.3] = 1
    df2 = df1.groupby('direcname')['badmovie'].agg([np.sum, 'count'])
    df2.columns = ['badmovie', 'moviesum']
    df2 = df2[df2['moviesum'] >= 10]
    df2['bad_per'] = df2['badmovie'] / df2['moviesum']
    df2.sort_values('bad_per', ascending=False, inplace=True)
    return df2
direc_2 = dire_bad(direc_1)


def pol2(df):
    # 10部以上的导演的烂片占比图示
    plt.figure(figsize=(5,5))
    ax = plt.subplot(111, projection='polar')
    ax.set_title('导过10部以上电影导演的烂片占比')
    th = np.arange(0, 2*np.pi, 2*np.pi/5)

    ax.bar(th, df['moviesum'], color='burlywood')
    ax.bar(th, df['badmovie'], color='chocolate')
    plt.legend(['电影数量', '烂片量'], loc=(0.83, 0.9))

    for i, j in zip(th, df['bad_per']):
        plt.text(i, 10, '%.1f%%'%(j*100), color='brown')
    
    plt.thetagrids(np.arange(0, 360, 72), labels=['王晶','周伟','邓衍成','海涛','胡明凯'])
    plt.savefig('10部以上电影导演的烂片占比.jpg')
pol2(direc_2)


def year_moviesum(df):
    # 计算拥有10部以上电影的导演的2007到2017年间每年影片数量及电影平均得分
    df = df.copy().set_index('direcname')
    df1 = pd.merge(df, direc_2, left_index=True, right_index=True)
    df1 = df1[(df1['year'] >= '2007') & (df1['year'] <= '2017')]
    df1 = df1.groupby(['year', 'direcname']).agg([np.mean, 'count'])
    df1.columns=['score_mean', 'movie_year', 'badmovie', 'badmoviecount', 'moviesummean', 'moviesum', 'bad_per', 'bad_percount']
    df2 = df1[['score_mean', 'movie_year']]
    df2.reset_index('direcname', inplace=True)
    return df2

direc_3 = year_moviesum(direc_1)


def bok_sca3(df):
    # 10部以上电影导演07到17年每年电影数量和平均得分散点图
    df1 = df.copy()
    df1['size'] = df1['movie_year'] * 5
    colors = ['chocolate', 'skyblue', 'red', 'lawngreen', 'purple']
    colmark = 0
    df1['color'] = np.nan
    for i in df1['direcname'].unique():
        df1['color'][df1['direcname'] == i] = colors[colmark]
        colmark += 1

    source = ColumnDataSource(df1)
    output_file('10部以上电影导演07到17年电影得分.html')
    box = BoxAnnotation(top=4.3, fill_color='gray', fill_alpha=0.1)
    hover = HoverTool(tooltips=[('该年电影总量', '@movie_year'),
                                ('该年电影平均得分', '@score_mean')])
    p = figure(plot_width=800, plot_height=400, title='10部以上导演07到17年年电影量和均分',
               tools=[hover, 'pan, wheel_zoom, box_select, reset'])
    p.circle(x='year', y='score_mean', source=source, size='size', legend='direcname', color='color', alpha=0.6)
    p.legend.orientation = 'horizontal'
    p.legend.background_fill_alpha = 0.5
    p.add_layout(box)
    show(p)
bok_sca3(direc_3)

print('finished')
