import time
import cv2
import yaml
from detection.detector import ObjectDetector
from tracking.deepsort_tracker import Tracker
from tracking.trajectory import TrajectoryManager
from detection.utils import draw_tracking_info

class TrackManager:
    def __init__(self, config_path="config.yaml", n_init_override=None):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        self.detector = ObjectDetector(config_path)
        
        # Manually construct the Tracker to allow n_init_override
        tracker_cfg = self.config['tracking']
        n_init = n_init_override if n_init_override is not None else tracker_cfg.get('n_init', 3)
        self.tracker = Tracker(config_path)
        self.tracker.tracker.tracker.n_init = n_init  # deep_sort_realtime has .tracker.tracker
        
        self.trajectory_manager = TrajectoryManager(max_length=40)
        
        self.frame_skip = self.config['processing']['frame_skip']
        self.target_width = self.config['processing']['target_width']
        self.target_height = self.config['processing']['target_height']
        
        self.total_unique_objects = set()
        self.frame_count = 0
        self.prev_time = time.time()
        self.last_tracks = []

    def process_frame(self, frame):
        self.frame_count += 1
        
        # Optimization: Resizing and Resolution Scaling
        frame = cv2.resize(frame, (self.target_width, self.target_height))
        
        # Optimization: Frame skipping (process every nth frame)
        if self.frame_count % self.frame_skip == 0 or self.frame_count == 1:
            detections = self.detector.detect(frame)
            tracks = self.tracker.update(detections, frame)
            self.last_tracks = tracks
        else:
            # Update tracks without new detections. DeepSORT's Kalman filter will predict new positions.
            tracks = self.tracker.update([], frame)
            self.last_tracks = tracks

        active_count = 0
        for track in tracks:
            if not track.is_confirmed() or track.time_since_update > self.frame_skip:
                continue
                
            active_count += 1
            track_id = track.track_id
            self.total_unique_objects.add(track_id)
            
            ltrb = track.to_ltrb() # Left, Top, Right, Bottom
            x1, y1, x2, y2 = map(int, ltrb)
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            
            self.trajectory_manager.update(track_id, center_x, center_y)

        # FPS calculation
        curr_time = time.time()
        fps = 1 / (curr_time - self.prev_time + 1e-6) # prevent divide by zero
        self.prev_time = curr_time
        
        # Draw Output
        processed_frame = draw_tracking_info(
            frame, 
            tracks, 
            self.trajectory_manager.get_all(),
            fps, 
            len(self.total_unique_objects),
            active_count
        )
        
        # Return telemetry as well
        stats = {
            "fps": round(fps, 1),
            "total_count": len(self.total_unique_objects),
            "active_count": active_count
        }
        
        return processed_frame, stats
