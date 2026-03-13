from deep_sort_realtime.deepsort_tracker import DeepSort
import yaml

class Tracker:
    def __init__(self, config_path="config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)
            
        tracker_cfg = self.config['tracking']
        self.tracker = DeepSort(
            max_age=tracker_cfg.get('max_age', 30),
            n_init=tracker_cfg.get('n_init', 3),
            nn_budget=tracker_cfg.get('nn_budget', 100)
        )

    def update(self, detections, frame):
        """
        detections: list of [[x_min, y_min, w, h], conf, class_id]
        frame: BGR image numpy array
        """
        tracks = self.tracker.update_tracks(detections, frame=frame)
        return tracks
