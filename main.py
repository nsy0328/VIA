import sys
import argparse
from vgg_coco import *

if __name__ =="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('json_format', default="via", help='Specify the format of original json file: via or coco; Defalut: via')
    parser.add_argument('images_dir', help='Specify a path to the images Directory')
    parser.add_argument('original_json', help='Specify a path to the json file')
    parser.add_argument('config',default="/tutorial/configs/config.yaml", help='Specify a path to the config.yaml')
    args = parser.parse_args()

    if args.json_format=="via":
        via2coco(args.images_dir,args.original_json,args.config)
        print("="*20 + "END" +"="*20)
    elif args.json_format=="coco":
        coco2via(args.images_dir,args.original_json,args.config)
        print("="*20 + "END" +"="*20)
    else:
        print('Error: the first argument, json_format should be vgg or coco')
        sys.exit()
