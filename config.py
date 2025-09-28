#Configuration settings for the video recording system

import os

# Video Settings
BUFFER_SECONDS = 15  # Seconds to buffer before event
POST_EVENT_SECONDS = 15  # Seconds to record after event
TOTAL_CLIP_SECONDS = BUFFER_SECONDS + POST_EVENT_SECONDS  # 30 seconds total
FPS = 20  # Frames per second (lower for better performance)
FRAME_WIDTH = 640  # Video width
FRAME_HEIGHT = 480  # Video height

# Event Detection Settings
EVENT_PROBABILITY = 0.05  # 5% chance per second for mock events
EVENT_TYPES = ["person_detected", "vehicle_detected", "accident_detected", "speeding_detected"]
MIN_CONFIDENCE = 0.7  

# File Settings
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
METADATA_DIR = os.path.join(BASE_DIR, "metadata")
VIDEO_FORMAT = "mp4"
VIDEO_CODEC = "mp4v"  

# GPS Settings (Simulated)
DEFAULT_LAT = 28.6139  # Delhi, India
DEFAULT_LON = 77.2090
GPS_VARIANCE = 0.001  # Random variance for simulation

# Metadata Settings
METADATA_FORMAT = "json"  

# System Settings
MAX_RECORDING_AGE_DAYS = 7  # Auto-delete recordings older than 7 days
MAX_STORAGE_GB = 2  # Maximum storage in GB

# Create directories if they don't exist
os.makedirs(RECORDINGS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# Debug settings
DEBUG = True
VERBOSE = True