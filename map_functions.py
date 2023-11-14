from plotly import graph_objects as go
import pandas as pd
import numpy as np
from plotly.colors import qualitative as qual
import pickle
import json 

def create_cmap():
    """create color map used for shapes and labels"""
    # read in data
    map_data_formatted = pd.read_csv(
        "map_data_formatted.csv",
        index_col='datetime',
        parse_dates=True)

    # create a color map from the shape column
    cmap = {}
    for i in range(map_data_formatted["shape"].dropna().nunique()):
        cmap.update(
            {map_data_formatted["shape"].dropna().unique()[i]:qual.Dark24[i]})
        
    with open("cmap.json", "w") as f:
        json.dump(obj=cmap, fp=f)
    f.close()


def create_map_object():
    """create and pickle the plotly figure object of the unfiltered map"""

    # read in data
    map_data_formatted = pd.read_csv(
        "map_data_formatted.csv",
        index_col='datetime',
        parse_dates=True)

    # read in the color map json object to a dictionary
    with open("cmap.json", "r") as f:
        cmap = json.load(f)
    f.close()

    # adding the color column to map_data_formatted
    map_data_formatted = map_data_formatted.assign(color=lambda df_: 
        df_["shape"].map(cmap))

    years = map_data_formatted.index.year.unique()

    fig_dict = {
        'data':[],
        'layout':{},
        'frames':[]
    }

    fig_dict["layout"].update(
        {'mapbox':{
            'style':"carto-darkmatter",
            'zoom':4,
            'center':{
                'lat':38,'lon':-96}}})

    fig_dict["layout"].update({'height':1000})

    fig_dict["layout"].update({"hovermode":"closest"})

    fig_dict["layout"].update({'updatemenus':[
        dict(
            buttons=[
                dict(
                    args=[None, {"frame": {
                        "duration": 500, 
                        "redraw": True},
                        "fromcurrent": True, 
                        "transition": {
                            "duration": 300}}],
                    label="Play",
                    method="animate",
                    ),
                dict(
                    args=[[None], {"frame": {
                        "duration":0,
                        "redraw":True},
                        "mode": "immediate",
                        "transition": {"duration": 0}}],
                    label="Pause",
                    method="animate",
                    )
                ],
            type="buttons",
            direction="left",
            pad={"r":10, "t":87},
            showactive=False,
            xanchor="right",
            yanchor="top",
            x=0.1,
            y=0
            )
        ]
    })

    fig_dict["layout"].update({"legend":{
        "title":{
            "text":"Shape"}
        }
    })

    # fig_dict["layout"].update({"paper_bgcolor":"mediumspringgreen"})
    # {"legend": {
        # "title":"""
        # <h1><b>Shape</b></h1>
        # <br>double click to isolate
        # <br>single click to disable
        # """,
        # "side":{"text-align":"center"}}})

    shapes = list(map_data_formatted["shape"].dropna().unique())

    frames = []
    for year in years:
        frame = {"data": [], "name":str(year)}
        dataset_by_year = map_data_formatted[map_data_formatted.index.year==year]
        for shape in shapes:
            
            dataset_by_year_and_shape = dataset_by_year[
                dataset_by_year["shape"]==shape]
            
            if len(dataset_by_year_and_shape) > 0:
                trace = go.Scattermapbox(
                    lat=dataset_by_year_and_shape["latitude"],
                    lon=dataset_by_year_and_shape["longitude"],
                    customdata=np.stack((
                        dataset_by_year_and_shape["shape"],
                        dataset_by_year_and_shape["duration_formatted"],
                        dataset_by_year_and_shape["state_name"],
                        dataset_by_year_and_shape["county_name"],
                        dataset_by_year_and_shape["city_name"],
                        dataset_by_year_and_shape.index.year,
                        dataset_by_year_and_shape['duration_seconds']
                        ),
                        axis=-1),
                    mode="markers",
                    marker={'color':dataset_by_year_and_shape['color']},
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

    fig_dict["data"] = frames[0]["data"]

    fig_dict["frames"] = frames[1:]

    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Year:",
            "visible": True,
            "xanchor": "right"
        },
        "transition": {
            "duration": 300,
            "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    for year in years:
        slider_step = {
            "args": [
                [year],
                {"frame": {
                    "duration": 300,
                    "redraw": True},
                "mode": "immediate",
                "transition": {"duration": 300},
                }
            ],
            "label": year,
            "method": "animate"
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"].update({"sliders":[sliders_dict]})

    # with open("fig_dict.json", "w") as f:
    #     json.dump(fig_dict, f)
    
    # f.close()

    # fig = go.Figure(fig_dict)

    with open('fig_dict_object.pkl', 'wb') as f:
        pickle.dump(fig_dict, f)
    
    f.close()