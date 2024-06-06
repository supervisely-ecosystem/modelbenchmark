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
    Table,
    Text,
)
from supervisely.nn.benchmark import metric_provider
from supervisely.nn.benchmark.metric_provider import METRIC_NAMES, MetricProvider


def prepare():
    global pr_curve
    pr_curve = g.m.pr_curve()


def _pr_curve():
    # Precision-Recall curve
    fig = px.line(
        x=g.m.recThrs,
        y=pr_curve.mean(-1),
        title="Precision-Recall Curve",
        labels={"x": "Recall", "y": "Precision"},
        width=600,
        height=500,
    )
    fig.data[0].name = "Model"
    fig.data[0].showlegend = True
    fig.update_traces(fill="tozeroy", line=dict(color="#1f77b4"))
    fig.add_trace(
        go.Scatter(
            x=g.m.recThrs,
            y=[1] * len(g.m.recThrs),
            name="Perfect",
            line=dict(color="orange", dash="dash"),
            showlegend=True,
        )
    )
    fig.add_annotation(
        text=f"mAP = {g.m.base_metrics()['mAP']:.2f}",
        xref="paper",
        yref="paper",
        x=0.98,
        y=0.92,
        showarrow=False,
        bgcolor="white",
    )

    # fig.show()
    fig.write_html(g.STATIC_DIR + "/07_01_pr_curve.html")


def pr_curve_perclass():
    # Precision-Recall curve per-class
    df = pd.DataFrame(pr_curve, columns=g.m.cat_names)

    fig = px.line(
        df,
        x=g.m.recThrs,
        y=df.columns,
        title="Precision-Recall Curve per Class",
        labels={"x": "Recall", "value": "Precision", "variable": "Category"},
        color_discrete_sequence=px.colors.qualitative.Prism,
        width=800,
        height=600,
    )

    fig.update_yaxes(range=[0, 1])
    fig.update_xaxes(range=[0, 1])
    # fig.show()

    fig.write_html(g.STATIC_DIR + "/07_02_pr_curve_perclass.html")


if g.RECALC_PLOTS:
    prepare()
    _pr_curve()
    pr_curve_perclass()

txt = Text("text")
# table_model_preds = Table(g.m.prediction_table())
iframe_pr = IFrame("static/07_01_pr_curve.html", width=620, height=520)
iframe_pr_perclass = IFrame("static/07_02_pr_curve_perclass.html", width=820, height=620)


# Input card with all widgets.
card = Card(
    "PR Curves",
    "Description",
    content=Container(
        widgets=[
            txt,
            iframe_pr,
            iframe_pr_perclass,
        ]
    ),
    # content_top_right=change_dataset_button,
    collapsable=True,
)
