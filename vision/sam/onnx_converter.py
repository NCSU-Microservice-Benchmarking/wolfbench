import os

import torch
from ultralytics import YOLO  # 假设您使用的是 YOLOv8

# # 1. 加载 PyTorch 模型
# model = YOLO('yolov8n.pt')  # 加载预训练的 YOLOv8 模型
#
# # 2. 准备输入示例
# # 创建一个假数据作为模型的输入
# # 注意：输入的形状需要与模型期望的输入形状一致，例如 (batch_size, channels, height, width)
# dummy_input = torch.randn(1, 3, 640, 640)  # (1, 3, 640, 640) 为输入张量的形状
#
# # 3. 导出为 ONNX 格式
# # 设置导出 ONNX 文件的路径
# onnx_model_path = "yolov8n.onnx"
#
# # 使用 torch.onnx.export 将模型转换为 ONNX 格式
# torch.onnx.export(
#     model.model,  # 模型对象
#     dummy_input,  # 示例输入
#     onnx_model_path,  # 导出 ONNX 文件的路径
#     export_params=True,  # 是否导出模型参数
#     opset_version=11,  # ONNX opset 版本
#     do_constant_folding=True,  # 是否执行常量折叠优化
#     input_names=['input'],  # 输入张量的名称
#     output_names=['output'],  # 输出张量的名称
#     dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}  # 动态轴
# )
#
# print(f"ONNX 模型已成功导出到: {onnx_model_path}")

# Load the YOLOv8 model
model = YOLO("yolov8n-seg.pt")

# Export the model to ONNX format
model.export(format="onnx")  # creates 'yolov8n.onnx'

# Load the exported ONNX model
onnx_model = YOLO("yolov8n-seg.onnx")

def export_cloud_detection_model_to_onnx(model_path, output_folder, model_input_size):
    try:
        # model input size
        input_height = model_input_size[0]
        input_width = model_input_size[1]

        # check if model path exists
        if not os.path.exists(model_path):
            return True

        # # check device
        # device = torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
        # print("device: ", device)
        device = torch.device('cpu')

        # load model
        model_channel_file_path = model_path.replace('.pt', '_channels.txt')
        model = YOLO('yolov8n.pt')
        model.load_state_dict(torch.load(model_path))
        model.to(device)

        # prepare arguments
        dummy_input = torch.randn(1, 3, input_height, input_width, device=device)
        input_names = ["in"]
        output_names = ["out"]
        dynamic_axes = {'in': {0: 'batch'}, 'out': {0: 'batch'}}

        # make output directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        # get the onnx file output path
        output_path = os.path.join(output_folder, os.path.basename(model_path).replace('.pt', '.onnx'))

        torch.onnx.export(model, dummy_input, output_path, verbose=False, input_names=input_names,
                          output_names=output_names, dynamic_axes=dynamic_axes)
        return True
    except Exception as e:
        print(f'Error exporting model to ONNX: {e}')
        return False