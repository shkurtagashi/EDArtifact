import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
import base64
import json
import io
import flask
import os
from textwrap import dedent as d
from datetime import datetime
import dash_table
import plotly.graph_objs as go
import plotly
from datetime import timedelta
from UIHelper import UIHelper
from EDAData import EDAData
import time
import dash_auth

# from datetime import timezone
from datetime import datetime

# import urllib.parse
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

STATIC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# The css stylesheet that we are using for the app
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.scripts.config.serve_locally = True
# app.config.supress_callback_exceptions = True
app.config["suppress_callback_exceptions"] = True


@app.server.route("/static/<resource>")
def serve_static(resource):
    return flask.send_from_directory(STATIC_PATH, resource)


## Read from password file
VALID_USERNAME_PASSWORD_PAIRS = pd.read_csv("static/auth_details.csv")
VALID_USERNAME_PASSWORD_PAIRS = VALID_USERNAME_PASSWORD_PAIRS.values
auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

# Defining some text to add on the dashboard
title1 = """
# Artifacts examples
"""

title2 = """
# Upload csv
"""

# Defining css colors
colors = {
    "background": "#ffffff",
    "text": "#11111",
    "grey": "#d3d3d3",
    "artifact": "#ff0000",
    "clean": "#458b00",
    "unsure": "#ff8000",
    "progress": "#c1ae8d",
}

styles = {"pre": {"border": "thin lightgrey solid", "overflowX": "scroll"}}


class CallbackVars:
    def __init__(self):
        self.clicks_next = 0
        self.clicks_prev = 0
        self.clicks_done = 0
        self.clicks_clean_all = 0
        self.clicks_artifact_all = 0
        self.clicks_continue = 0
        self.clicks_next_epoch = 0
        self.clicks_prev_epoch = 0
        self.clicks_finish = 0
        self.filename = ""
        self.last_click = 0
        self.clicks_download = 0
        self.clicks_reset = 0
        self.username = ""

    def update_next(self):
        self.clicks_next += 1

    def update_prev(self):
        self.clicks_prev += 1

    def update_done(self):
        self.clicks_done += 1

    def update_clean(self):
        self.clicks_clean_all += 1

    def update_artifact(self):
        self.clicks_artifact_all += 1

    def update_clicks_continue(self):
        self.clicks_continue += 1

    def update_next_epoch(self):
        self.clicks_next_epoch += 1

    def update_prev_epoch(self):
        self.clicks_prev_epoch += 1

    def update_finish(self):
        self.clicks_finish += 1

    def update_last_click(self, val):
        self.last_click = val

    def update_clicks_download(self):
        self.clicks_download += 1

    def update_clicks_reset(self):
        self.clicks_reset += 1

    def set_username(self, user):
        self.username = user


eda_Data = EDAData()
callback_vars = CallbackVars()
ui_helper = UIHelper()

