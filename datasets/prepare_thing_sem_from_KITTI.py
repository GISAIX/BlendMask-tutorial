# You may need to restart your runtime prior to this, to let your installation take effect
# Some basic setup:
# Setup detectron2 logger
import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

# import some common libraries
import numpy as np
import cv2
import random

# import some common detectron2 utilities
from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from adet.config import get_cfg
from detectron2.utils.visualizer import Visualizer
from detectron2.data import MetadataCatalog

import os
import numpy as np
import json
from detectron2.structures import BoxMode
from copy import deepcopy
from skimage import measure
from matplotlib import pyplot as plt
from pycocotools.mask import decode, encode, toBbox
import random
import cv2
from detectron2.utils.visualizer import Visualizer
import matplotlib.pyplot as plt


def get_KITTI_dicts(img_dir):
    dataset_dicts = []
    tmp = os.path.join(img_dir, 'annotations_raw')
    for ann in os.listdir(tmp):
        imgs_anns = open(os.path.join(tmp, ann), 'r')
        imgs_anns = imgs_anns.read().splitlines()
        prev_img_id = -1
        record = {}
        objs = []
        for _, v in enumerate(imgs_anns):
            v = v.split()
            number_of_folder = int(ann[:4])
            number_of_frame = int(v[0])
            filename = os.path.join(img_dir,  'train/' + str(10000 * number_of_folder + number_of_frame))
            height, width = int(v[3]), int(v[4])
            if (int(v[1]) == 10000):
                continue
            if (prev_img_id != 10000 * number_of_folder + number_of_frame):
                if(objs != []):
                    record["annotations"] = deepcopy(objs)
                    dataset_dicts.append(deepcopy(record))
                    objs.clear()

            record["file_name"] = filename + '.png'
            record["image_id"] = 10000 * number_of_folder + number_of_frame
            record["height"] = height
            record["width"] = width

            rle2 = {"size": [height, width], "counts": v[5]}
            result_mask = decode(rle2)
            encoded_mask = encode(result_mask)
            result_bbox = toBbox(encoded_mask)

            contours = measure.find_contours(result_mask, 0.5)
            polygons = measure.approximate_polygon(np.flip(contours[0], axis=1), tolerance=0)

            obj = {
                "bbox": list(result_bbox),
                "bbox_mode": BoxMode.XYWH_ABS,
                "segmentation": rle2,    #[polygons.tolist()],
                "category_id": int(v[2]) - 1,
                "iscrowd": 0
            }
            objs.append(deepcopy(obj))
            prev_img_id = 10000 * number_of_folder + number_of_frame
        print("Done: ", ann)

    return dataset_dicts


from detectron2.data import DatasetCatalog, MetadataCatalog
dataset_dicts = get_KITTI_dicts("KITTI/")
#for d in ["train"]:
#    DatasetCatalog.register("KITTI_" + d, lambda d=d: get_KITTI_dicts("KITTI/"))
#    MetadataCatalog.get("KITTI_" + d).set(thing_classes=["car", "pedestrian"])
#KITTI_metadata = MetadataCatalog.get("KITTI_train")

import simplejson
simplejson.dump(dataset_dicts,open("instances_train.json",'w'))