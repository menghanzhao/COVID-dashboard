import dash
from dash import dcc
from dash import html
import plotly.express as px
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import pandas as pd
import datetime as dt
from datetime import date, datetime
import geojson

# read in the dataset
global df, df2

df = pd.read_csv(r'C:\Users\mengh\plotly dash covid app\COVID-dashboard\datasetformapping.csv')

df = df.sort_values(['Country/Region','ObservationDate'],ascending=True)
df['iso_code'] = df.apply(lambda x: 'USA' if x['Country/Region']=='US' else x['iso_code'],axis=1)

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
        dbc.NavItem(dbc.NavLink('Predictions',href='#')),
        dbc.NavItem(dbc.NavLink('GitHub',href='https://github.com/menghanzhao/COVID-dashboard')),

    ],
    brand='Map',
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

# define the layout
app.layout = html.Div(
    [navbar,body]
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

if __name__=='__main__':
    app.run_server()