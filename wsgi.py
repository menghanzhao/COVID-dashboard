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

def add_daily():
    temp = df.copy()
    temp['Confirmed'] = temp['Confirmed'].diff().fillna(temp['Confirmed'])
    temp['Recovered'] = temp['Recovered'].diff().fillna(temp['Recovered'])
    temp['Deaths'] = temp['Deaths'].diff().fillna(temp['Deaths'])

    return temp

df2 = add_daily()

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
    print(len(input2))
    fig = px.choropleth(df, locations="iso_code",
                    color=input1,
                    hover_name="Country/Region",
                    animation_frame="ObservationDate",
                    title = "Number of {} Cases".format(input1),                 
                    color_continuous_scale=px.colors.sequential.PuRd)
 
    fig["layout"].pop("updatemenus")
    return fig

if __name__=='__main__':
    app.run_server()