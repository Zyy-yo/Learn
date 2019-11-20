import numpy as np 
import pandas as pd 
import matplotlib.pyplot as plt 
import os 

os.chdir(r'D:\PY\figures\pro_wealth')


'''
一个财富分配游戏：
房间里有100个人，每人都有100元钱，他们在玩一个游戏。每轮游戏中，每个人都要拿出一元钱随机给另一个人，最后这100个人的财富分布是怎样的？
财富为0时，可以不支付，但能够获得
'''


'''
方法一，直接用数组循环绘图
'''


# # def fig(data, t):
# #     values = np.sort(data.copy())
# #     plt.figure(figsize=(8,5))
# #     plt.bar(np.arange(1,101), values, color='hotpink')
# #     plt.ylim([0, 500])
# #     plt.title('round%i'%t)
# #     plt.savefig('财富分配模拟round%i'%t)
# #     plt.close()

# def assi():
#     money = np.array([100]*100)      # 100个人，每个人初始金钱100元
#     ran = range(0,100)               # 数组下标，模拟人
#     times = range(1, 17001)          # 每天一次，一共玩17000次，模拟游戏次数
#     for t in times:
#         if t == 1:
#             # fig(money, t-1)
#             pass
#         for i in ran:                   # 这100个人中循环一次表示一轮游戏
#             if money[i] == 0:            # 当身上0元时，不需要给别人1元，但可以接受
#                 continue
#             money[i] -= 1               # 轮到的人给出1元
#             j = i
#             while j == i:
#                 j = np.random.choice(ran)   # 随机选择另外一个人（非自身）
#             money[j] += 1                    # 另外一个人得到1元
#         # if t <= 100:
#         #     if t % 10 == 0:
#         #         fig(money, t)
#         # elif t > 100 and t <= 2000:
#         #     if t % 100 == 0:
#         #         fig(money, t)
#         # else:
#         #     if t % 500 == 0:
#         #         fig(money, t)
#     return money
# moneyfinal = assi()  

# sortdata = np.sort(moneyfinal)
# df = pd.DataFrame(sortdata, columns=['money'])
# df.sort_values('money', ascending=False, inplace=True)
# df['cumsum'] = df['money'].cumsum()
# df['cumper'] = df['cumsum'] / df['money'].sum()

# plt.bar(np.arange(1,101), df['money'], color='hotpink')

# x = df[df['cumper']>0.8].index[0]
# v = df[df['cumper']>0.8]['cumper'].values[0]
# length = len(df[df['cumper']>0.8]) / len(df)

# plt.axvline(x, linestyle='--', alpha=0.5)
# plt.text(x+2, 200, '%.2f%%的人累计财富达到%.2f%%'%(length*100, v*100))

# v2 = len(df[df['money'] < 100]) / len(df)

# plt.axhline(100, linestyle='--', alpha=0.5)
# plt.text(60, 80, '%.2f%%的人财富在100元以下'%(v2*100))
# plt.savefig('17000轮游戏后财富分配.jpg')
# print('17000轮游戏后，财富最多的玩家拥有%i元'%df['money'].max())

'''
允许借贷时，财富分布是如何呢？
财富为0时，仍然支付
'''

plt.rcParams['axes.unicode_minus']=False

# def fig(data, t):
#     values = np.sort(data.copy())
#     plt.figure(figsize=(8,5))
#     plt.bar(np.arange(1,101), values, color='hotpink')
#     plt.ylim([-400, 500])
#     plt.title('round%i'%t)
#     plt.savefig('财富分配模拟round%i'%t)
#     plt.close()

# def assi():
#     money = np.array([100]*100)      # 100个人，每个人初始金钱100元
#     ran = range(0,100)               # 数组下标，模拟人
#     times = range(1, 17001)          # 每天一次，一共玩17000次，模拟游戏次数
#     for t in times:
#         if t == 1:
#             fig(money, t-1)
#             pass
#         for i in ran:                   # 这100个人中循环一次表示一轮游戏
#             money[i] -= 1               # 轮到的人给出1元
#             j = i
#             while j == i:
#                 j = np.random.choice(ran)   # 随机选择另外一个人（非自身）
#             money[j] += 1                    # 另外一个人得到1元
#         if t <= 100:
#             if t % 10 == 0:
#                 fig(money, t)
#         elif t > 100 and t <= 2000:
#             if t % 100 == 0:
#                 fig(money, t)
#         else:
#             if t % 500 == 0:
#                 fig(money, t)
#     return money
# moneyfinal = assi()  

# sortdata = np.sort(moneyfinal)
# df = pd.DataFrame(sortdata, columns=['money'])
# df.sort_values('money', ascending=False, inplace=True)
# df['cumsum'] = df['money'].cumsum()
# df['cumper'] = df['cumsum'] / df['money'].sum()

