import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import keras
from sklearn.preprocessing import StandardScaler

# read in the dataset
global df, df2

df = pd.read_csv('.\datasetformapping.csv')

df = df.sort_values(['Country/Region','ObservationDate'],ascending=True)
df['iso_code'] = df.apply(lambda x: 'USA' if x['Country/Region']=='US' else x['iso_code'],axis=1)

model = keras.models.load_model('.')
scaler = StandardScaler()

predicted_data = pd.read_csv('.\predicted_data.csv',index_col='ObservationDate')
realdata = pd.read_csv('.\data.csv',index_col='ObservationDate')

def add_daily():
    temp = df.copy()
    temp2 = pd.DataFrame()
    country_ls = list(set(temp['Country/Region']))
    for c in country_ls:
        a = temp[temp['Country/Region'] == c]
        a['Confirmed'] = a['Confirmed'].diff().fillna(a['Confirmed'])
        a['Recovered'] = a['Recovered'].diff().fillna(a['Recovered'])
        a['Deaths'] = a['Deaths'].diff().fillna(a['Deaths'])
        temp2 = temp2.append(a)
    return temp2

batch_size = 1

def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back - 1):
        a = dataset[i:(i+look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i+look_back,0])
    return np.array(dataX), np.array(dataY)

def future_predict(model, last_look_back_days, future_days=50):
    future_predicts = np.array([])
    dt = datetime.strptime(realdata.index[-1], '%Y-%m-%d')
    dates = np.array([])
    
    for day in range(future_days):
        dataset = scaler.fit_transform(last_look_back_days.reshape(-1,1))
        testX, testY = create_dataset(dataset, look_back=len(last_look_back_days)-2)
        testX = np.reshape(testX, (testX.shape[0], testX.shape[1], 1))
        new_predict  = model.predict(testX, batch_size=batch_size)
        new_predict = scaler.inverse_transform(new_predict)
        future_predicts = np.append(future_predicts, new_predict)
        
        dates = np.append(dates, [dt + timedelta(days=day)])
        dates[day].strftime('%m/%d/%Y')
        
        model.reset_states()
        last_look_back_days = np.delete(last_look_back_days, 0)
        last_look_back_days = np.append(last_look_back_days, new_predict)
        
    predicts = pd.DataFrame(future_predicts, index=dates)
    predicts
    return predicts

df2 = add_daily()

df = df.sort_values('ObservationDate',ascending=True)
df2 = df2.sort_values('ObservationDate',ascending=True)

# create the app object
app = dash.Dash(
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)
server = app.server

# define layout components
navbar = dbc.NavbarSimple(
    children=[

        dbc.NavItem(dbc.NavLink('GitHub',href='https://github.com/menghanzhao/COVID-dashboard')),

    ],
    brand='COVID Cases Visualization',
    brand_href='#',
    color='primary',
    dark=True,
)

radioitems = dbc.FormGroup(
    [
        dbc.Label('Choose one to view on the map'),
        dbc.RadioItems(
            options=[
                {'label':'Confirmed','value':'Confirmed'},
                {'label':'Recovered','value':'Recovered'},
                {'label':'Deaths','value':'Deaths'},
            ],
            value='Confirmed',
            id='radioitems-inputs',
        ),
    ]
)

switch = dbc.FormGroup(
    [
        dbc.Label('toggle'),
        dbc.Checklist(
            options=[
                {'label':'Cumulative','value':True},
            ],
            value=[True],
            id='switch-input',
            switch=True,
        ),
    ],
)

body = dbc.Row([
    dbc.Col([radioitems,switch],width=12),
    dbc.Col([dbc.Spinner(dcc.Graph(id='map'))], width=12)
],style={'margin':'4px'})

header = dbc.Card([
    dbc.Row([
        dbc.Col([html.H5('Predicting Cumulative Confirmed Cases in the USA from May 29, 2021 onwards')], width=12,style={'text-align':'center'}),
    ],style={'margin':'20px'})
],style={'padding':'20px','boarder':'50px'})

line_plot = dbc.Row([
    dbc.Col(dbc.Input(id='user-input-days', 
                type='number', 
                min=5, max=300, step=1, 
                placeholder='Type the number of days (between 5 to 300)',
                value=5
            ),width=3),
    dbc.Col(dcc.Graph(id='line-chart'),width=9),
])

# define the layout
app.layout = html.Div(
    [navbar,body,header,line_plot]
)

# add callback function
@app.callback(
    Output('map','figure'),
    [Input('radioitems-inputs','value'),Input('switch-input','value')],
)
def generate_figure(input1, input2):
    if len(input2) == 1:
        data = df
    else:
        data = df2
    fig = px.choropleth(data, locations="iso_code",
                    color=input1,
                    hover_name="Country/Region",
                    animation_frame="ObservationDate",
                    title = "Number of {} Cases".format(input1),                 
                    color_continuous_scale=px.colors.sequential.PuRd)
 
    fig["layout"].pop("updatemenus")
    return fig

@app.callback(
    Output('line-chart','figure'),
    [Input('user-input-days','value')],
)
def generate_prediction(input):
    predicts = future_predict(model, predicted_data.values[-100:], future_days=input)
    fig = px.line(predicts)
    return fig

if __name__=='__main__':
    app.run_server()