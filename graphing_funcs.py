import plotly.express as px
import plotly.graph_objects as go
from callback_funcs import get_country_shape_counts_chained
import numpy as np



def update_graph_2(tweaked, country):
    """Plots the dataset of the selected country based on callback data"""

    def calculate_n_log_ticks(year_max):
        """helper func to calculate the yaxis1 bound"""
        return len(str(int(np.floor(year_max*1.2))))
        # return len(str(year_max))

    def calculate_yaxis2(cumsum_max):
        """helper func to calculate the yaxis2 bound"""
        return (cumsum_max*1.3)//(10**(len(str(cumsum_max))-2))*\
            (10**(len(str(cumsum_max))-2))
    
    dataset = get_country_shape_counts_chained(tweaked, country)
    fig_dict = {
        "data": [],
        "layout": {},
        "frames": []
    }

    fig_dict['layout'].update({
        'updatemenus': [{
            'buttons': [
                {
                    "args": [
                        None, 
                        {
                            "frame": {"duration": 500, "redraw": False},
                            "fromcurrent": True, 
                            "transition": {
                            "duration": 300, "easing": "quadratic-in-out"}
                        }
                    ],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration":0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0}
                        }
                    ],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
            }],
        'yaxis': {
            'title': 'Year Count<br>(log)',
            'range': [0,calculate_n_log_ticks(dataset["year_count"].max())],
            'type': 'log',
            'nticks':calculate_n_log_ticks(dataset["year_count"].max()),
            'color':'#0000FF'},
        'yaxis2': {
            'title': 'Cumulative Count<br>(linear)',
            'range': [0, calculate_yaxis2(dataset["cumsum"].max())], 
            'overlaying': 'y', 'side': 'right', 'nticks': 5,
            'color':'#FF0000'},
        'hovermode': "closest",
        'title':"Yearly and Cumulative Count of Shapes",
        'legend': {'orientation': 'h'}
        })
    
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
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": []
    }

    # make frames
    for year in list(dataset.datetime.unique()):
        frame = {"data": [], "name": str(year)}
        dataset_by_year = dataset[dataset["datetime"] == int(year)]
        # add the old data population to this part
        # y = dataset["datetime"]
        year_data = [
            go.Bar(
                name='year',
                x=dataset_by_year['shape'], 
                y=dataset_by_year['year_count_log'],
                yaxis='y', offsetgroup=1, 
                customdata=dataset_by_year["year_count"],
                texttemplate='%{customdata:}',
                textposition='outside',
                hovertemplate='%{customdata:}'
                ),
            go.Bar(
                name='cumulative',
                x=dataset_by_year['shape'],
                y=dataset_by_year['cumsum'],
                yaxis='y2', offsetgroup=2,
                texttemplate='%{y:}',
                textposition='outside',
                hovertemplate='%{y:}'
                )
            ]
        frame["data"] = year_data
        fig_dict["frames"].append(frame)
        slider_step = {"args": [
            [str(year)],
            {"frame": {"duration": 300, "redraw": False},
            "mode": "immediate",
            "transition": {"duration": 300}}
            ],
            "label": str(year),
            "method": "animate"}
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]
    fig_dict["data"] = fig_dict["frames"][-1]["data"]
    # fig_dict["data"] = fig_dict["frames"][0]["data"]
    fig_dict["layout"]["sliders"][0]["active"] = len(fig_dict["frames"])-1
    fig = go.Figure(fig_dict)

    return fig