import pandas as pd
import pyecharts as pe
import pyecharts_snapshot

data = pd.read_excel(r"D:\PY\excel_file\constellation_cleaned.xlsx")

# 筛选星座为白羊座的DataFrame数据
cons = data[data['星座']=='白羊座']
# 选择白羊座数据中星座和日期列的数据，转化为列表，此处二维转化，必须加.values
x = cons[['星座','日期']].values.tolist()
y = cons['健康指数'].tolist()
y2 = cons['商谈指数'].tolist()
bar = pe.Bar('白羊座运势图', height=600, width=1200)
bar.add('健康程度', x, y,
        is_more_utils=True,
        is_datazoom_show=True,
        tooltip_axispointer_type='cross',
        mark_point=['max','min'])
bar.add('商谈指数', x, y2, mark_point=['max','min'])
bar.render('D:/PY/html_file/test2.html')