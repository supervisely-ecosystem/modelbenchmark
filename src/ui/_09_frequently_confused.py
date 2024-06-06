import os
import random
from collections import defaultdict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from matplotlib import pyplot as plt
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval, Params

import src.globals as g
import src.ui.settings as settings
import supervisely as sly
from supervisely.app.widgets import (
    Button,
    Card,
    Container,
    DatasetThumbnail,
    IFrame,
    SelectDataset,
    Text,
)
from supervisely.nn.benchmark import metric_provider
from supervisely.nn.benchmark.metric_provider import METRIC_NAMES, MetricProvider


def frequently_confused():
    confusion_matrix = g.m.confusion_matrix()

    # Frequency of confusion as bar chart
    confused_df = g.m.frequently_confused(confusion_matrix, topk_pairs=20)
    confused_name_pairs = confused_df["category_pair"]
    confused_prob = confused_df["probability"]
    x_labels = [f"{pair[0]} - {pair[1]}" for pair in confused_name_pairs]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=x_labels, y=confused_prob, marker=dict(color=confused_prob, colorscale="Reds"))
    )
    fig.update_layout(
        # title="Frequently confused class pairs",
        xaxis_title="Class pair",
        yaxis_title="Probability",
    )
    fig.update_traces(text=confused_prob.round(2))
    # fig.show()
    fig.write_html(g.STATIC_DIR + "/09_frequently_confused.html")


if g.RECALC_PLOTS:
    frequently_confused()

txt = Text("text")
iframe_frequently_confused = IFrame("static/09_frequently_confused.html", width=620, height=520)


# Input card with all widgets.
card = Card(
    "Frequently confused class pairs",
    "Description",
    content=Container(
        widgets=[
            txt,
            iframe_frequently_confused,
            # dataset_thumbnail,
            # select_dataset,
            # load_button,
            # no_dataset_message,
        ]
    ),
    # content_top_right=change_dataset_button,
    collapsable=True,
)


def clean_static_dir():
    # * Utility function to clean static directory, it can be securely removed if not needed.
    static_files = os.listdir(g.STATIC_DIR)

    sly.logger.debug(f"Cleaning static directory. Number of files to delete: {len(static_files)}.")

    for static_file in static_files:
        os.remove(os.path.join(g.STATIC_DIR, static_file))
