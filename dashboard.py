import pandas as pd
import dash
from dash.dependencies import Input, Output, State
from dash.dash_table import DataTable
from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.colors import qualitative


app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://stackpath.bootstrapcdn.com/bootswatch/4.5.0/flatly/bootstrap.min.css"
    ],
)


COLORS = qualitative.T10[:2]

SUMMARY = pd.read_csv("data/summary.csv", index_col="group", parse_dates=["date"])
ALL_DATA = pd.read_csv(
    "data/all_data.csv", index_col=["group", "area", "date"], parse_dates=["date"]
).sort_index()
LAST_DATE = SUMMARY["date"].iloc[0]
FIRST_PRED_DATE = LAST_DATE + pd.Timedelta("1D")


def create_table(group):
    used_columns = [
        "area",
        "Deaths",
        "Cases",
        "Deaths per Million",
        "Cases per Million",
    ]
    df = SUMMARY.loc[group, used_columns]
    first_col = "Country" if group == "world" else "State"
    df = df.rename(columns={"area": first_col})

    columns = [{"name": first_col, "id": first_col}]
    for name in df.columns[1:]:
        col_info = {
            "name": name,
            "id": name,
            "type": "numeric",
            "format": {"specifier": ","},
        }
        columns.append(col_info)
    data = df.sort_values("Deaths", ascending=False).to_dict("records")
    return DataTable(
        id=f"{group}-table",
        columns=columns,
        data=data,
        active_cell={"row": 0, "column": 0},
        fixed_rows={"headers": True},
        sort_action="native",
        derived_virtual_data=data,
        style_table={
            "minHeight": "85vh",
            "height": "85vh",
            "overflowY": "scroll",
            "borderRadius": "0px 0px 10px 10px",
        },
        style_cell={
            "whiteSpace": "normal",
            "height": "auto",
            "font-family": "verdana",
        },
        style_header={
            "textAlign": "center",
            "fontSize": 14,
        },
        style_data={
            "fontSize": 12,
        },
        style_data_conditional=[
            {
                "if": {"column_id": first_col},
                "width": "120px",
                "textAlign": "left",
                "textDecoration": "underline",
                "cursor": "pointer",
            },
            {"if": {"row_index": "odd"}, "backgroundColor": "#fafbfb"},
        ],
    )


def create_graphs(group, area):
    df = ALL_DATA.loc[(group, area)]
    df_dict = {"actual": df.loc[:LAST_DATE], "prediction": df.loc[FIRST_PRED_DATE:]}
    figs = create_figures(area)

    kinds = ["Deaths", "Cases"]
    daily_kinds = ["Daily Deaths", "Daily Cases"]

    make_cumulative_graphs(figs[0], df_dict, kinds)
    make_daily_graphs(figs[1], df_dict, daily_kinds)
    make_weekly_graphs(figs[2], df_dict, daily_kinds)
    return figs


def create_figures(title, n=3):
    figs = []
    annot_props = {
        "x": 0.1,
        "xref": "paper",
        "yref": "paper",
        "xanchor": "left",
        "showarrow": False,
        "font": {"size": 18},
    }
    for _ in range(n):
        fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1)
        fig.update_layout(
            title={"text": title, "x": 0.5, "y": 0.97, "font": {"size": 20}},
            annotations=[
                {"y": 0.95, "text": "<b>Deaths</b>"},
                {"y": 0.3, "text": "<b>Cases</b>"},
            ],
            margin={"t": 40, "l": 50, "r": 10, "b": 0},
            legend={
                "x": 0.5,
                "y": -0.05,
                "xanchor": "center",
                "orientation": "h",
                "font": {"size": 15},
            },
        )
        fig.update_traces(showlegend=False, row=2, col=1)
        fig.update_traces(hovertemplate="%{x} - %{y:,}")
        fig.update_annotations(annot_props)
        figs.append(fig)
    return figs


def make_cumulative_graphs(fig, df_dict, kinds):
    for row, kind in enumerate(kinds, start=1):
        for i, (name, df) in enumerate(df_dict.items()):
            fig.add_scatter(
                x=df.index,
                y=df[kind],
                mode="lines+markers",
                line={"color": COLORS[i]},
                showlegend=row == 1,
                name=name,
                row=row,
                col=1,
            )


def make_daily_graphs(fig, df_dict, kinds):
    for row, kind in enumerate(kinds, start=1):
        for i, (name, df) in enumerate(df_dict.items()):
            fig.add_bar(
                x=df.index,
                y=df[kind],
                marker={"color": COLORS[i]},
                showlegend=row == 1,
                name=name,
                row=row,
                col=1,
            )


def make_weekly_graphs(fig, df_dict, kinds):
    offset = "W-" + LAST_DATE.strftime("%a").upper()
    df_dict = {
        name: df.resample(offset, kind="timestamp", closed="right")[kinds].sum()
        for name, df in df_dict.items()
    }

    for row, kind in enumerate(kinds, start=1):
        for i, (name, df) in enumerate(df_dict.items()):
            fig.add_scatter(
                x=df.index,
                y=df[kind],
                mode="lines+markers",
                showlegend=row == 1,
                line={"color": COLORS[i]},
                name=name,
                row=row,
                col=1,
            )


def hover_text(x):
    name = x["area"]
    deaths = x["Deaths"]
    cases = x["Cases"]
    deathsm = x["Deaths per Million"]
    casesm = x["Cases per Million"]
    return (
        f"<b>{name}</b><br>"
        f"Deaths - {deaths:,.0f}<br>"
        f"Cases - {cases:,.0f}<br>"
        f"Deaths per Million - {deathsm:,.0f}<br>"
        f"Cases per Million - {casesm:,.0f}<br>"
    )


