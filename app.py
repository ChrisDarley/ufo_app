import dash
from dash import Dash, html, dcc
from populate_data import populate

# data should already be populated for production app
populate()

app = Dash(__name__, use_pages=True)

style = {
    'display':'inline-block',
    'margin-right':'1%'
}

pages = [page for page in dash.page_registry.values()]

# print(list(page["name"] for page in dash.page_registry.values()))
app.layout = html.Div([
    # html.H1('Multi-page app with Dash Pages'),
    html.Div([
        # non ordered version:

        # html.Div(
        #     dcc.Link(
        #         f"{page['name']}",
        #         href=page["relative_path"]),
        #     style=style
        # ) for page in dash.page_registry.values()
        html.Div(
            dcc.Link(
                f"{pages[0]['name']}",
                href=pages[0]['relative_path']
                ),
            style=style
        ),
        html.Div(
            dcc.Link(
                f"{pages[2]['name']}",
                href=pages[2]['relative_path']
                ),
            style=style
        ),
        html.Div(
            dcc.Link(
                f"{pages[1]['name']}",
                href=pages[1]['relative_path']
                ),
            style=style
        ),
    ]),
    dash.page_container
])

if __name__ == '__main__':
    app.run(debug=True)