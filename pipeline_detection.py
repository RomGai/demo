from inference_sdk import InferenceHTTPClient
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from PIL import Image
import os

# 按照距离屏幕中心最近的检测框，减少因为镜头畸变导致的视角移动误差
# 这里的每个函数都需要自己设置API
def detect_trunk_with_wid_hi(image_path, output_folder, x_aim, y_aim):
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=""
    )

    result = CLIENT.infer(image_path, model_id="mc-trunk/3")

    # 加载图像
    image = Image.open(image_path)

    # 绘制图像
    fig, ax = plt.subplots()
    ax.imshow(image)

    # 筛选出trunk对应的框
    trunk_boxes = [box for box in result['predictions'] if box['class'] == 'trunk']

    # 找到距离准心最近的框
    closest_box = min(trunk_boxes, key=lambda box: ((box['x'] - x_aim) ** 2 + (box['y'] - y_aim) ** 2) ** 0.5, default=None)

    if closest_box:
        x = closest_box['x'] - closest_box['width'] / 2
        y = closest_box['y'] - closest_box['height'] / 2
        width = closest_box['width']
        height = closest_box['height']

        # 创建矩形框
        rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # 注释面积
        area = width * height
        ax.text(x, y, f"Area: {area:.2f}", color='white', fontsize=10, backgroundcolor='red')

        # 设置输出路径
        output_filename = os.path.basename(image_path)  # 获取输入文件名
        output_filename = "Trunk_detect_" + output_filename
        output_path = os.path.join(output_folder, output_filename)  # 生成输出路径

        # 保存结果图像
        plt.axis('off') 
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # 返回距离准心最近的x和y值
        return closest_box['x'], closest_box['y'], closest_box['width'], closest_box['height']
    else:
        print("未检测到trunk")
        return None,None,None,None

# 按照距离屏幕中心最近的检测框，减少因为镜头畸变导致的视角移动误差
def detect_trunk(image_path, output_folder, x_aim, y_aim):
    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key=""
    )

    result = CLIENT.infer(image_path, model_id="mc-trunk/3")

    # 加载图像
    image = Image.open(image_path)

    # 绘制图像
    fig, ax = plt.subplots()
    ax.imshow(image)

    # 筛选出'class'为'trunk'的数据
    trunk_boxes = [box for box in result['predictions'] if box['class'] == 'trunk']

    # 找到距离准心最近的框
    closest_box = min(trunk_boxes, key=lambda box: ((box['x'] - x_aim) ** 2 + (box['y'] - y_aim) ** 2) ** 0.5, default=None)

    if closest_box:
        x = closest_box['x'] - closest_box['width'] / 2
        y = closest_box['y'] - closest_box['height'] / 2
        width = closest_box['width']
        height = closest_box['height']

        # 创建矩形框
        rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

        # 在框内显示面积
        area = width * height
        ax.text(x, y, f"Area: {area:.2f}", color='white', fontsize=10, backgroundcolor='red')

        # 生成输出文件名
        output_filename = os.path.basename(image_path)  # 获取输入文件名
        output_filename = "Trunk_detect_" + output_filename
        output_path = os.path.join(output_folder, output_filename)  # 生成输出路径

        # 保存结果图像
        plt.axis('off')  # 关闭坐标轴
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
        plt.close()

        # 返回距离准心最近的x和y值
        return closest_box['x'], closest_box['y']
    else:
        print("未检测到trunk")
        return None

# # 按照检测框最大面积（距离可能更近，目标可能更显著，遮挡物可能更少）
# def detect_trunk(image_path, output_folder):
#     CLIENT = InferenceHTTPClient(
#         api_url="https://detect.roboflow.com",
#         api_key=""
#     )
#
#     result = CLIENT.infer(image_path, model_id="mc-trunk/3")
#
#     # 加载图像
#     image = Image.open(image_path)
#
#     # 绘制图像
#     fig, ax = plt.subplots()
#     ax.imshow(image)
#
#     # 筛选出'class'为'trunk'的数据
#     trunk_boxes = [box for box in result['predictions'] if box['class'] == 'trunk']
#
#     # 找到面积最大的框
#     largest_area_box = max(trunk_boxes, key=lambda box: box['width'] * box['height'], default=None)
#
#     if largest_area_box:
#         x = largest_area_box['x'] - largest_area_box['width'] / 2
#         y = largest_area_box['y'] - largest_area_box['height'] / 2
#         width = largest_area_box['width']
#         height = largest_area_box['height']
#
#         # 创建矩形框
#         rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='r', facecolor='none')
#         ax.add_patch(rect)
#
#         # 在框内显示面积
#         area = width * height
#         ax.text(x, y, f"Area: {area:.2f}", color='white', fontsize=10, backgroundcolor='red')
#
#         # 生成输出文件名
#         output_filename = os.path.basename(image_path)  # 获取输入文件名
#         output_filename = "Trunk_detect_" + output_filename
#         output_path = os.path.join(output_folder, output_filename)  # 生成输出路径
#
#         # 保存结果图像
#         plt.axis('off')  # 关闭坐标轴
#         plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
#         plt.close()
#
#         # 返回面积最大的x和y值
#         return largest_area_box['x'], largest_area_box['y']
#     else:
#         print("未检测到trunk")
#         return None
#

# 按照最大置信度
# def detect_trunk(image_path, output_folder,step):
#     CLIENT = InferenceHTTPClient(
#         api_url="https://detect.roboflow.com",
#         api_key=""
#     )
#
#     result = CLIENT.infer(image_path, model_id="mc-trunk/3")
#
#     # 加载图像
#     image = Image.open(image_path)
#
#     # 绘制图像
#     fig, ax = plt.subplots()
#     ax.imshow(image)
#
#     # 筛选出'class'为'trunk'的数据
#     trunk_boxes = [box for box in result['predictions'] if box['class'] == 'trunk']
#
#     # 找到置信度最高的框
#     highest_confidence_box = max(trunk_boxes, key=lambda box: box['confidence'], default=None)
#
#     if highest_confidence_box:
#         x = highest_confidence_box['x'] - highest_confidence_box['width'] / 2
#         y = highest_confidence_box['y'] - highest_confidence_box['height'] / 2
#         width = highest_confidence_box['width']
#         height = highest_confidence_box['height']
#
#         # 创建矩形框
#         rect = patches.Rectangle((x, y), width, height, linewidth=2, edgecolor='r', facecolor='none')
#         ax.add_patch(rect)
#
#         # 在框内显示置信度
#         ax.text(x, y, f"{highest_confidence_box['confidence']:.2f}", color='white', fontsize=10, backgroundcolor='red')
#
#         # 生成输出文件名
#         output_filename = os.path.basename(image_path)  # 获取输入文件名
#         output_filename="Trunk_detect_"+output_filename
#         output_path = os.path.join(output_folder, output_filename)  # 生成输出路径
#
#         # 保存结果图像
#         plt.axis('off')  # 关闭坐标轴
#         plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
#         plt.close()
#
#         # 返回置信度最高的x和y值
#         return highest_confidence_box['x'], highest_confidence_box['y']
#     else:
#         print("未检测到trunk")
#         return None