# Defining the main layout components
app.layout = html.Div(
    children=[
        html.H1(
            children="EDA Artifacts Labelling Dashboard",
            style={"textAlign": "center", "color": colors["text"]},
        ),
        html.Div(
            [
                dcc.Upload(
                    id="upload-data",
                    children=html.Button("Upload File"),
                    style={"display": "inline-block", "margin": "10px"},
                    multiple=True,
                ),
                html.Button(
                    "Continue labelling",
                    id="continue",
                    style={"display": "inline-block", "margin": "10px"},
                    n_clicks=0,
                ),
                html.Button(
                    "Reset",
                    id="reset",
                    style={"display": "inline-block", "margin": "10px"},
                    n_clicks=0,
                ),
                html.Button(
                    "Finish", style={"float": "right"}, id="download", n_clicks=0
                ),
            ]
        ),
        html.Br(),
        html.Div(id="error message"),
        dcc.Graph(id="eda_data_graph"),
        html.Div(
            [
                html.Div(
                    [
                        html.Button(
                            children=[
                                html.Img(
                                    src=app.get_asset_url("arrow-left.png"),
                                    style={"height": "25px", "width": "25px"},
                                ),
                            ],
                            style={"padding": "5px", "height": "40px"},
                            id="previous-window",
                            n_clicks=0,
                        ),
                    ],
                    style={"display": "inline-block", "float": "left"},
                ),
                html.Div(
                    [
                        html.Button(
                            "Mark all as clean",
                            id="clean_all",
                            style={"margin": "10px", "height": "40px"},
                            n_clicks=0,
                        ),
                        html.Button(
                            "Mark all as artifact",
                            id="artifact_all",
                            style={"margin": "10px", "height": "40px"},
                            n_clicks=0,
                        ),
                    ],
                    style={"display": "inline-block"},
                ),
                html.Div(
                    [
                        html.Button(
                            children=[
                                html.Img(
                                    src=app.get_asset_url("arrow-right.png"),
                                    style={"height": "25px", "width": "25px"},
                                ),
                            ],
                            style={"height": "40px", "padding": "5px"},
                            id="next-window",
                            n_clicks=0,
                        )
                    ],
                    style={"display": "inline-block", "float": "right"},
                ),
            ],
            style={"text-align": "center"},
        ),
        dcc.Graph(id="eda_parts"),
        html.Div(
            [
                html.Button(
                    children=[
                        html.Img(
                            src=app.get_asset_url("arrow-left.png"),
                            style={"height": "25px", "width": "25px"},
                        ),
                    ],
                    style={
                        "padding": "5px",
                        "height": "40px",
                        "display": "inline-block",
                        "float": "left",
                    },
                    id="prev-epoch",
                    n_clicks=0,
                ),
                html.Button(
                    children=[
                        html.Img(
                            src=app.get_asset_url("arrow-right.png"),
                            style={"height": "25px", "width": "25px"},
                        ),
                    ],
                    style={
                        "padding": "5px",
                        "height": "40px",
                        "display": "inline-block",
                        "float": "right",
                    },
                    id="next-epoch",
                    n_clicks=0,
                ),
            ]
        ),
        html.Br(),
        html.Br(),
        dcc.Graph(
            id="detailed_view",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label(
                            "Label:", style={"float": "left", "margin-left": "150px"}
                        ),
                        dcc.RadioItems(
                            options=[
                                {"label": "Artifact", "value": "artifact"},
                                {"label": "Unsure", "value": "unsure"},
                                {"label": "Clean", "value": "clean"},
                            ],
                            value="clean",
                            id="label",
                            labelStyle={"display": "inline-block"},
                            style={"float": "left", "margin-right": "75px"},
                        ),
                        html.Label("Confidence:", style={"float": "left"}),
                        dcc.RadioItems(
                            options=[
                                {"label": "High", "value": "high"},
                                {"label": "Low", "value": "low"},
                            ],
                            value="low",
                            id="confidence",
                            labelStyle={"display": "inline-block"},
                            style={"float": "left"},
                        ),
                    ],
                    style={
                        "margin": "0 auto",
                        "width": "60%",
                        "text-align": "center",
                        "margin-bottom": "15px",
                    },
                ),
                html.Br(),
                html.Div(
                    [
                        html.Label("Type of artifact:", style={"float": "left"}),
                        dcc.RadioItems(
                            options=[
                                {"label": "None", "value": "none"},
                                {"label": "Abrupt peak", "value": "abrupt_peak"},
                                {"label": "Abrupt drop", "value": "abrupt_drop"},
                                {"label": "Out of range", "value": "out_of range"},
                                {
                                    "label": "Changes quickly",
                                    "value": "changes_quickly",
                                },
                                {"label": "Rises quickly", "value": "rise_quickly"},
                                {"label": "Drops quickly", "value": "drops_quickly"},
                                {
                                    "label": "Invalid portion - left",
                                    "value": "invalid-left",
                                },
                                {
                                    "label": "Invalid portion - right",
                                    "value": "invalid-right",
                                },
                            ],
                            value="none",
                            id="artifact-type",
                            labelStyle={"display": "inline-block"},
                            style={
                                "margin": "0 auto",
                                "width": "70%",
                                "text-align": "center",
                            },
                        ),
                    ],
                    style={
                        "margin": "0 auto",
                        "width": "60%",
                        "text-align": "center",
                        "margin-bottom": "15px",
                    },
                ),
                html.Br(),
                html.Div(
                    [html.Button("Done", id="done", n_clicks=0)],
                    style={
                        "margin": "0 auto",
                        "width": "20%",
                        "text-align": "center",
                        "margin-bottom": "15px",
                    },
                ),
            ],
            id="artifact-labelling",
        ),
        dcc.Graph(
            id="acc_data",
        ),
        html.Div(id="hidden-div", style={"display": "none"}),
    ]
)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    try:
        df = None
        if "csv" in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        elif "xls" in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        return df
    except Exception as e:
        print(e)
        return None


# Callback to create the file on load
@app.callback(
    Output(component_id="eda_data_graph", component_property="figure"),
    [
        Input("eda_parts", "figure"),
        Input("continue", "n_clicks"),
        Input("next-window", "n_clicks"),
        Input("previous-window", "n_clicks"),
    ],
)
def update_output(fig, continue_clicks, next, prev):
    if eda_Data.loaded:
        save = False
        shapes = []
        left, right = eda_Data.current_window_left, eda_Data.current_window_right
        current = ui_helper.get_current_marker(left, right)
        shapes.append(current)
        start, end = eda_Data.get_progress()
        progress = ui_helper.get_shape(start, end, colors["progress"])
        shapes.append(progress)
        layout = {"shapes": shapes, "yaxis": {"title": "EDA"}}
        return {
            "data": [
                go.Scattergl(
                    x=eda_Data.eda["eda_Time"],
                    y=eda_Data.eda["eda_value"],
                    mode="lines",
                )
            ],
            "layout": layout,
        }
    return [{}]


