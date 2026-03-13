import torch
import yaml
from detection.model_loader import load_model

class ObjectDetector:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
        
        yolo_path = self.config['model']['yolo_path']
        self.model = load_model(yolo_path)
        self.classes = self.config['model']['classes']
        self.conf_thresh = self.config['model']['confidence_threshold']

    def detect(self, frame):
        # Optimization: torch.no_grad()
        with torch.no_grad():
            results = self.model.predict(
                source=frame,
                conf=self.conf_thresh,
                classes=self.classes,
                verbose=False
            )
        
        # Format for DeepSORT: List of [ [x_min, y_min, w, h], confidence, class_id ]
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())
                
                w = x2 - x1
                h = y2 - y1
                detections.append([[x1, y1, w, h], conf, cls])
                
        return detections
