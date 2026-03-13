import os
from ultralytics import YOLO

def load_model(model_path="yolov8n.pt"):
    """
    Loads the YOLOv8n model, downloading it if necessary, and ensures it's in eval mode.
    """
    model = YOLO(model_path)
    # Set model to evaluation mode (optimization for CPU inference)
    model.eval()
    return model
