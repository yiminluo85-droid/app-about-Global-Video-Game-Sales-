import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_theme()

st.title('Video Game Sales (1980-2020)')
df = pd.read_csv('vgsales.csv')


#创建按钮

#Year slider 单一年份
year = st.sidebar.slider('(Published time)',1980.0,2020.0,2000.0,1.0)

#选择区间年份还是单年份slider
option = ['seperate year','years interval']
choice = st.sidebar.radio('Choose seperate year or interval of years',option,)

#区间年份选择
form = st.sidebar.form('years_interval')
year_begain = form.text_input('year beagin',1980,help='inter a integer from 1980 to 2020')
year_end = form.text_input('year end',2020,help='inter a integer from 1980 to 2020')
form.form_submit_button('Apply')

#游戏genre选择
genre = st.sidebar.multiselect(
    'Genre of games',
    df.Genre.unique(),
    df.Genre.unique()
)


# 发行商选择（含全选/取消全选）
if 'selected_publishers' not in st.session_state:
    st.session_state['selected_publishers'] = df.Publisher.unique().tolist()
st.sidebar.subheader('Publisher of games')
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button('全选'):
        st.session_state['selected_publishers'] = df.Publisher.unique().tolist()
with col2:
    if st.button('取消全选'):
        st.session_state['selected_publishers'] = []

#公司选择
publisher = st.sidebar.multiselect(
    'publisher of games',
    df.Publisher.unique(),
    default=st.session_state['selected_publishers']
)
st.session_state['selected_publishers'] = publisher

#location select
option_location =  ['NA_Sales','EU_Sales','JP_Sales','Other_Sales','Global_Sales']
location = st.sidebar.multiselect(
   'location of buyers',
    option_location,
    option_location
)


#创建筛选对应数据:year,publisher,genre都被筛选
if choice == 'seperate year':
    df = df[(df.Year==year)&(df.Publisher.isin(publisher))&(df.Genre.isin(genre))]
else:
    df = df[(df.Year>=float(year_begain))&(df.Year<=float(year_end))&(df.Publisher.isin(publisher))&(df.Genre.isin(genre))]

#添加地点：筛选location
new_df = df[['Year','Publisher','Genre']]
for i in option_location: 
    for j in range(0,len(location)):
        if i == location[j]:
           new_df[i] = df[location[j]]


#画图

#展示(区间时间)

if choice == 'years interval':
#1.sales-years    
    st.subheader('relation between sales and years')
    fig,ax = plt.subplots(figsize=(30,20))
    sale_sum = df.groupby('Year')[location].sum()
    sale_sum.plot(ax=ax)
    st.pyplot(fig)

#per slaes by location-year
    st.subheader('relation between per sales and years')
    fig,ax = plt.subplots(len(location),1,figsize=(30,20))
    cont = 0
   
    for j in range(len(location)):
        sale_sum = df.groupby('Year')[location[j]].sum()
        ax[cont].plot(sale_sum,label=location[j])
        ax[cont].legend() 
        cont+=1
    st.pyplot(fig)
        


#展示(单独年份)    
else:
    #1.sales-location
    st.subheader('relation between sales and location')
    fig,ax = plt.subplots(figsize=(5,5))
    sale_sum = new_df[location].sum()
    sale_sum.plot.bar()
    st.pyplot(fig)

    #2.sales-publisher change to pie chart
    st.subheader('Sales Distribution by Publisher') 
    
    #one location only
    if 'Global_Sales' in location:
        location = 'Global_Sales'
    else:
        location = location[0]   
    publisher_sales = new_df.groupby('Publisher')[location].sum()     
    
    #cut the redundant data
    publisher_sales = publisher_sales[publisher_sales > 0]
    if len(publisher_sales) > 10:
        top10 = publisher_sales.nlargest(10)
        others = pd.Series([publisher_sales.iloc[10:].sum()], index=['Others'])
        publisher_sales = pd.concat([top10, others])


    fig, ax = plt.subplots(figsize=(12, 12))  
    wedges, texts, autotexts = ax.pie(
                    publisher_sales.values,
                    labels=publisher_sales.index,
                    autopct='%1.1f%%',  
                    startangle=90,
                    textprops={'fontsize': 10})
    for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
    legend_labels = [f'{idx}: {val:.2f}M' for idx, val in publisher_sales.items()]
    ax.legend(wedges, legend_labels, title='Publisher & Sales', loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
    st.pyplot(fig)