@app.callback(
    Output(component_id="eda_parts", component_property="figure"),
    [
        Input("upload-data", "contents"),
        Input("upload-data", "filename"),
        Input("eda_parts", "clickData"),
        Input("clean_all", "n_clicks"),
        Input("artifact_all", "n_clicks"),
        Input("continue", "n_clicks"),
        Input("done", "n_clicks"),
        Input("next-epoch", "n_clicks"),
        Input("prev-epoch", "n_clicks"),
        Input("next-window", "n_clicks"),
        Input("previous-window", "n_clicks"),
        Input("download", "n_clicks"),
        Input("reset", "n_clicks"),
    ],
    [
        State("label", "value"),
        State("confidence", "value"),
        State("artifact-type", "value"),
    ],
)
def update_window(
    contents,
    filename,
    clickData,
    clean_all_click,
    artifact_all_click,
    continue_clicks,
    done,
    next_epoch,
    prev_epoch,
    next_window,
    prev_window,
    download,
    reset,
    value,
    confidence,
    type_artifact,
):
    header = flask.request.headers.get("Authorization", None)
    if header:
        username_password = base64.b64decode(header.split("Basic ")[1])
        username_password_utf8 = username_password.decode("utf-8")
        username, p = username_password_utf8.split(":")
        callback_vars.set_username(username)
    move = False
    df = None
    if reset != callback_vars.clicks_reset:
        if eda_Data.loaded == True:
            callback_vars.update_clicks_reset()
            eda_Data.reset()
    elif download != callback_vars.clicks_download:
        if eda_Data.loaded == True:
            name = callback_vars.filename.split(".")[0]
            download_name = name + "_labelled_" + callback_vars.username + ".csv"
            eda_Data.eda.to_csv(download_name, sep=",", index=False)
            eda_Data.reset()
            callback_vars.filename = ""
            callback_vars.update_clicks_download()
    elif continue_clicks != callback_vars.clicks_continue:
        callback_vars.update_clicks_continue()
        df = None
        df_acc = None
        if os.path.exists("backup.csv"):
            df = pd.read_csv("backup.csv")
        if os.path.exists("backup_acc.csv"):
            df_acc = pd.read_csv("backup_acc.csv")
        if df is not None:
            eda_Data.upload_backup(df, df_acc)
    elif contents is not None:
        filename_eda = None
        contents_eda = None
        filename_acc = None
        contents_acc = None
        for my_file, c in zip(filename, contents):
            if "Filtered_EDA" in str(my_file):
                filename_eda = my_file
                contents_eda = c
            if "ACC" in str(my_file):
                filename_acc = my_file
                contents_acc = c
        if filename_eda != callback_vars.filename:
            callback_vars.filename = filename_eda
            df = parse_contents(contents_eda, filename_eda)
            columns = list(df)
            if "EDA_Filtered" in columns and "Time" in columns:
                eda_Data.upload(df.EDA_Filtered, df.Time)
            if filename_acc is not None:
                df_acc = parse_contents(contents_acc, filename_acc)
                eda_Data.upload_acc(df_acc.ACC_g, df_acc.Time)
                while not eda_Data.loaded:
                    pass
    ##Waiting for the file to be loaded before displaying:

    if eda_Data.loaded:
        save = False
        move = False
        if next_window != callback_vars.clicks_next:
            callback_vars.update_next()
            eda_Data.move_to_next()
            save = True
            move = True
        elif prev_window != callback_vars.clicks_prev:
            callback_vars.update_prev()
            eda_Data.move_to_prev()
            save = True
            move = True
        elif callback_vars.clicks_next_epoch != next_epoch:
            callback_vars.update_next_epoch()
            eda_Data.set_current_epochs(eda_Data.current_epoch + 1)
            move = True
        elif callback_vars.clicks_prev_epoch != prev_epoch:
            callback_vars.update_prev_epoch()
            eda_Data.set_current_epochs(eda_Data.current_epoch - 1)
            move = True
        elif clean_all_click != callback_vars.clicks_clean_all:
            callback_vars.update_clean()
            eda_Data.label_window_as(eda_Data.current_window, "clean")
        elif artifact_all_click != callback_vars.clicks_artifact_all:
            callback_vars.update_artifact()
            eda_Data.label_window_as(eda_Data.current_window, "artifact")
        if save:
            eda_Data.eda.to_csv("backup.csv", sep=",", index=False)
            if eda_Data.loaded_acc == True:
                eda_Data.acc.to_csv("backup_acc.csv", sep=",", index=False)
            eda_Data.set_current_epochs(eda_Data.get_first_of_window())
        window = eda_Data.get_window()
        shapes = []
        if clickData is not None and not move:
            interval = eda_Data.get_value_of(clickData["points"][0]["x"], "intervals")
            if interval != callback_vars.last_click:
                eda_Data.set_current_epochs(interval)
                callback_vars.update_last_click(interval)
        left, right, label = eda_Data.get_current_epoch_values()
        if done != callback_vars.clicks_done:
            callback_vars.update_done()
            eda_Data.label_epoch(left, right, value, confidence, type_artifact)
            eda_Data.set_current_epochs(eda_Data.current_epoch + 1)
        left, right, label = eda_Data.get_current_epoch_values()
        current = ui_helper.get_current_marker(left, right)
        shapes.append(current)
        for item in window["intervals"].unique():
            left_int, right_int, label = eda_Data.get_interval(int(item))
            if label in {"artifact", "clean", "unsure"}:
                my_shape = ui_helper.get_shape(left_int, right_int, colors[label])
                shapes.append(my_shape)
        layout = {
            "shapes": shapes,
            "yaxis": {"title": "EDA"},
        }
        return {
            "data": [
                go.Scattergl(
                    x=window["eda_Time"],
                    y=window["eda_value"],
                )
            ],
            "layout": layout,
        }
    else:
        return [{}]


