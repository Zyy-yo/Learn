import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt
import os 
import time
import re
import warnings
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split, KFold
from sklearn.preprocessing import StandardScaler, PowerTransformer, PolynomialFeatures
from sklearn.linear_model import LassoCV, LinearRegression, RidgeCV
from xgboost import XGBRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import pickle



'''
上海租房租金预测，预测租房每平米每月租金

读取初步清洗后的数据222243条，做进一步处理：
    户型及公交车站分割后的空值不好填充，直接删除；
    上海周边数据量很小，删除上海周边数据，让房源数据统一在上海市；
    关联更多空间特征：500米、1000米、2000米范围内的地铁站/公交站/三甲医院/小学/中学/幼儿园数量
    将地铁线路制作为哑变量，使模型更准确
    制作因变量————每平米每月租金
    对因变量的离群值进行处理，删除离群值
    
模型训练和预测：
    尝试了线性回归模型，lasso回归模型，ridge回归模型，xgboost模型；尝试CART回归树以及随机森林模型时，长时间运行无结果，这里直接pass。
    线性回归模型评价并不好，pass掉
    lasso回归当alpha取值在0.01-0.1之间，mape在0.196，r2_score在0.57，mae在16.44，相比其他取值效果较好
    ridge回归当alpha取值在0.1-10之间，和lasso回归的结果类似，mape在0.19，r2_score在0.57，mae在16.43，相比其他取值效果较好
    因此我觉得在lasso回归和ridge回归中，选择ridge回归更好，lasso回归模型pass掉。然而该模型的效果还是不如人意。
    xgboost模型做回归任务，经过调参，当子学习器在800，学习步长0.2，最大深度11时，mae在6.63，r2_score在0.87，mape在0.079，模型效果不错。
    最终利用ridge模型对数据集进行集成学习，再重新使用xgboost模型进行预测，模型评价mae在6.46，r2_score在0.87，mape在0.077。
'''

def outliers(s):
    '''
    定义离群值
    '''
    q1 = s.quantile(0.25)
    q3 = s.quantile(0.75)
    up = q3 + 1.5 * (q3 - q1)
    low = q1 - 1.5 * (q3 - q1)
    return (up, low)

def pipe_ridgef():
    # ridge回归
    pipe_rm = Pipeline([
        ('pt', PowerTransformer()),
        ('sc', StandardScaler()),
        ('pol', PolynomialFeatures()),
        ('ridge', RidgeCV(alphas=list(np.arange(1, 10) * 0.1) + list(np.arange(1, 10)), cv=cv))
    ])
    return pipe_rm

def pipe_xgbf():
    # xgboost模型
    xgb_m = XGBRegressor(objective='reg:squarederror', booster='gbtree', n_estimators=800,
                         n_jobs=-1, max_depth=11, learning_rate=0.2, subsample=0.8, 
                         colsample_bytree=0.8, random_state=1)

    pipe_xgbm = Pipeline([
        ('pt', PowerTransformer()),
        ('sc', StandardScaler()),
        ('xgb', xgb_m)
    ])     
    return pipe_xgbm


def mape_f(ytruedata, ypredata):
    # 计算mape
    y_data = pd.DataFrame(ytruedata.copy())
    y_data['ypre'] = ypredata
    y_data['y_ypre'] = abs(y_data['y'] - y_data['ypre']) / y_data['y']
    return np.mean(y_data['y_ypre'])


def save_model(filename, model):
    # 保存模型文件
    path = os.path.abspath('./model')
    f = open(path + '\\' + filename + '.pkl', 'wb')
    joblib.dump({'model_name': filename,
                 'features': features,
                 'model': model,
                 'data': [xtrain, ytrain, xtest, ytest]}, f)
    f.close()



