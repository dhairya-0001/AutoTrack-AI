from collections import deque

class TrajectoryManager:
    def __init__(self, max_length=40):
        self.trajectories = {}
        self.max_length = max_length

    def update(self, track_id, center_x, center_y):
        if track_id not in self.trajectories:
            self.trajectories[track_id] = deque(maxlen=self.max_length)
        self.trajectories[track_id].append((center_x, center_y))
        
    def get_all(self):
        return self.trajectories
