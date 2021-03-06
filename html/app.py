import pandas as pd
from dash import Dash, html, dcc, Input, Output, no_update
import altair as alt
import dash_bootstrap_components as dbc
from datetime import date
alt.data_transformers.disable_max_rows()

# Data (wrangled)
raw_trees = pd.read_csv("data/processed_trees.csv")
raw_trees["BLOOM_START"] = pd.to_datetime(raw_trees["BLOOM_START"], format="%d/%m/%Y")
raw_trees["BLOOM_END"] = pd.to_datetime(raw_trees["BLOOM_END"], format="%d/%m/%Y")
raw_trees["CULTIVAR_NAME"] = raw_trees["CULTIVAR_NAME"].str.title()
raw_trees["COMMON_NAME"] = raw_trees["COMMON_NAME"].str.title()



# Setup app and layout/frontend
app = Dash(external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Montserrat:wght@300&display=swap',
    dbc.themes.BOOTSTRAP])

server = app.server

# C O M P O N E N T S

# Collapse

toast = html.Div(
    [
        dbc.Button(
            "About",
            id="simple-toast-toggle",
            color="#B665A4",
            className="mb-3",
            n_clicks=0,
        )
    ]
)



# Header navigation component
navbar = dbc.NavbarSimple(
    children=[
        toast
    ],
    brand="Vancouver Cherry Blossom Tracker",
    brand_href="#",
    color="#B665A4",
    dark=True,
)

# Menu filters
date_picker = dcc.DatePickerRange(
    id="picker_date",
    min_date_allowed=date(2022, 1, 1),
    max_date_allowed=date(2022, 5, 30),
    start_date_placeholder_text="Start date",
    end_date_placeholder_text="End date",
)

drop_hood = dcc.Dropdown(
    id="filter_neighbourhood",
    value="all_neighbourhoods",
    options=[
        { "label": "All neighbourhoods", "value": "all_neighbourhoods",
        }] + 
        [{"label": i, "value": i}
        for i in raw_trees.NEIGHBOURHOOD_NAME.unique()
        ]
    )

drop_cultivar = dcc.Dropdown(
    id="filter_cultivar",
    value="all_cultivars",
    options=[
        {"label": "All cultivars", "value": "all_cultivars"}
        ] +
        [{"label": i, "value": i}
        for i in raw_trees.CULTIVAR_NAME.unique()
        ]
)

# Range sliders
range_slider = dcc.RangeSlider(
    id="slider_diameter",
    min=0,
    max=150,
    value=[0, 150],
    marks={0: "0cm", 150: "150cm"},
    tooltip={"placement": "bottom", "always_visible": True},
)

# L A Y O U T

app.layout = dbc.Container([
    dbc.Toast(
            [html.A("GitHub", href='https://github.com/UBC-MDS/cherry_blossom_tracker',
            style={'color':'white', 'text-decoration': 'underline'}),
            html.P("The dashboard was created by Katia Aristova, Gabriel Fairbrother, Chaoran Wang, TZ Yan. It is licensed under the terms of the GNU General Public License v3.0 license. You can find more information in our GitHub repo."),
            html.A("Data", href='https://opendata.vancouver.ca/explore/dataset/street-trees/',
            style={'color':'white', 'text-decoration': 'underline'}),
            html.P("The dataset was created by the City of Vancouver and accessed via Vancouver Open Data website."),
            html.A("Logo", href='https://thenounproject.com/icon/cherry-blossoms-2818017/',
            style={'color':'white', 'text-decoration': 'underline'}),
            html.P("The cherry blossom logo Cherry Blossoms by Olena Panasovska from NounProject.com"),
        ],
            id="simple-toast",
            header="About",
            icon="primary",
            dismissable=True,
            is_open=False,
        ),
    dbc.Container([
        dbc.Container([
            dbc.Row([
            dbc.Col(
                html.Div(
                    html.Img(src = 'assets/logo.png', height='70px')),
                    id='logo-img',
                    width = 1,
                    style={'padding-top': '5px'}),
            dbc.Col(navbar, style = {'padding': '0'}, width = 11)
        ])
    ],
    id = 'header')
    ],
    id = 'header-back'),
    dbc.Container([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label(["Blossom date"],),
                    date_picker
                    ],
                    width = 3),
                dbc.Col([
                    html.Label(["Neighbourhood"],),
                    drop_hood
                    ],
                    width = 3),
                    dbc.Col([
                        html.Label(["Tree cultivar (type)"]),
                        drop_cultivar
                    ],
                    width = 3),
                dbc.Col([
                    html.Label(["Tree diameter"],),
                    range_slider
                    ],
                    width = 3)
            ],
        id = 'menu-bar')
    ])],
    id = 'nav-back'),
    dbc.Container([
        dbc.Row([dbc.Col([
            html.Label(["Cherry blossom tree map"]),
            html.Div(
                style = {
                    'height': '400px',
                    'background-color':'lightgray'})
        ],
        width = 12,
        id='row-map')]),
        dbc.Row([
            dbc.Col([
                html.Label(["Tree cultivars (types)"]),
                html.Iframe(
                    id='bar')],
                    width = 6,
                    className = 'chart-box'),
            dbc.Col([
                html.Label(["Blooming timeline"]),
                html.Iframe(
                    id='timeline'
                    )],
                    width=6,
                    className = 'chart-box'),
                    ],
                    className='row-chart'),
        dbc.Row([
            dbc.Col([
                html.Label(["Tree diameters"]),
                html.Iframe(
                    id='diameter')],
                    width = 6,
                    className = 'chart-box'),
            dbc.Col([
                html.Label(["Tree density"]),
                html.Iframe()],
                    width=6,
                    className = 'chart-box'),
                ],
            className='row-chart')
            ])
        ],
    id = 'content'
)