if __name__ == '__main__':

    warnings.filterwarnings('ignore')
    os.chdir(r'D:\工作\数据分析\微专业\项目数据\练习10_住宅租金预测')

    # pd.set_option('display.max_columns', None)
    df = pd.read_csv('data_cleaned.csv')

    # 以下字段缺失值不好填充，直接删除
    df2 = df.dropna(subset=['rooms', 'halls', 'sub_line', 'sub_station', 'sub_distance']).reset_index(drop=True)
    # 删除上海以外数据
    df3 = df2.loc[df2['区域'] != '上海周边'].copy()
    # 读取周边poi数据
    locdata = pd.read_excel('loc_data.xlsx')
    # 合并数据
    data = pd.merge(df3, locdata, on='address')
    # 去除不需要的特征
    data_final = data.copy().drop(columns=['区域', 'address', 'lng', 'lat', 'lease_mode', 'sub_station'])  
        # 合租的部分样本房源面积是总面积，合租样本每平米租金的计算可能不准确，在去除缺失值后，样本只余下整租样本，因此这里不需要再对租赁方式做处理

    # 制作哑变量
    data_final = pd.get_dummies(data_final, columns=['sub_line'])   
    # 制作因变量：每平米租金
    data_final['y'] = data_final['rent_month'] / data_final['area']  

    # 查看分布
    data_final[['y']].boxplot()
    # plt.show()
    # 删除离群值
    data_final = data_final.loc[(data_final['y'] < outliers(data_final['y'])[0]) & (data_final['y'] > outliers(data_final['y'])[1])]
    # 查看删除离群值后的分布
    data_final['y'].plot.hist()
    # plt.show()

    # 去除不需要的特征，保存模型所用数据
    data_m = data_final.copy().drop(columns=['rent_month'])
    data_m.to_csv('model_data.csv')


    '''样本量153075'''


    # 分割训练集和测试集
    train, test = train_test_split(data_m, test_size=0.3, random_state=1)

    # 提取自变量和因变量
    xtrain = train.copy().drop(columns=['y'])
    ytrain = train.copy()['y']
    xtest = test.copy().drop(columns=['y'])
    ytest = test.copy()['y']

    # 保存自变量名称
    features = xtrain.columns.tolist()

    
    # ridge回归
    cv = KFold(n_splits=3, shuffle=True, random_state=2)

    pipe_ridge = pipe_ridgef()
    pipe_ridge.fit(xtrain, ytrain)
    ypre_r = pipe_ridge.predict(xtest)

    # ridge模型评价
    print('ridge模型 mae：', mean_absolute_error(ytest, ypre_r))
    print('ridge模型 r方：', r2_score(ytest, ypre_r))
    print('ridge模型 mape:', mape_f(ytest, ypre_r))

    # 保存ridge模型
    save_model('ridge_model', pipe_ridge)


    # xgboost模型
    xgb_st = time.time()
    pipe_xgb = pipe_xgbf()             
    pipe_xgb.fit(xtrain, ytrain)
    ypre_x = pipe_xgb.predict(xtest)

    # xgboost模型评价
    print('xgboost模型 mae：', mean_absolute_error(ytest, ypre_x))
    print('xgboost模型 r方：', r2_score(ytest, ypre_x))
    print('xgboost模型 mape:', mape_f(ytest, ypre_x))
    xgb_et = time.time()
    print('xgboost模型用时：%.2fs'%(xgb_et - xgb_st))

    # 保存xgboost模型
    save_model('xgb_model', pipe_xgb)
   

    # xgboost模型优化
    # 使用ridge模型进行集成学习
    train['ensemble_ridge'] = pipe_ridge.predict(train.loc[:,features])
    test['ensemble_ridge'] = pipe_ridge.predict(test.loc[:,features])
    # 提取新的自变量和因变量
    xtrain_rx = train.copy().drop(columns=['y'])
    ytrain_rx = train.copy()['y']
    xtest_rx = test.copy().drop(columns=['y'])
    ytest_rx = test.copy()['y']

    xgbo_st = time.time()
    pipe_xgb.fit(xtrain_rx, ytrain_rx)
    ypre_rx = pipe_xgb.predict(xtest_rx)

    print('xgboost优化 mae：', mean_absolute_error(ytest_rx, ypre_rx))
    print('xgboost优化 r方：', r2_score(ytest_rx, ypre_rx))
    print('xgboost优化 mape:', mape_f(ytest_rx, ypre_rx))
    xgbo_et = time.time()
    print('xgboost优化模型用时：%.2fs'%(xgbo_et - xgbo_st))
    
    # 保存xgboost优化模型
    save_model('xgb_ensembleridge_model', pipe_xgb)