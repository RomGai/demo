import torch
import cv2
import numpy as np
from PIL import Image
import os
from torchvision.transforms import Compose, Resize, ToTensor
import math

def get_depth_map(image_path, output_folder):
    # Load MiDaS model
    model_type = "DPT_Large"  # MiDaS v3 - Large
    midas = torch.hub.load("intel-isl/MiDaS", model_type)

    # Load transforms to match model
    transform = Compose([Resize(384), ToTensor()])

    # Load image using OpenCV and convert to RGB
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Convert the image from numpy array to PIL Image
    img = Image.fromarray(img)

    # Apply transforms and add batch dimension
    img_input = transform(img).unsqueeze(0)

    # Perform inference
    with torch.no_grad():
        prediction = midas(img_input)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.size[::-1],  # height, width order for size
            mode="bilinear",
            align_corners=False,
        ).squeeze()

    depth_map = prediction.numpy()

    # Normalize the depth map to the range [0, 255]
    depth_map = (depth_map - np.min(depth_map)) / (np.max(depth_map) - np.min(depth_map)) * 255

    # Convert the depth map to an unsigned 8-bit integer type
    depth_map_uint8 = depth_map.astype(np.uint8)

    # Get the image name and prepare the output path
    image_name = os.path.basename(image_path)
    depth_image_name = f"Depth_{image_name}"
    output_path = os.path.join(output_folder, depth_image_name)

    # Save the depth map to the specified folder
    cv2.imwrite(output_path, depth_map_uint8)
    print(f"Depth map saved as {output_path}")

def check_depth(image_path, log_folder,x, y):
    # 读取深度图像
    image_name = os.path.basename(image_path)
    image_path= f"{log_folder}/Depth_{image_name}"
    depth_image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

    if depth_image is None:
        raise ValueError(f"Error: Image at {image_path} could not be loaded.")

    # 检查坐标是否在图像范围内
    if x < 0 or y < 0 or x >= depth_image.shape[1] or y >= depth_image.shape[0]:
        raise ValueError(f"Error: Coordinates ({x}, {y}) are out of bounds for the image.")

    # 获取指定像素的深度值
    depth_value = depth_image[y, x]

    # 判断深度值是否大于35并返回对应的字符串(大于35就是小于5m)
    if depth_value > 40:
        return "小于"
    elif depth_value<=40 and depth_value>22:
        return "接近"
    else:
        return "大于"

def check_depth_by_box(width):
    min_width=width/math.sqrt(2)

    if min_width > 110:
        return "小于"
    elif min_width<=110 and min_width>65:
        return "接近"
    else:
        return "大于"