# C H A R T  F U N C T I O N S

def bar_plot(trees_bar):
    trees_bar = trees_bar.dropna(subset=["COMMON_NAME", "NEIGHBOURHOOD_NAME"])

    bar_plot = (
        alt.Chart(trees_bar)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", axis=alt.Axis(title="Number of Trees")),
            y=alt.Y(
                "COMMON_NAME:N",
                axis=alt.Axis(title="Tree Name"),
                sort=alt.SortField("count", order="descending"),
            ),
            tooltip=alt.Tooltip("count:Q"),
        )
        .transform_aggregate(count="count()", groupby=["COMMON_NAME"])
        .transform_filter("datum.count >= 10")
        .configure_mark(opacity=0.6, color="#F3B2D2")
        .interactive()
    )

    return bar_plot.to_html()

def timeline_plot(trees_timeline):
    trees_timeline = trees_timeline.dropna(subset=["BLOOM_START", "BLOOM_END"])

    timeline = (
        alt.Chart(trees_timeline)
        .mark_bar()
        .encode(
            x=alt.X(
                "BLOOM_START",
                axis=alt.Axis(
                    values=[
                        d.isoformat()
                        for d in pd.date_range(
                            start="2022-01-01", end="2022-5-31", freq="1M"
                        )
                    ],
                    format="%b",
                    tickCount=5,
                    orient="top",
                ),
                title=None,
            ),
            x2="BLOOM_END",
            y=alt.Y("CULTIVAR_NAME:N", title=None),
            tooltip=[
                alt.Tooltip("BLOOM_START", title="Start"),
                alt.Tooltip("BLOOM_END", title="End"),
            ],
        )
        .configure_mark(color="#F3B2D2")
        .configure_axis(domainOpacity=0)
        .configure_view(strokeOpacity=0)
    )

    return timeline.to_html()

def diameter_plot(trees_df):
    trees_df = trees_df.dropna(subset=["DIAMETER"])
    trees_df["DIAMETER_CM"] = trees_df["DIAMETER"] * 2.54
    diameter = alt.Chart(trees_df).transform_density(
        'DIAMETER_CM',
        as_=['DIAMETER', 'density']).mark_area(
            interpolate='monotone', color='#F3B2D2',
            opacity=0.4,
            line=({'color':'#B665A4'})).encode(
        alt.X('DIAMETER', title = 'Tree diameter (cm)', scale=alt.Scale(nice=False)),
        alt.Y('density:Q', title="Density", axis=alt.Axis(labels=False))
    )
    return diameter.to_html()

# Set up callbacks/backend
@app.callback(
    Output("bar", "srcDoc"),
    Output("timeline", "srcDoc"),
    Output("diameter", "srcDoc"),
    Input("picker_date", "start_date"),
    Input("picker_date", "end_date"),
    Input("filter_neighbourhood", "value"),
    Input("filter_cultivar", "value"),
    Input("slider_diameter", "value")
)

def main_callback(start_date, end_date, neighbourhood, cultivar, diameter_range):
    # Build new dataset and call all charts

    # Date input Cleanup
    if start_date is None:
        start_date = "2022-01-01"
    if end_date is None:
        end_date = "2022-05-30"
    start_date = pd.Timestamp(date.fromisoformat(start_date))
    end_date = pd.Timestamp(date.fromisoformat(end_date))

    filtered_trees = raw_trees

    # Filter by neighbourhood
    if neighbourhood != "all_neighbourhoods":
        filtered_trees = filtered_trees[
            filtered_trees["NEIGHBOURHOOD_NAME"] == neighbourhood
        ]

    # Filter by date

    filtered_trees = filtered_trees[
        (
            (filtered_trees["BLOOM_START"] <= start_date)
            & (filtered_trees["BLOOM_END"] >= start_date)
        )
        | (
            (filtered_trees["BLOOM_START"] <= end_date)
            & (filtered_trees["BLOOM_END"] >= end_date)
        )
        | (filtered_trees["BLOOM_START"].between(start_date, end_date))
        | (filtered_trees["BLOOM_END"].between(start_date, end_date))
    ]

    # Filter by Diameter
    filtered_trees = filtered_trees[
        filtered_trees["DIAMETER"].between(diameter_range[0], diameter_range[1])
    ]

    if cultivar != "all_cultivars":
        filtered_trees = filtered_trees[filtered_trees["CULTIVAR_NAME"] == cultivar]

    bar = bar_plot(filtered_trees)
    timeline = timeline_plot(filtered_trees)
    diameter = diameter_plot(filtered_trees)

    return bar, timeline, diameter

@app.callback(
    Output("simple-toast", "is_open"),
    [Input("simple-toast-toggle", "n_clicks")],
)
def open_toast(n):
    if n == 0:
        return no_update
    return True

if __name__ == '__main__':
    app.run_server(debug=True, port=8000)