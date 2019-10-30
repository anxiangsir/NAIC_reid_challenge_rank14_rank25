# encoding: utf-8
"""
@author:  sherlock
@contact: sherlockliao01@gmail.com
"""
from torchvision import transforms
import numpy as np
from PIL import Image
import pickle
import argparse
import os
import sys
import torch

from torch.backends import cudnn

sys.path.append('.')
from config import cfg
#from data import make_data_loader
#from engine.trainer import do_train, do_train_with_center
from modeling import build_model
#from layers import make_loss, make_loss_with_center
#from solver import make_optimizer, make_optimizer_with_center, WarmupMultiStepLR

from utils.logger import setup_logger



def main():
    parser = argparse.ArgumentParser(description="ReID Baseline Training")
    parser.add_argument(
        "--config_file", default="", help="path to config file", type=str
    )
    parser.add_argument("opts", help="Modify config options using the command-line", default=None,
                        nargs=argparse.REMAINDER)

    args = parser.parse_args()

    num_gpus = int(os.environ["WORLD_SIZE"]) if "WORLD_SIZE" in os.environ else 1

    if args.config_file != "":
        cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    cfg.freeze()

    output_dir = cfg.OUTPUT_DIR
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    logger = setup_logger("reid_baseline", output_dir, 0)
    logger.info("Using {} GPUS".format(num_gpus))
    logger.info(args)

    if args.config_file != "":
        logger.info("Loaded configuration file {}".format(args.config_file))
        with open(args.config_file, 'r') as cf:
            config_str = "\n" + cf.read()
            logger.info(config_str)
    logger.info("Running with config:\n{}".format(cfg))

    if cfg.MODEL.DEVICE == "cuda":
        os.environ['CUDA_VISIBLE_DEVICES'] = cfg.MODEL.DEVICE_ID    # new add by gu
    cudnn.benchmark = True
    #model = train(cfg)
    model = build_model(cfg, 3815)
    model.load_state_dict(torch.load(cfg.MODEL.PRETRAIN_PATH))
    return model

def get_image(filename,model):

    img = Image.open(filename).convert('RGB')

    mean = [0.485, 0.456, 0.406]

    std = [0.229, 0.224, 0.225]

    img = transforms.Resize([256, 128])(img)
    #img = transforms.Resize([300, 300])(img) 
    img = transforms.ToTensor()(img)

    img = transforms.Normalize(mean,std)(img)
 
    img = img.unsqueeze(0)

    img = img.cuda()

    feature = model(img)
    
    #print(feature)

    return feature

if __name__ == '__main__':
    model = main()
    model = model.eval()

    model = model.cuda()
 
    result = []

    #path = os.listdir('/data/fyf/MVB_val/Image/gallery')
    #root = '/data/fyf/MVB_val/Image/gallery'
    
    root = '../DukeMTMC-reID/DukeMTMC-reID/query' 
    #root = '../train_split/split2/query' 
    path = os.listdir(root)
    for i in range(len(path)):
        #print(i)
        name = os.path.join(root,path[i])

        feature = get_image(name,model)

        feature = feature.data.cpu().numpy()
        #print(feature)
        
        result.append([feature, path[i]])
    #print(cfg.OUTPUT_DIR)
    pickle.dump(result, open(cfg.OUTPUT_DIR+'/query_train_feature.feat','wb'))

    #print(feature)