# encoding: utf-8
"""
@author:  liaoxingyu
@contact: sherlockliao01@gmail.com
"""
import logging

from ignite.metrics import RunningAverage
from torch.nn import CrossEntropyLoss

from .dec_loss import DECLoss
from .smoth_loss import CrossEntropyLabelSmooth
from .triplet_loss import TripletLoss
from .center_loss import CenterLoss

logger = logging.getLogger("reid_baseline.loss")


class Loss:
    def __init__(self, cfg, num_classes, feat_dim):  # modified by arron

        self.cfg = cfg
        self.num_classes = num_classes
        self.loss_type = cfg.LOSS.LOSS_TYPE

        # ID loss
        if self.cfg.LOSS.IF_LABEL_SMOOTH:
            self.xent = CrossEntropyLabelSmooth(num_classes=self.num_classes)
            logger.info(f"Label smooth on, numclasses: {self.num_classes}")
        else:
            self.xent = CrossEntropyLoss()

        # m loss
        self.triplet = TripletLoss(self.cfg.LOSS.MARGIN)

        # cluster loss
        self.center_loss_weight = cfg.LOSS.CENTER_LOSS_WEIGHT
        self.center = CenterLoss(num_classes=self.num_classes, feat_dim=feat_dim)
        if cfg.LOSS.IF_DEC:
            self.dec = DECLoss()

        self.loss_function_map = {}
        self.make_loss()

    def make_loss(self):

        if 'softmax' in self.loss_type:
            def loss_function(score, feat, target):
                return self.xent(score, target)

            self.loss_function_map["softmax"] = loss_function

        if 'triplet' in self.loss_type:
            def loss_function(score, feat, target):
                return self.triplet(feat, target)

            self.loss_function_map["triplet"] = loss_function

        if self.cfg.LOSS.IF_WITH_CENTER:
            def loss_function(score, feat, target):
                return self.center_loss_weight * self.center(feat, target)

            self.loss_function_map["center"] = loss_function

        return self.loss_function_map
