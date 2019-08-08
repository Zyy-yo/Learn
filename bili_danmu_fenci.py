import jieba.posseg as pseg
import pandas as pd

data = pd.read_excel(r"D:\PY\excel_file\b站弹幕.xlsx")
# 选择弹幕列，将其转为列表数据，并连接在一起
words = ''.join(data['弹幕'].tolist())
# 使用jieba分词并标注词性
cut_words = pseg.lcut(words)
# 用DataFrame封装
words_cx = pd.DataFrame(cut_words)
# 变更列名
words_cx.rename(columns={0:'词', 1:'词性'}, inplace=True)
# 筛选词性，统计该词出现的次数
def fil(x):
    cx = words_cx[words_cx['词性']== x ]
    coun = cx['词'].value_counts()
    return coun
# 导出
fil('n').to_excel(r'D:\PY\excel_file\b站弹幕词性.xlsx')
fil('a').to_excel(r'D:\PY\excel_file\b站弹幕词性a.xlsx')
'''
线上wordart.com制作词云图
import→将导出的词及其频率粘贴过来，选择csv format；
为了支持中文，在font里添加字体；
'''

