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
    FastTable,
    GridGallery,
    GridGalleryV2,
    IFrame,
    Markdown,
    SelectDataset,
)
from supervisely.nn.benchmark import metric_provider
from supervisely.nn.benchmark.metric_provider import METRIC_NAMES, MetricProvider


def grid_gallery_model_preds():
    gt_project_id = 38685
    gt_dataset_id = 91896
    pred_project_id = 38684
    pred_dataset_id = 91895
    diff_project_id = 38740
    diff_dataset_id = 92002

    gt_project_meta = sly.ProjectMeta.from_json(data=g.api.project.get_meta(id=gt_project_id))
    pred_project_meta = sly.ProjectMeta.from_json(data=g.api.project.get_meta(id=pred_project_id))
    diff_project_meta = sly.ProjectMeta.from_json(data=g.api.project.get_meta(id=diff_project_id))

    global grid_gallery
    # initialize widgets we will use in UI
    grid_gallery = GridGalleryV2(columns_number=3, enable_zoom=False)

    gt_image_info = g.api.image.get_list(dataset_id=gt_dataset_id)[0]

    for image in g.api.image.get_list(dataset_id=pred_dataset_id):
        if image.name == gt_image_info.name:
            pred_image_info = image
            break

    for image in g.api.image.get_list(dataset_id=diff_dataset_id):
        if image.name == gt_image_info.name:
            diff_image_info = image
            break

    images_infos = [gt_image_info, pred_image_info, diff_image_info]
    anns_infos = [g.api.annotation.download(x.id) for x in images_infos]
    project_metas = [gt_project_meta, pred_project_meta, diff_project_meta]

    for idx, (image_info, ann_info, project_meta) in enumerate(
        zip(images_infos, anns_infos, project_metas)
    ):
        image_name = image_info.name
        image_url = image_info.full_storage_url

        # image_ann = sly.Annotation.from_json(data=ann_info, project_meta=project_meta)
        # g.api.annotation.get_info_by_id(image_info.id)

        grid_gallery.append(
            title=image_name,
            image_url=image_url,
            annotation_info=ann_info,
            column_index=idx,
            project_meta=project_meta,
        )


if g.RECALC_PLOTS:
    grid_gallery_model_preds()

markdown = Markdown(
    """
Here are samples of model predictions. The images are sorted using our Auto-insights ranking algorithm. The algorithm is trying to gather a diverse set of images that illustrate the model's performance across various scenarios. It takes into account per-image metrics (precision, recall, TP, FP, FN counts), model predictions, and ground truth annotations to provide a comprehensive view of how the model performs in different conditions, revealing the edge cases.\n

You can choose different sorting method:\n
* **Least accurate**: Displays images where the model made more errors.\n
* **Most accurate**: Displays images where the model made fewer or no errors.\n
* **Dataset order**: Displays images in the original order of the dataset\n

""",
    show_border=False,
)
# table_model_preds = FastTable(g.m.prediction_table())
# iframe_overview = IFrame("static/01_overview.html", width=620, height=520)


# Input card with all widgets.
card = Card(
    "Model Predictions",
    "Description",
    content=Container(
        widgets=[
            # markdown,
            grid_gallery,
            # table_model_preds,
        ]
    ),
    # content_top_right=change_dataset_button,
    collapsable=True,
)