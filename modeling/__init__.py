# encoding: utf-8
"""
@author:  sherlock
@contact: sherlockliao01@gmail.com
"""

from .baseline import Baseline


def build_model(cfg, num_classes):
    model = Baseline(
        num_classes=num_classes,
        last_stride=cfg.MODEL.LAST_STRIDE,
        model_path=cfg.MODEL.PRETRAIN_PATH,
        model_name=cfg.MODEL.NAME,
        pretrain_choice=cfg.MODEL.PRETRAIN_CHOICE)
    return model
