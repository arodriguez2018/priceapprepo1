import pandas as pd
from pandas_datareader.data import DataReader
#import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import urllib3

import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
import plotly.express as px
import datetime as dt
import pydeck as pdk
import base64

# INLINE CSS
# EITHER THIS OR THE ACUTAL MARKDOWN BUT NOT BOTH,WAIT AND FIGURE
st.markdown(
"""
 <style type='text/css'>

    body {
        background-color:white;
        font-family: arial;
   }

    h1 {
        color:gray;
        font-family: arial;
    }
</style>
""", unsafe_allow_html=True)

# INTRO PARAGRAPH
st.markdown(
"""

# NATURAL GAS AND OIL PRICES
#### Created by Arthur Rodriguez on 2020-05-24 for Educational Purposes Only
<ul>
    <li>Historical Data: U.S. Energy Information Administration, Henry Hub Natural Gas Spot Price [DHHNGSP], retrieved from FRED, Federal Reserve Bank of St. Louis; https://fred.stlouisfed.org/series/DHHNGSP, May 24, 2020.</li>
    <li>Futures Data: https://www.cmegroup.com/trading/energy/natural-gas/natural-gas.html</li>
    <li><a href="https://www.linkedin.com/in/1artrodriguez/" target="_blank"</a>My LinkedIn</li>
</ul>


---

""", unsafe_allow_html=True)

series_code1 = 'DHHNGSP'
series_code2 = 'DCOILWTICO'
data_source = 'fred'
start = dt.date(2015, 1,1)
ng_data = DataReader(series_code1, data_source, start)
oil_data = DataReader(series_code2, data_source, start)



both = pd.concat([ng_data, oil_data], axis=1).fillna(method='ffill')

wtiFutC = 'https://www.cmegroup.com/trading/energy/natural-gas/natural-gas.html'
http = urllib3.PoolManager()
response2 = http.request('GET', wtiFutC)
soup2 = BeautifulSoup(response2.data.decode('utf-8'), features='html.parser')

r = requests.get('https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/444/G?quoteCodes=null&_=1590283610945').json()
last_quotes_g = [(item['expirationDate'], item['priorSettle']) for item in r['quotes']]
futures_g = pd.DataFrame((tuple(t) for t in last_quotes_g))
futures_g.rename(columns={0:'Dateraw', 1:'Price'}, inplace=True)
futures_g['Date'] = pd.to_datetime(futures_g['Dateraw'])
futures_g['Price'] = pd.to_numeric(futures_g['Price'])
futures_g.set_index('Date', inplace=True)
del futures_g['Dateraw']
futures_g5 = futures_g[:59]
bothg = both[['DHHNGSP']]
gasplot = pd.concat([bothg, futures_g5], axis=1)
gp1 = gasplot.copy()
#st.write(gp1)

gp2 = gp1.rename(columns={'DHHNGSP':'Historic', 'Price':'Futures'}).reset_index().melt(id_vars='index')

fig2 = px.line(gp2,x='index', y='value', 
        color='variable', title="Natural Gas",
        width=800, height=600, #original 800 and 600
        labels={ # replaces default labels by column name
                "variable": "Type",  "index": "Date", "value": "Gas Price ($/MMBTU)"
            },template="simple_white",
            color_discrete_sequence=["red", "black"],
            
            )

fig2.update_layout(
    xaxis=dict(showgrid=True, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=True))

fig2.update_yaxes(range=[0.00, 5.00],
    tickprefix="$")#, yaxis_tickformat = '%')

fig2.update_layout(yaxis_tickformat = '.3s')


fig2.update_traces(mode='lines+markers',
marker=dict(
            size=4,
            )
            )

        
st.plotly_chart(fig2)


wtiFutC = 'https://www.cmegroup.com/trading/energy/crude-oil/west-texas-intermediate-wti-crude-oil-calendar-swap-futures_quotes_globex.html'
http = urllib3.PoolManager()
response2 = http.request('GET', wtiFutC)
soup2 = BeautifulSoup(response2.data.decode('utf-8'), features='html.parser')

r = requests.get('https://www.cmegroup.com/CmeWS/mvc/Quotes/Future/4707/G?quoteCodes=null&_=1560171518204').json()
last_quotes_o = [(item['expirationDate'], item['priorSettle']) for item in r['quotes']]
futures_o = pd.DataFrame((tuple(t) for t in last_quotes_o))

futures_o.rename(columns={0:'Dateraw', 1:'Price'}, inplace=True)
futures_o['Date'] = pd.to_datetime(futures_o['Dateraw'])
futures_o['Price'] = pd.to_numeric(futures_o['Price'])
futures_o.set_index('Date', inplace=True)
del futures_o['Dateraw']

futures_o5 = futures_o[1:59]
botho = both[['DCOILWTICO']]
oilplot = pd.concat([botho, futures_o5], axis=1)
op1 = oilplot.copy()
#st.write(op1)
op2 = op1.rename(columns={'DCOILWTICO':'Historic', 'Price':'Futures'}).reset_index().melt(id_vars='index')
fig2o = px.line(op2,x='index', y='value', 
        color='variable', title="Oil",
        width=800, height=600,
        labels={ # replaces default labels by column name
                "variable": "Type",  "index": "Date", "value": "Oil Price ($/BBL)"
            },template="simple_white",
            color_discrete_sequence=["green", "black"],
            
            )

fig2o.update_layout(
    xaxis=dict(showgrid=True, zeroline=False),
    yaxis=dict(showgrid=True, zeroline=True))

fig2o.update_yaxes(range=[0.00, 100],
    tickprefix="$")#, yaxis_tickformat = '%')

fig2o.update_layout(yaxis_tickformat = '.4s')


fig2o.update_traces(mode='lines+markers',
marker=dict(
            size=4,
            )
            )

        
st.plotly_chart(fig2o)

allt=pd.concat([op2, gp2], keys=['oil','gas']).reset_index().drop(columns='level_1').rename(columns={'level_0':'Product', 'index':'Date', 'variable':'Type', 'value':'Price'})
#st.write(allt)

# ACTUALLY, UNSTACK AND THEN OUTPUT
csv = allt.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()
href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
st.markdown(href, unsafe_allow_html=True)

