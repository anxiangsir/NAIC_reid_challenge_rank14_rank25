# encoding: utf-8
"""
@author:  liaoxingyu
@contact: liaoxingyu2@jd.com
"""

import torchvision.transforms as T

from .transforms import RandomErasing
from .transforms import Random2DTranslation
from .transforms import RandomPatch


def build_transforms(cfg, is_train=True):
    normalize_transform = T.Normalize(mean=cfg.INPUT.PIXEL_MEAN, std=cfg.INPUT.PIXEL_STD)
    if is_train:
        transform = T.Compose([
            T.Resize(cfg.INPUT.SIZE_TRAIN),
            T.RandomHorizontalFlip(p=cfg.INPUT.PROB),
            T.Pad(cfg.INPUT.PADDING),
            T.RandomCrop(cfg.INPUT.SIZE_TRAIN),
            RandomPatch(prob_happen=cfg.INPUT.RANDOM_PATCH_PROB, patch_max_area=0.1677),
            T.ToTensor(),
            normalize_transform
        ])
        return transform

    else:
        transform = T.Compose([
            T.Resize(cfg.INPUT.SIZE_TEST),
            T.ToTensor(),
            normalize_transform
        ])

    return transform
