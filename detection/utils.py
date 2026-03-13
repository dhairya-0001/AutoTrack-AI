import cv2
import yaml

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)
classes_list = config['model']['classes']

CLASS_NAMES = {
    0: 'person', 2: 'car', 3: 'motorcycle', 5: 'bus', 7: 'truck'
}

COLORS = {
    0: (255, 100, 100),   # person - Blue
    2: (100, 255, 100),   # car - Green
    3: (100, 100, 255),   # motorcycle - Red
    5: (255, 200, 100),   # bus - Cyan
    7: (255, 100, 200)    # truck - Purple
}

def draw_tracking_info(frame, tracks, trajectories, fps, total_count, active_count):
    # Iterate through tracks
    for track in tracks:
        if not track.is_confirmed() or track.time_since_update > config['processing'].get('frame_skip', 2):
            continue
        
        track_id = track.track_id
        ltrb = track.to_ltrb() # Left, Top, Right, Bottom
        x1, y1, x2, y2 = map(int, ltrb)
        
        cls = int(track.get_det_class()) if track.get_det_class() is not None else 0
        cls_name = CLASS_NAMES.get(cls, f"cls_{cls}")
        color = COLORS.get(cls, (0, 255, 255))
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw ID and class
        label = f"{cls_name.capitalize()} #{track_id}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw trajectory
        traj = trajectories.get(track_id, [])
        if len(traj) > 1:
            for i in range(1, len(traj)):
                cv2.line(frame, (int(traj[i-1][0]), int(traj[i-1][1])), 
                               (int(traj[i][0]), int(traj[i][1])), color, 2)
                
    # Draw Telemetry Overlay
    overlay_text = [
        f"FPS: {fps:.1f}",
        f"Total Unique Objects: {total_count}",
        f"Active Count: {active_count}"
    ]
    
    y_offset = 30
    for text in overlay_text:
        cv2.putText(frame, text, (15, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        y_offset += 30
        
    return frame
