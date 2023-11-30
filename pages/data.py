# import os
# import sys

# adding parent dir to path
# parent_dir = os.path.abspath(
#     os.path.join(os.getcwd(), os.pardir))
# sys.path.append(parent_dir)

import dash
from dash import html, dcc, callback, Output, Input, dash_table
import pandas as pd
import json
from plotly import graph_objects as go

# #populating data
# populate()

# read in map_data_formatted
map_data_formatted = pd.read_csv("map_data_formatted.csv")

# read in cmap
with open('cmap.json', 'r') as f:
    cmap = json.load(f)
f.close()

column_map = {
    "datetime":"Date/ Time", "state_name":"State",
    "county_name":"County", "city_name":"City",
    "shape":"Shape", "duration_formatted":"Duration",
    "comments":"Summary"}

# filtered = map_data_formatted.loc[map_data_formatted['shape']=='disk']

############################################

# app = Dash(__name__)
dash.register_page(__name__)

# app.layout = html.Div([
layout = html.Div([
    html.Div([
        html.Div(
            children=html.B('Check out your home town!'),
            style={
                'textAlign':'center',
                'fontSize':35,
                'margin-bottom':'0.3%'
                }
        ),
        html.Div(
            children='Downloads in csv format',
            style={
                'textAlign':'center',
                'margin-bottom':'1%',
                'fontSize':18}
        )
    ]),

    html.Div([
        html.Div([
            # dcc.Label()
            html.Label('State'),
            dcc.Dropdown([
                {"label": html.Span(
                    [state], style={'font-size': 20}),
                "value": state} for state in map_data_formatted["state_name"].dropna().unique()
                ],
                value='Nevada',
                id='state-dropdown',
                placeholder='State')
            ],
            style={'display':'inline-block', 'width':'10%', 'margin-right':'1%'}
        ),
        html.Div([
            # dcc.Label()
            html.Label('County'),
            dcc.Dropdown(
                [
                {"label": html.Span(
                    [county], style={'font-size': 20}),
                "value": county} for county in map_data_formatted["county_name"].dropna().unique()
                ],
                value='Lincoln',
                id='county-dropdown',
                placeholder='County')
            ],
            style={'display':'inline-block', 'width':'10%', 'margin-right':'1%'}
        ),
        html.Div([
            # dcc.Label()
            html.Label('Cities'),
            dcc.Dropdown([
                {"label": html.Span(
                    [city], style={'font-size': 20}),
                "value": city} for city in map_data_formatted["city_name"].dropna().unique()
                ],
                value=['Rachel (highway 318)', 'Rachel'],
                multi=True,
                id='city-dropdown',
                placeholder='Cities')
            ],
            style={'display':'inline-block', 'width':'20%', 'margin-right':'1%'}
        ),
        html.Div([
            html.Label('Shapes'),
            dcc.Dropdown([
                {"label": html.Span(
                    [key], style={'color': value, 'font-size': 20}),
                "value": key}
                for key, value in cmap.items()],
                value=[],
                id='shape-dropdown',
                multi=True,
                placeholder="Shapes",)],
            style={'display':'inline-block', 'width':'35%'}
        ),
    ]),
    # html.Div(
    #         children='Exports in cvs format',
    #         style={'textAlign':'left', 'margin-top':'0.8%'}
    #     ),

    html.Div([
        dcc.Loading(children=dash_table.DataTable(
            (map_data_formatted
             .loc[
                 (map_data_formatted["state_name"]=="Nevada")&
                 (map_data_formatted["county_name"]=="Lincoln")&
                 (map_data_formatted["city_name"].isin(["Rachel (highway 318)", "Rachel"]))]
             .to_dict('records')),
            [{"name": column_map[i], "id": i} for i in [
                "datetime", "state_name", "county_name", 
                "city_name", "shape",
                "duration_formatted", "comments"
            ]],
            export_format='csv',
            export_headers='names',
            # merge_duplicate_headers=True,
            sort_action='native',
            id='table'
        ),
        fullscreen=True)],
        style={'margin-top':'1%'})
])

@callback(
    Output('county-dropdown', 'options'),
    Input('state-dropdown', 'value'))
def set_counties_options(selected_state):
    if selected_state is not None:    
        return [{'label': i, 'value': i} for i in 
            map_data_formatted.loc[
                (map_data_formatted["state_name"]==selected_state),
                "county_name"].unique()]
    elif selected_state is None:
        return [{'label': i, 'value': i} for i in 
            map_data_formatted["county_name"].unique()]