# plt.bar(np.arange(1,101), df['money'], color='hotpink')

# x = df[df['cumper']>0.8].index[0]                             # 累积财富达到80%
# v = df[df['cumper']>0.8]['cumper'].values[0]
# length = len(df[df['cumper']>0.8]) / len(df)

# plt.axvline(x, linestyle='--', alpha=0.5, lw=1)
# plt.text(20, 200, '%.2f%%的人掌握了%.2f%%的财富'%(length*100, v*100))


# v1 = df['cumper'].loc[80]                                  # 20%的人掌握了多少财富
# plt.axvline(20, linestyle='--', alpha=0.5, lw=1)
# plt.text(0, -50, '20%%的人掌握了%.2f%%的财富'%(v1*100))
# # print(v1)

# v2 = len(df[df['money'] < 100]) / len(df)                    # 100元以下人数占比

# plt.axhline(100, linestyle='--', alpha=0.5, lw=1)
# plt.text(65, 70, '%.2f%%的人财富在100元以下'%(v2*100))

# v3 = len(df[df['money'] < 0]) / len(df)           # 负债人数占比
# plt.text(70, -100, '%.2f%%的人负债'%(v3*100))

# plt.savefig('17000轮游戏后财富分配.jpg')


# print('17000轮游戏后，财富最多的玩家拥有%i元'%df['money'].max())
# print('17000轮游戏后，财富最少的玩家负债%i元'%df['money'].min())


# a = np.array([1,3,5,7,8,10,22,34])
# df = pd.DataFrame(a, columns=['v'])
# df.sort_values('v', ascending=False, inplace=True)
# df['cumsum'] = df['v'].cumsum()
# df['per'] = df['cumsum'] / df['v'].sum()
# print(df[df['per'] > 0.8]['per'].values[0])
# print(df['per'].loc[5])
# print(df)

'''
方法二，利用数组，循环存储为dataframe；再循环绘图
'''

# def wealth_data():
#     money = np.array([100] * 100)       # 初始金钱
#     moneyc = money.copy()
#     person = range(0, 100)              # 模拟人，100个人编号从0到99
#     times = range(1, 17001)                # 游戏次数
#     dfall = pd.DataFrame(money)         # 初始数据

#     for t in times:
#         for p in person:                # 一轮游戏，100个人都要玩一次
#             # if moneyc[p] == 0:          # 0元时无需支付
#             #     continue
#             moneyc[p] -= 1
#             p2 = p
#             while p2 == p:              # 随机选择其他玩家（不包含自己），支付1元
#                 p2 = np.random.choice(person)
#             moneyc[p2] += 1
#         df = pd.DataFrame(moneyc, columns=[t])     # 一轮游戏结束后的财富数据
#         dfall = pd.concat([dfall, df], axis=1)       # 合并每轮财富数据
#     return dfall

# data = wealth_data()

# def figbar(df, start, end, step):
#     for i in range(start, end, step):
#         dfi = df[i].sort_values()
#         plt.figure()
#         plt.bar(range(0,100), dfi.values, color='red', alpha=0.5)
#         plt.title('round%i'%i)
#         plt.ylim([-300, 500])
#         plt.savefig('财富分配模拟%i'%i)
#         plt.close()
# figbar(data, 0, 100, 10)       # 100轮以内，每10轮绘制一次
# figbar(data, 100, 2000, 100)   # 2000轮以内，每100轮绘制一次
# figbar(data, 2000, 17001, 500)   # 2000轮以后，每500轮绘制一次


'''
方法三，直接用dataframe来做，循环出数据（速度慢）
'''

# def game(data, round):
#     # 每轮游戏财富分配
#     if len(data[data[round-1] == 0]) > 0:                            # 当有财富值为0的玩家时                               
#         pay = pd.DataFrame({'pre_round': data[round-1], 'lost': 0})
#         con = pay['pre_round'] > 0
#         pay['lost'][con] = 1                                  # 只有财富值>0的玩家失去1元
#         choice_r = pd.Series(np.random.choice(person, len(pay[con])))     # 相应的，获得1元的玩家个数=财富值>0的玩家个数    
#         gain = pd.DataFrame({'gain':choice_r.value_counts()})                    # 汇总盈利玩家数据
#         round1 = pay.join(gain)                                            # 合并一轮游戏的支付与收入数据        
#         round1.fillna(0, inplace=True)                                      # 未得到1元的空值填充为0       
#         return round1['pre_round'] - round1['lost'] + round1['gain']        # 返回一轮游戏结束后的财富值
#     else:                                                                    # 当没有人财富值为0时，所有人都参与游戏
#         pay = pd.DataFrame({'pre_round': data[round-1], 'lost': 1})               
#         choice_r = pd.Series(np.random.choice(person, 100))           # 每轮游戏，从100个人里随机进行100次选择，(id被选择表示获得1元，多次被选择就多次获得1元)           
#         gain = pd.DataFrame({'gain':choice_r.value_counts()})           
#         round1 = pay.join(gain)               
#         round1.fillna(0, inplace=True)
#         return round1['pre_round'] - round1['lost'] + round1['gain']  

