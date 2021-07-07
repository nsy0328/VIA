import json
import os
from PIL import Image
import yaml
from typing import List,Dict

def viaReg2cocoReg(region:Dict
    ):
    """Convert VIA x,y to COCO annotation
    Extract super category infomation from via json (type : radio)

    Args:
        region (Dict): VIA annotation info (region_attributes)

    Returns:
        seg (List): COCO annotation
        bbox (List): Bounding box info ... Ex) [x, y, width, height]
        cat (Dict): categories info
    """
    x=region["shape_attributes"]["all_points_x"]
    y=region["shape_attributes"]["all_points_y"]
    cat = region["region_attributes"]
    seg=[]
    bbox=[min(x),min(y),max(x)-min(x),max(y)-min(y)]
    for i,j in zip(x,y):
        seg.extend([i,j])
    return seg,bbox,cat

def cocoReg2viaReg(seg:List
    ):
    """Convert COCO annotation to VIA x,y

    Args:
        seg (List): COCO annotation info

    Returns:
        x (List): VIA annotation (all_points_x)
        y (List): VIA annotation (all_points_y)
    """
    x,y = [],[]
    for i,s in enumerate(seg):
        if i%2 == 0:
            x.append(s)
        else:
            y.append(s)
    return x,y

def via2coco(images_path:str,
            via_path:str
            ,config_path:str
            )-> None:
    """Making COCO json from VIA json

    Args:
        images_path (str): Specify a path to the images Directory
        via_path (str): Specify a path to the VIA json file
        config_path (str): Specify a path to the config yaml file
    """
    with open(via_path,"r") as f:
        via = json.load(f)
    with open(config_path,"r") as f:
        config = yaml.safe_load(f)

    coco = {"info":[],"images":[],"annotations":[],"categories":[]}
    list_of_images=[]
    list_of_annotations=[]
    name_list=sorted(list(config["names"].keys()))
    reg_attr = config["region_attributes"]
    name2super = config["names"]
    anno_count=-1
    for i,image_name_with_size in enumerate(via.keys()):
        im = Image.open(images_path+"/"+via[image_name_with_size]["filename"])
        list_of_images.append({"id":i,"file_name":via[image_name_with_size]["filename"],"width":im.size[0],"height":im.size[1]})
        for region in via[image_name_with_size]["regions"]:
            anno_count+=1
            seg,bbox,cat=viaReg2cocoReg(region)
            for attr in reg_attr:
                cat_idx = name_list.index(cat["name"])+1 # index of names(category_id)
            list_of_annotations.append({"id":anno_count,"image_id":i,"category_id":cat_idx,"segmentation":[seg],"bbox":bbox,"iscrowd":0})

    list_of_categories=[{"supercategory":name2super[name],"id":i+1,"name":name} for i,name in enumerate(name_list)]
    coco["images"]=list_of_images
    coco["annotations"]=list_of_annotations
    coco["categories"]=list_of_categories

    with open(via_path[:-5]+"_coco.json","w") as f:
        json.dump(coco,f)

def coco2via(images_path:str,
            coco_path:str
            ,config_path:str
            )-> None:
    """Making VIA json from COCO json

    Args:
        images_path (str): Specify a path to the images Directory
        coco_path (str): Specify a path to the COCO json file
        config_path (str): Specify a path to the config yaml file
    """
    with open(coco_path,"r") as f:
        coco = json.load(f)
    with open(config_path,"r") as f:
        config = yaml.safe_load(f)
    vgg={}
    reg_attr = config["region_attributes"]
    images = coco["images"]
    annotations = coco["annotations"]
    category_with_id = {c["id"] : {attr : c[attr] for attr in reg_attr} for c in coco["categories"]}
    dic_img_anno = {img["id"] : [] for img in images}

    for a in annotations:
        dic_img_anno[a["image_id"]].append(a)

    for img in images:
        img_size = os.stat(os.path.join(images_path,img["file_name"])).st_size
        vgg[img["file_name"]+str(img_size)] = {"filename":img["file_name"],"size":img_size,"regions":[],"file_attributes":{}}
        for a in dic_img_anno[img["id"]]:
            region={"region_attributes":{attr:"" for attr in reg_attr},"shape_attributes":{"name":"polygon","all_points_x":[],"all_points_y":[]}}
            for attr in reg_attr:
                region["region_attributes"][attr]=category_with_id[a["category_id"]][attr]
            region["shape_attributes"]["all_points_x"],region["shape_attributes"]["all_points_y"] = cocoReg2viaReg(a["segmentation"][0])
            vgg[img["file_name"]+str(img_size)]["regions"].append(region)

    with open(coco_path[:-5]+"_vgg.json","w") as f:
        json.dump(vgg,f)
