# video_buffer.py - Video buffering and recording system

import cv2
import numpy as np
import threading
import time
from collections import deque
from datetime import datetime
import os
import config

class VideoBuffer:
    def __init__(self):
        self.buffer = deque(maxlen=config.BUFFER_SECONDS * config.FPS)
        self.cap = None
        self.is_recording = False
        self.buffer_lock = threading.Lock()
        self.frame_timestamps = deque(maxlen=config.BUFFER_SECONDS * config.FPS)
        
    def initialize_camera(self):
        """Initialize the camera/video capture"""
        try:
            self.cap = cv2.VideoCapture(0)  # 0 for default camera
            if not self.cap.isOpened():
                print("Error: Could not open camera")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, config.FPS)
            
            print(f"Camera initialized: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT} @ {config.FPS} FPS")
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def start_buffering(self):
        """Start continuous video buffering in a separate thread"""
        if not self.initialize_camera():
            return False
            
        self.is_recording = True
        self.buffer_thread = threading.Thread(target=self._buffer_loop, daemon=True)
        self.buffer_thread.start()
        print("Video buffering started...")
        return True
    
    def _buffer_loop(self):
        """Main buffering loop - runs in separate thread"""
        while self.is_recording:
            ret, frame = self.cap.read()
            if ret:
                current_time = datetime.now()
                
                with self.buffer_lock:
                    self.buffer.append(frame.copy())
                    self.frame_timestamps.append(current_time)
                
                # Control frame rate
                time.sleep(1.0 / config.FPS)
            else:
                print("Warning: Failed to read frame from camera")
                time.sleep(0.1)
    
    def save_event_clip(self, event_data):
        """Save a video clip when an event occurs"""
        try:
            # Generate filename with timestamp
            timestamp = datetime.now()
            filename = f"event_{timestamp.strftime('%Y%m%d_%H%M%S')}_{event_data['type']}.{config.VIDEO_FORMAT}"
            filepath = os.path.join(config.RECORDINGS_DIR, filename)
            
            # Get buffered frames
            with self.buffer_lock:
                buffered_frames = list(self.buffer)
                buffered_timestamps = list(self.frame_timestamps)
            
            if len(buffered_frames) == 0:
                print("Warning: No frames in buffer to save")
                return None
            
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*config.VIDEO_CODEC)
            out = cv2.VideoWriter(filepath, fourcc, config.FPS, 
                                (config.FRAME_WIDTH, config.FRAME_HEIGHT))
            
            if not out.isOpened():
                print("Error: Could not open video writer")
                return None
            
            # Write buffered frames (15 seconds before event)
            frames_written = 0
            for frame in buffered_frames:
                out.write(frame)
                frames_written += 1
            
            # Continue recording for POST_EVENT_SECONDS
            post_event_frames = config.POST_EVENT_SECONDS * config.FPS
            for _ in range(post_event_frames):
                if self.is_recording and self.cap is not None:
                    ret, frame = self.cap.read()
                    if ret:
                        out.write(frame)
                        frames_written += 1
                    time.sleep(1.0 / config.FPS)
            
            out.release()
            
            # Calculate actual duration
            actual_duration = frames_written / config.FPS
            
            clip_info = {
                'filename': filename,
                'filepath': filepath,
                'duration': actual_duration,
                'frames_count': frames_written,
                'event_data': event_data,
                'timestamp': timestamp
            }
            
            print(f"✅ Saved clip: {filename} ({actual_duration:.1f}s, {frames_written} frames)")
            return clip_info
            
        except Exception as e:
            print(f"Error saving clip: {e}")
            return None
    
    def get_current_frame(self):
        """Get the current frame from camera"""
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None
    
    def get_buffer_info(self):
        """Get information about current buffer state"""
        with self.buffer_lock:
            buffer_size = len(self.buffer)
            buffer_seconds = buffer_size / config.FPS if config.FPS > 0 else 0
            
        return {
            'frames_in_buffer': buffer_size,
            'seconds_buffered': round(buffer_seconds, 1),
            'max_buffer_seconds': config.BUFFER_SECONDS,
            'is_recording': self.is_recording
        }
    
    def stop_buffering(self):
        """Stop video buffering and cleanup"""
        self.is_recording = False
        
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            
        cv2.destroyAllWindows()
        print("Video buffering stopped")
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.stop_buffering()