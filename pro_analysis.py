import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os
from scipy import stats
from sklearn.linear_model import LinearRegression

# 某公司A,B产品在2018年1,2,3月的销量数据，数据格式为xlsx

path = 'D:\\PY\\excel_file\\protri'          # 数据读取路径
savepath = 'D:\\PY\\figures\\protri_fig'      # 图片存储路径

# 1.
# 路径下有3个文件，需要创建函数批量读取
# 每读取一个文件，需要获得数据量（即多少条数据），数据字段（columns），以及缺失值数量

def du(p):
    # 批量读取数据，存储到列表返回
    l = []
    for _, _, f in os.walk(p):
        i = 0
        while i < len(f):
            df = pd.read_excel(p +'\\%s'%f[i], index_col=0)
            i += 1  
            l.append(df)
    return l

def infor():
    # 获取每个数据的数据量、字段名、缺失值数量信息
    for i in range(1, len(du(path))+1):
        data = du(path)[i-1]
        print('第%i个数据的数据量为：'%i, len(data))
        print('第%i个数据的数据字段为：'%i, list(data.columns))
        print('第%i个数据的缺失值数量为：'%i, len(data[data.isnull().values == True]))
        print('-'*5)
    # print('finished!\n')

infor()

# 2.
# 均值填充缺失数据; ‘日期’字段进行时间序列处理，转换成period
# 计算三个数据中A，B产品月总销量，绘制柱状图并存储
# 计算A产品月销量超过80%的日期

def fil():
    # 用均值填充缺失数据，对日期进行时间序列处理，存储到列表返回
    l = []
    data = du(path)
    for i in range(len(data)):
        df = data[i]
        df = df.to_period()
        for j in df.columns:
            df[j].fillna(df[j].mean(), inplace=True)
        l.append(df)
    return l

datas = fil()
print('data1:\n', datas[0], '\n')
print('data2:\n', datas[1], '\n')
print('data3:\n', datas[2], '\n')

def sale_date():
    lsale = []
    ldate = []
    for d in datas:
        # 计算A产品销量超过80%的日期，存储到列表ldate
        dc = d.copy()
        dc['A_rate'] = dc['productA'].cumsum() / dc['productA'].sum()
        date = str(dc[dc['A_rate'] >= 0.8].index[0])
        ldate.append(date)
        
        # 对数据按月做降采样并求和，计算产品A、B在1-3月的总销量，并合到一个dataframe中
        dr = d.resample('M').sum().rename(columns={'productA':'A_sale_sum', 'productB':'B_sale_sum'})
        lsale.append(dr)
    df = pd.concat(lsale)
    return [df, ldate]

print('A产品在1到3月累计超过80%销量的日期分别为：\n', sale_date()[1], '\n')

def fig1():
    # 绘图:A、B产品月总销量
    sale_df = sale_date()[0]
    chart = sale_df.plot.bar(rot=0, title='2018年1-3月A,B产品总销量柱状图')
    plt.grid(ls='--', lw=1, alpha=0.5, color='gray')
    for x, y in zip(range(3), sale_df.values[:,0]):
        plt.text(x-0.28, y, '%.2f'%y)
    for x, y in zip(range(3), sale_df.values[:,1]):
        plt.text(x, y, '%.2f'%y)
    plt.savefig(savepath + '\\pro_sale_sum.jpg')

fig1()

# 3.
# 读取数据并合并,删除缺失值；转换时间序列为period
# 做散点图观察A、B产品销量
# 做回归，预测当A销量为1200时，B产品销量值

def deal():
    # 读取数据并合并,转换时间序列为period,删除缺失值
    data = du(path)
    data_h = pd.concat(data)
    data_h = data_h.to_period()
    data_h.dropna(inplace=True)
    return data_h

datah = deal()
print('删除缺失值并合并后的数据：\n', datah)

def rel(data):
    # 对A、B产品销量数据做KS正态性检验
    ua = data['productA'].mean()
    ub = data['productB'].mean()
    stda = data['productA'].std()
    stdb = data['productB'].std()
    print('A产品数据KS正态性检验：\n',stats.kstest(data['productA'], 'norm', (ua, stda)))
    print('B产品数据KS正态性检验：\n',stats.kstest(data['productB'], 'norm', (ub, stdb)))
    # 做Pearson相关系数查看A、B产品相关性
    print('\nA、B产品相关性：\n', data.corr('pearson'))

rel(datah)

def pre_fig2():
    # 预测A产品1200时B产品销量
    dfh = deal()
    reg = LinearRegression()
    reg.fit(dfh[['productA']], dfh['productB'])
    b = reg.predict([[1200]])
    print('\nA产品销量1200时，预测B产品的销量为：%.2f'%b[0])

    # 绘图：AB产品散点图、回归拟合
    fig = plt.figure()
    plt.scatter(dfh['productA'], dfh['productB'], marker='.')
    atest = np.linspace(0,1000,1000)
    btest = reg.predict(atest[:,np.newaxis])
    plt.plot(atest, btest, 'r', lw=1)
    plt.title('A-B产品销量回归拟合')
    plt.grid(ls='--', lw=1, alpha=0.5)
    plt.savefig(savepath + '\\pro_regression.jpg')  

pre_fig2()

plt.show()

print('\nfinished!!')