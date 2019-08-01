import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

labels = np.array([u'推进', 'KDA', u'生存', u'团战', u'发育', u'输出'])
stats = [83, 61, 95, 67, 76, 88]
'''
画图数据准备，角度及状态值
因为要画出一个圆形，角度是相等的,用linspace
后期要连线，首尾要相连，用concatenate连接起尾部数据，必须相同维度
'''
angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
stats = np.concatenate((stats, [stats[0]]))
angles = np.concatenate((angles, [angles[0]]))
'''
先plt.figure()准备空白画板
在fig中添加子图fig.add_subplot，只需要这一个图，设置1行1列，索引位置1，polar为True，则图为圆形
ax.plot，开始画图，以‘o-’方式连接，x为angles,y为stats。也可以添加kwargs：linewidth=int，来设置线宽;
    color='green'来设置线的颜色
ax.fill，填充画好的图形，alpha为透明度。也可以添加kwarg：facecolor='green'(或其他颜色）改变填充颜色
'''
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.plot(angles, stats, 'o-', color='green')
ax.fill(angles, stats, facecolor='green', alpha=0.2)
'''
matplotlib画图无法友好显示中文字体，因此设置字体
ax.set_thetagrids设置网格的角度框线及标签
'''
font = FontProperties(fname=r'C:\Windows\Fonts\一纸情书.ttf', size=14)
ax.set_thetagrids(angles*180/np.pi, labels, FontProperties=font)
plt.show()
