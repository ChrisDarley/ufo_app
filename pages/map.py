import os
import sys

# adding parent dir to path
# parent_dir = os.path.abspath(
#     os.path.join(os.getcwd(), os.pardir))
# sys.path.append(parent_dir)

import dash
from dash import Dash, html, dcc, callback, Output, Input
from populate_data import populate
from plotly import graph_objects as go
import pickle
import json
from dash import dcc, html, Dash, dash_table
import pandas as pd
import numpy as np
# from functools import partial

# # ensure all data is populated
# populate()

# read in cmap
# with open(os.path.join(parent_dir,'cmap.json'), 'r') as f:
#     cmap = json.load(f)
# f.close()
with open('cmap.json', 'r') as f:
    cmap = json.load(f)
f.close()

# read in map_data_formatted
map_data_formatted = pd.read_csv(
    "map_data_formatted.csv",
    index_col='datetime', parse_dates=True)
    # "map_data_formatted.csv", index_col='datetime', parse_dates=True)

map_data_formatted = map_data_formatted.assign(color=lambda df_:
    df_["shape"].map(cmap))

# read in the pickled plotly figure object
with open('fig_dict_object.pkl', 'rb') as f:
    fig_dict_unfiltered = pickle.load(f)
f.close()

# app = Dash(__name__)
dash.register_page(__name__, path='/')

# app.layout = html.Div([
layout = html.Div([
    html.Div([
        html.H1(
            children='Historical Map of UFO Sightings',
            style={'textAlign':'center'}
        )
    ]),
    dcc.Loading(children=dcc.Graph(id='map')),
    html.Div([
        html.Div([
            html.Label('Optional: Select State(s)', htmlFor='selected_states'),
            dcc.Dropdown(
                sorted(map_data_formatted["state_name"].unique()),
                value=[],
                id='selected_states',
                multi=True
            )],
            style={'margin-left':'6.5%', 'margin-right':'1.5%',
                'width':'20%', 'display':'inline-block'}),
        html.Div([
            html.Label('Optional:   Select Duration (minutes)'),
            dcc.RangeSlider(
                0,60,1,
                marks={i:{"label":str(i)} for i in [
                    0,1,2,3,4,5,6,7,8,9,10,20,30,40,50,60]},
                value=[0,60],
                pushable=1,
                tooltip={"placement": "bottom", "always_visible": True},
                id='duration_interval')
            ],
            style={'margin-left':'1.5%', 'margin-right':'2%',
                'width':'63.5%', 'display':'inline-block'}),
        ],
        style={'margin-top':'20px', 'margin-bottom':'40px'}
    ),
    html.Div([
        html.Div([html.Label(
            'Tips')], style={'margin-bottom':'5px'}),
        html.Div([html.Label(
            """1) Hover mouse over data points for description"""
        )]),
        html.Div([html.Label(
            """2) Double click legend shapes to isolate \
            and single click legend shapes to toggle"""
            )]),
        # html.Div([html.Label(
        #     """3) State and Duration updates will take effect after \
        #     slider reaches or is dragged to final year and Play button \
        #     is pressed again"""
        #     )]),
        # html.Div([html.Label(
        #     """4) Hover mouse above legend and click house button to \
        #     reset the map's zoom level"""
        # )]),

        ],
        style={'margin-top':'20px', 'margin-left':'6.5%'}
    ),
])

@callback(
    Output(component_id='map', component_property='figure'),
    Input(component_id='selected_states', component_property='value'),
    Input(component_id='duration_interval', component_property='value')

)
def create_map(selected_states, duration_interval):

    if selected_states == []:
        # selected_states = map_data_formatted["state_name"].unique()
        selected_states = map_data_formatted["state_name"].unique()

    years = map_data_formatted.index.year.unique()
    shapes = list(map_data_formatted["shape"].dropna().unique())
    # fig_dict_filtered = fig_dict_unfiltered
    
    frames = []
    # totals = []
    # totals_2 = []
    for year in years:
        dataset_by_year = map_data_formatted.loc[
            map_data_formatted.index.year==year]
        frame = {"data": [], "name":str(year)}
        for shape in shapes:
            dataset_by_year_and_shape = dataset_by_year.loc[
                dataset_by_year["shape"]==shape]

            # # here i want to lock on to my selection based on duration ### AND state_name
            filtered = dataset_by_year_and_shape.loc[
                (dataset_by_year_and_shape["duration_seconds"]/60).ge(
                    duration_interval[0])&
                (dataset_by_year_and_shape["duration_seconds"]/60).le(
                    duration_interval[1])&
                (dataset_by_year_and_shape["state_name"].isin(
                    selected_states))
            ]

            # print(f'loc operation time: {end-start}')
            if len(filtered)>=1:
                trace = go.Scattermapbox(
                    lat=filtered["latitude"],
                    lon=filtered["longitude"],
                    customdata=np.stack(
                        (
                        filtered["shape"],
                        filtered["duration_formatted"],
                        filtered["state_name"],
                        filtered["county_name"],
                        filtered["city_name"],
                        filtered.index.year,
                        filtered['duration_seconds']
                        ),
                        axis=1),
                    mode="markers",
                    marker={'color':filtered['color']},
                    name=shape,
                    hovertemplate=
                    'Shape: %{customdata[0]}<br>'+
                    'Duration: %{customdata[1]}<br>'+
                    'State: %{customdata[2]}<br>'+
                    'County: %{customdata[3]}<br>'
                    'City: %{customdata[4]}<br>'+
                    'Year: %{customdata[5]}'+
                    '<extra></extra>')
            else:
                trace = go.Scattermapbox(
                    lon=[0],
                    lat=[90],
                    mode="markers",
                    marker={'color':cmap[shape]},
                    name=shape,
                )

            frame["data"].append(trace)
        frames.append(frame)
    
    fig_dict_copy = fig_dict_unfiltered.copy()
    fig_dict_copy["frames"] = frames
    fig_dict_copy["data"] = frames[-1]["data"]
    fig_dict_copy["layout"]["sliders"][0]["active"] = len(
        fig_dict_copy["frames"])-1
    # fig = go.Figure(fig_dict_copy)


    return go.Figure(fig_dict_copy)