@app.callback(
    Output(component_id="acc_data", component_property="figure"),
    [Input("eda_parts", "figure")],
)
def update_accelerometer(contents):
    if eda_Data.loaded_acc:
        left = eda_Data.current_window_left
        right = eda_Data.current_window_right
        interval = eda_Data.acc[eda_Data.acc["Time"].between(left, right)]
        left_epoch = eda_Data.current_epoch_left
        right_epoch = eda_Data.current_epoch_right
        shapes = []
        current = ui_helper.get_current_marker(left_epoch, right_epoch)
        shapes.append(current)
        return {
            "data": [
                go.Scattergl(
                    x=interval["Time"],
                    y=interval["ACC_g"],
                    mode="lines",
                    line=dict(color="orange"),
                )
            ],
            "layout": {"shapes": shapes, "yaxis": {"title": "ACC"}},
        }
    return [{}]


@app.callback(
    Output(component_id="detailed_view", component_property="figure"),
    [
        Input("eda_parts", "clickData"),
        Input("done", "n_clicks"),
        Input("eda_parts", "figure"),
    ],
)
def update_details(clickData, n_clicks, fig):
    if eda_Data.loaded == True:
        left, right = eda_Data.get_interval_padded(eda_Data.current_epoch)
        left_current, right_current, label = eda_Data.get_current_epoch_values()
        shapes = []
        current = ui_helper.get_current_marker(left_current, right_current)
        shapes.append(current)
        interval = eda_Data.get_data_between(left, right)
        return {
            "data": [
                go.Scattergl(
                    x=interval["eda_Time"],
                    y=interval["eda_value"],
                    mode="lines+markers",
                )
            ],
            "layout": {"shapes": shapes, "yaxis": {"title": "EDA"}},
        }
    else:
        return [{}]


@app.callback(
    Output(component_id="artifact-labelling", component_property="style"),
    [Input("eda_parts", "figure")],
)
def update_labelling(fig):
    if eda_Data.loaded == True:
        return {"display": "block", "text-align": "center"}
    return {"display": "none", "text-align": "center"}


@app.callback(
    Output(component_id="label", component_property="value"),
    [Input("eda_parts", "figure")],
)
def update_radio_label(fig):
    if eda_Data.loaded == True:
        label = eda_Data.get_value_of_epoch(eda_Data.current_epoch, "label")
        if label in {"artifact", "clean", "unsure"}:
            return label
        else:
            return "artifact"


@app.callback(
    Output(component_id="confidence", component_property="value"),
    [Input("eda_parts", "figure")],
)
def update_confidence(fig):
    if eda_Data.loaded == True:
        confidence = eda_Data.get_value_of_epoch(eda_Data.current_epoch, "confidence")
        if confidence in {"high", "low"}:
            return confidence
        else:
            return "high"


@app.callback(
    Output(component_id="artifact-type", component_property="value"),
    [Input("eda_parts", "figure")],
)
def update_artifact_type(fig):
    if eda_Data.loaded == True:
        artifact = eda_Data.get_value_of_epoch(eda_Data.current_epoch, "type")
        return artifact


if __name__ == "__main__":
    # app.run_server(debug=True)
    app.run_server()
