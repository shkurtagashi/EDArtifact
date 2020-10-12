import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import base64
import json
from textwrap import dedent as d
from datetime import datetime




#EDA artifacts images examples directory
eda_low = '/Users/shkurtagashi/Desktop/Dashboard/eda_low.png' 
encoded_eda_low = base64.b64encode(open(eda_low, 'rb').read())
eda_high = '/Users/shkurtagashi/Desktop/Dashboard/eda_high.png' 
encoded_eda_high = base64.b64encode(open(eda_high, 'rb').read())
eda_rapid_change = '/Users/shkurtagashi/Desktop/Dashboard/eda_fast.png' 
encoded_eda_rapid_change = base64.b64encode(open(eda_rapid_change, 'rb').read())


#Reading an example EDA file
eda_file = pd.read_csv("/Users/shkurtagashi/Desktop/Dashboard/All_EDA_P1-RB.csv")
eda_value = eda_file.EDA_Raw
eda_time = eda_file.Time

#The css stylesheet that we are using for the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.config['suppress_callback_exceptions']=True


#Defining css colors
colors = {
    'background': '#ffffff',
    'text': '#11111'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

# Defining some text to add on the dashboard
title1 = '''
##### Artifacts examples 
'''

title2 = '''
##### Settings 
'''

title3 = '''
'''

##### Electrodermal activity for participant: X and session: Y

available_users = ["u001", "u002", "u003", "u004","u005", "u006", "u007", "u008","u009", "u010", "u011", "u012","u013", "u014", "u015", "u016"]
available_sessions = ["Day1", "Day2", "Day3"]

#Defining the main layout components
app.layout = html.Div(children=[
    html.H1(children='EDA Artifacts Labelling Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='Electrodermal Activity', value='tab-1'),
        dcc.Tab(label='Other Sensors', value='tab-2'),
    ]),
    html.Div(id='tabs-content')

])

@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])


def render_content(tab):
    if tab == 'tab-1':
        return html.Div([

    dcc.Markdown(children=title1),
    html.Div([

        html.Div([
            html.Label('EDA low'),
            html.Img(id='image1', 
                    src='data:image/png;base64,{}'.format(encoded_eda_low),
                    height="160", 
                    width="160")
        ],
        style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label('EDA high'),
            html.Img(id='image2', 
                    src='data:image/png;base64,{}'.format(encoded_eda_high),
                    height="160", 
                    width="160")
        ],style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label('EDA rapid changes'),
            html.Img(id='image3', 
                    src='data:image/png;base64,{}'.format(encoded_eda_rapid_change),
                    height="160", 
                    width="160")
        ],style={'width': '20%', 'display': 'inline-block'})
    ]),

    dcc.Markdown(children=title2),
    html.Div([

        html.Div([
            html.Label('Participant'),
            dcc.Dropdown(
                id='xaxis-column',
                options=[{'label': i, 'value': i} for i in available_users],
            )
        ],
        style={'width': '20%', 'display': 'inline-block'}),

        html.Div([
            html.Label('Session'),
            dcc.Dropdown(
                id='yaxis-column',
                options=[{'label': i, 'value': i} for i in available_sessions],
            )
        ],style={'width': '20%', 'display': 'inline-block'})
    ]),
    html.Div(
        dcc.Markdown(children=title3),
        style={
            'padding-top': 30,
            'textAlign': 'center',
            'color': colors['text']
        }),    
    dcc.Graph(
        id='basic-interactions',
        figure={
            'data': [
                {'x': eda_time, 
                'y': eda_value, 
                # 'type': 'lines+markers', 
                'name': 'EDA',
                'mode': 'lines+markers',
                'marker': {'size': 2}
                },
                # {'x': eda_time, 'y': eda_value, 'type': 'line', 'name': 'Montreal'}, #Include the filtered signal
            ],
            'layout': {
                # 'title': 'Dash Data Visualization',
                'plot_bgcolor': colors['background'],
                'paper_bgcolor': colors['background'],
                'font': {
                    'color': colors['text']
                }
            }
        }
    ),

    html.Div([
    dcc.RangeSlider(
        id='eda_signal_slider',
        min=1,
        max=20,
        step=1,
        value=[10, 15],
        updatemode='mouseup',
        included = True
    ),
    html.Div(id='output-container-range-slider')
    ]),
    dcc.Input(id='my-id', value='Type here', type='text'),
    html.Div(id='my-div'),

    html.Div([
    dcc.Markdown(d("""
        **Selection Data**

        Choose the lasso or rectangle tool in the graph's menu
        bar and then select points in the graph.
    """)),
    html.Pre(id='selected-data', style=styles['pre']),
], className='three columns')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
        ])


@app.callback(
    dash.dependencies.Output('output-container-range-slider', 'children'),
    [dash.dependencies.Input('eda_signal_slider', 'value')])

def update_output(value):
    return 'You have selected "{}"'.format(value)

@app.callback(
    Output(component_id='my-div', component_property='children'),
    [Input(component_id='my-id', component_property='value')]
)

def update_output_div(input_value):
    return 'You\'ve entered "{}"'.format(input_value)

@app.callback(
    Output('selected-data', 'children'),
    [Input('basic-interactions', 'selectedData')])

def display_selected_data(selectedData):
    return json.dumps(selectedData, indent=2)


#Define the method to filter the signal

if __name__ == '__main__':
    app.run_server(debug=True)