# # 100个人的编号
# person =[x for x in range(1,101)]
# # 初始数据
# origin = pd.DataFrame([100 for i in range(100)], index=person)        
# origin.index.name = 'id'
# for t in range(1, 17001):
#     # 一共17000轮游戏
#     origin[t] = game(origin, t)  



'''
玩家从18岁开始，在经过17年后为35岁，这个期间共进行游戏6200次左右，则此刻查看财富情况，将财富值为负的标记成“破产”，
通过图表研究该类玩家在今后的游戏中能否成功“逆袭”（财富值从负到正为逆袭）
'''

'''
根据方法二的data来完成绘图
'''

# # 找出6200轮资产为负玩家的id
# round6200 = pd.DataFrame({'money': data[6200],
#                           'id': data[6200].index})
# id_pc = round6200['id'][round6200['money'] < 0].tolist()

# # 绘图
# def figbar_after6200(df, start, end, step):
#     for i in range(start, end, step):
#         dfi = pd.DataFrame({'money': df[i],
#                             'color': 'gray'})
#         dfi['color'].loc[id_pc] = 'red'
#         dfi.sort_values('money', inplace=True)                  
#         plt.figure()
#         plt.bar(range(0,100), dfi['money'], color=dfi['color'], alpha=0.6)
#         plt.title('round%i'%i)
#         plt.ylim([-300, 500])
#         plt.savefig('逆袭模拟%i'%i)
#         plt.close()
# figbar_after6200(data, 6200, 17001, 400)       # 6200轮资产为负的玩家在之后是否可以逆袭图

# print(round6200)


'''
努力的人生会更好吗？
模型假设：
① 每个人初始基金仍为100元
② 一共玩17000轮
③ 每天拿出一元钱，并且随机分配给另一个人
④ 有10个人加倍努力，从而获得了1%的竞争优势
⑤ 允许借贷
'''

'''
根据方法三的方法改写
'''
# # 10个人的概率为0.0101，余下90个人的概率为(1 - 10 * 0.0101)/ 90
# probability = [0.899/90 for i in range(100)]
# for i in [10, 23, 18, 68, 29, 54, 91, 77, 82, 35]:     
#     probability[i-1] = 0.0101


# def game_struggle(data, round):
#     pay = pd.DataFrame({'pre_round': data[round-1], 'lost': 1})               
#     choice_r = pd.Series(np.random.choice(person, 100, p=probability))     # 指定概率 
#     gain = pd.DataFrame({'gain':choice_r.value_counts()})           
#     round1 = pay.join(gain)               
#     round1.fillna(0, inplace=True)
#     return round1['pre_round'] - round1['lost'] + round1['gain']  

# # 100个人的编号
# person =[x for x in range(1,101)]
# # 初始数据
# origin = pd.DataFrame([100 for i in range(100)], index=person)        
# origin.index.name = 'id'
# for t in range(1, 17001):
#     origin[t] = game_struggle(origin, t)  

# 绘图
# def figbar_struggle(df, start, end, step):
#     for i in range(start, end, step):
#         dfi = pd.DataFrame({'money': df[i],
#                             'color': 'gray'})
#         dfi['color'].loc[[10, 23, 18, 68, 29, 54, 91, 77, 82, 35]] = 'red'
#         dfi = dfi.sort_values('money').reset_index()                  
#         plt.figure()
#         plt.bar(dfi.index, dfi['money'], color=dfi['color'], alpha=0.6)
#         plt.title('round%i'%i)
#         plt.ylim([-300, 500])
#         plt.savefig('努力人生模拟%i'%i)
#         plt.close()
# figbar_struggle(origin, 0, 100, 10)       # 100轮以内，每10轮绘制一次
# figbar_struggle(origin, 100, 2000, 100)   # 2000轮以内，每100轮绘制一次
# figbar_struggle(origin, 2000, 17001, 500)   # 2000轮以后，每500轮绘制一次


'''
标准差的变化
'''
# game_std = origin.std()
# game_std.plot(figsize=(8,6), color='r', lw=1)
# plt.grid(linestyle='--', color='gray', alpha=0.4)
# plt.savefig('财富差距变化.jpg')