def create_map(group, radio_value):
    df = SUMMARY.loc[group].query("population > .5")
    lm = None if group == "world" else "USA-states"
    proj = "robinson" if group == "world" else "albers usa"
    text = df.apply(hover_text, axis=1)

    fig = go.Figure()
    fig.add_choropleth(
        locations=df["code"],
        z=df[radio_value],
        zmin=0,
        locationmode=lm,
        colorscale="orrd",
        marker_line_width=0.5,
        text=text,
        hoverinfo="text",
        colorbar=dict(len=0.6, x=1, y=0.5),
    )
    fig.update_layout(
        geo={
            "lataxis": {"range": [-50, 68]},
            "lonaxis": {"range": [-130, 150]},
            "projection": {"type": proj},
            "showframe": False,
        },
        margin={"t": 0, "l": 10, "r": 10, "b": 0},
    )
    return fig



def create_main_page():
    last_update_text = LAST_DATE.strftime("%B %d, %Y")
    top_info = html.Div(
        [
            html.H3("Coronavirus Forecasting Dashboard", id="info-title"),
            html.H4(f"Data updated through {last_update_text}", id="data-update"),
        ],
        className="top-info",
    )


    def create_tab(content, label, value):
        return dcc.Tab(
            content,
            label=label,
            value=value,
            id=f"{value}-tab",
            className="single-tab",
            selected_className="single-tab--selected",
        )

    world_table = create_table("world")
    usa_table = create_table("usa")

    world_tab = create_tab(world_table, "World", "world")
    usa_tab = create_tab(usa_table, "US States", "usa")


    table_tabs = dcc.Tabs(
        [world_tab, usa_tab],
        mobile_breakpoint=1000,
        className="tabs-container",
        id="table-tabs",
        value="world",  
    )

    graph_kwargs = {
        "config": {"displayModeBar": False, "responsive": True},
        "className": "top-graphs",
    }
    cumulative_graph = dcc.Graph(id="cumulative-graph", **graph_kwargs)
    daily_graph = dcc.Graph(id="daily-graph", **graph_kwargs)
    weekly_graph = dcc.Graph(id="weekly-graph", **graph_kwargs)

    cumulative_tab = create_tab(cumulative_graph, "Cumulative", "cumulative")
    daily_tab = create_tab(daily_graph, "Daily", "daily")
    weekly_tab = create_tab(weekly_graph, "Weekly", "weekly")


    graph_tabs = dcc.Tabs(
        [cumulative_tab, daily_tab, weekly_tab],
        mobile_breakpoint=1000,
        className="tabs-container",
        id="graph-tabs",
        value="cumulative",  
    )

    radio_items = dbc.RadioItems(
        options=[
            {"label": "Deaths", "value": "Deaths"},
            {"label": "Cases", "value": "Cases"},
            {"label": "Deaths per Million", "value": "Deaths per Million"},
            {"label": "Cases per Million", "value": "Cases per Million"},
        ],
        value="Deaths", 
        id="map-radio-items",
        labelCheckedClassName="label-radio-checked",
        inputClassName="label-radio-input",
    )


    map_graph = dcc.Graph(
        id="map-graph", config={"displayModeBar": False, "responsive": True}
    )

    map_div = html.Div([radio_items, map_graph], id="map-div")

    df_summary = SUMMARY.loc["world"]
    df_all = ALL_DATA.loc["world"]
    last_pred_date = ALL_DATA.iloc[-1].name[-1]
    last_pred_date_txt = last_pred_date.strftime("%b %d, %Y")
    ww_deaths, ww_cases = df_summary[["Deaths", "Cases"]].sum()
    ww_deathsp, ww_casesp = (
        df_all.droplevel(0).loc[last_pred_date, ["Deaths", "Cases"]].sum()
    )

    def create_card(header, number):
        return dbc.Card(
            [
                dbc.CardHeader(html.H5(header), className="side-card-header"),
                dbc.CardBody([html.H6(f"{number:,.0f}")]),
            ],
            color="primary",
            className="side-card",
            outline=True,
        )
    header_numbers = {
        "Worldwide Deaths": ww_deaths,
        "Worldwide Cases": ww_cases,
        f"Worldwide Deaths Predicted by {last_pred_date_txt}": ww_deathsp,
        f"Worldwide Cases Predicted by {last_pred_date_txt}": ww_casesp,
    }

    cards = [create_card(header, number) for header, number in header_numbers.items()]

    all_side_cards = html.Div(cards, id="all-side-cards")

    grid_container = html.Div(
        [all_side_cards, table_tabs, graph_tabs, map_div], id="grid-container"
    )
    container = html.Div([top_info, grid_container], id="container")
    return container



container = create_main_page()
app.layout = html.Div([container])




@app.callback(
    [
        Output("cumulative-graph", "figure"),
        Output("daily-graph", "figure"),
        Output("weekly-graph", "figure"),
    ],
    [
        Input("world-table", "active_cell"),
        Input("usa-table", "active_cell"),
        Input("table-tabs", "value"),
    ],
    [
        State("world-table", "derived_virtual_data"),
        State("usa-table", "derived_virtual_data"),
    ],
)
def change_area_graphs(world_cell, usa_cell, group, world_data, usa_data):

    area, cell, data = "Country", world_cell, world_data
    if group == "usa":
        area, cell, data = "State", usa_cell, usa_data

    if cell and cell["column"] == 0:
        country_state = data[cell["row"]][area]
        return create_graphs(group, country_state)
    else:
        raise dash.exceptions.PreventUpdate


@app.callback(
    Output("map-graph", "figure"),
    [Input("table-tabs", "value"), Input("map-radio-items", "value")],
)
def change_map(group, radio_value):
    return create_map(group, radio_value)


if __name__ == "__main__":
    app.run_server(debug=True)