@callback(
    Output('county-dropdown', 'value'),
    Input('county-dropdown', 'value'),
    Input('county-dropdown', 'options'))
def set_county_value(selected_county, county_options):
    options_parsed = [option["value"] for option in county_options]
    if selected_county in options_parsed:
        return selected_county
    else:
        return None

@callback(
    Output('city-dropdown', 'options'),
    Input('county-dropdown', 'value'),
    Input('state-dropdown', 'value'))
def set_city_options(selected_county, selected_state):
    if (selected_county is not None) & (selected_state is not None):    
        return [{'label': i, 'value': i} for i in 
            map_data_formatted.loc[
                (map_data_formatted['county_name']==selected_county)&
                (map_data_formatted['state_name']==selected_state),
                "city_name"].unique()]
    elif (selected_county is not None) & (selected_state is None):
        return [{'label': i, 'value': i} for i in 
            map_data_formatted.loc[
                (map_data_formatted['county_name']==selected_county),
                "city_name"].unique()]
    elif (selected_county is None) & (selected_state is not None):
        return [{'label': i, 'value': i} for i in 
            map_data_formatted.loc[
                (map_data_formatted['state_name']==selected_state),
                "city_name"].unique()]
    elif (selected_county is None) & (selected_state is None):
        return [{'label': i, 'value': i} for i in 
            map_data_formatted["city_name"].unique()]
    
@callback(
    Output('city-dropdown', 'value'),
    Input('city-dropdown', 'value'),
    Input('city-dropdown', 'options'))
def set_city_values(selected_cities, city_options):
    options_parsed = [option["value"] for option in city_options]
    return [city for city in selected_cities if city in options_parsed]
    # return [city for city in selected_cities if city in [
    #     option["value"] for option in city_options]]

    
@callback(
        Output('shape-dropdown', 'options'),
        Input('state-dropdown', 'value'),
        Input('county-dropdown', 'value'),
        Input('city-dropdown', 'value'))
def set_shape_options(state_name, county_name, city_name):
    """sets the options for shape dropdown to shapes available with 
    current state, county and city selections"""
    filtered = map_data_formatted.copy()
    if state_name is not None:
        filtered = filtered.loc[
            filtered["state_name"]==state_name]
    if county_name is not None:
        filtered = filtered.loc[
            filtered["county_name"]==county_name]
    if len(city_name)>=1:
        filtered = filtered.loc[
            filtered["city_name"].isin(city_name)]
    shapes = filtered["shape"].unique()
    return [
        {"label": html.Span(
            [key], style={'color': value, 'font-size': 20}),
            "value": key}
            for key, value in cmap.items() if key in shapes]

@callback(
    Output('shape-dropdown', 'value'),
    Input('shape-dropdown', 'value'),
    Input('shape-dropdown', 'options'))
def set_shape_values(selected_shapes, shape_options):
    options_parsed = [option["value"] for option in shape_options]
    return [shape for shape in selected_shapes if shape in options_parsed]
        
@callback(
    Output('table', 'data'),
    Input('state-dropdown', 'value'),
    Input('county-dropdown', 'value'),
    Input('city-dropdown', 'value'),
    Input('shape-dropdown', 'value')

)
def filter_table(state_name, county_name, city_name, shapes):
    """filters table based on dropdown selections"""
    filtered = map_data_formatted.copy()
    if state_name is not None:
        filtered = filtered.loc[
            filtered["state_name"]==state_name]
    if county_name is not None:
        filtered = filtered.loc[
            filtered["county_name"]==county_name]
    if len(city_name)>=1:
        filtered = filtered.loc[
            filtered["city_name"].isin(city_name)]
    if len(shapes)>=1:
        filtered = filtered.loc[
            filtered["shape"].isin(shapes)]
    
    return filtered.to_dict('records')

# if __name__ == '__main__':
#     app.run_server(debug=True)

#registering page
# dash.register_page(__name__)



########### IMPORTANT ################
# Need the callbacks to handle the case where, for example:
# state, county, and city are selected
# county gets unselected
# a new county is selected, and the data goes blank because the
# old city is still selected even though it does not show up

# the mechanism is that it is still selected although no longer an option