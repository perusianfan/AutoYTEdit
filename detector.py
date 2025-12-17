import cv2
import numpy as np
import torch
from config import DETECTION_CONFIDENCE, PERSON_CLASS_ID, USE_GPU

class PersonDetector:
    def __init__(self):
        self.model = None
        self.device = self._get_device()
        self._load_model()

    def _get_device(self):
        if USE_GPU and torch.cuda.is_available():
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
            return "cuda"
        else:
            print("Using CPU")
            return "cpu"

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO("yolov8n.pt")
            self.model.to(self.device)
            print("YOLOv8 model loaded successfully")
        except Exception as e:
            print(f"Error loading YOLO model: {e}")
            self.model = None

    def detect(self, frame):
        if self.model is None:
            return []
        
        try:
            results = self.model(frame, verbose=False, device=self.device)
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    if cls == PERSON_CLASS_ID and conf >= DETECTION_CONFIDENCE:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        detections.append([x1, y1, x2, y2, conf, cls])
            
            return detections
        except Exception as e:
            print(f"Detection error: {e}")
            return []

    def get_person_mask(self, frame, detections):
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        for det in detections:
            x1, y1, x2, y2 = map(int, det[:4])
            mask[y1:y2, x1:x2] = 255
        
        return mask

    def track_main_person(self, detections):
        if not detections:
            return None
        
        largest = max(detections, key=lambda d: (d[2] - d[0]) * (d[3] - d[1]))
        return largest