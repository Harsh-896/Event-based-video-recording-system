# Event-based-video-recording-system

An intelligent video recording system that uses AI event detection to capture only relevant footage, reducing storage costs by 90% while maintaining complete incident context. Designed for fleet management, smart cities, and industrial monitoring.
---

## 📂 Project Structure
```bash
video_recorder_system/
├── 📁 source_code/
│   ├── main.py
│   ├── web_app.py
│   ├── video_buffer.py
│   ├── event_detector.py
│   ├── metadata_manager.py
│   ├── cli_interface.py
│   ├── config.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── runtime.txt
│   └── templates/
│       ├── index.html
│       ├── recordings.html
│       └── settings.html
├── 📁 demo_materials/
│   ├── demo_video.mp4
│   ├── screenshots/
│   ├── sample_recordings/ (optional)
│   └── system_demo.gif
├── 📁 documentation/
│   ├── README.md
│   ├── SETUP_GUIDE.md
│   ├── API_DOCUMENTATION.md
│   └── DEPLOYMENT_GUIDE.md
└── 📁 deployment/
    ├── docker-compose.yml
    ├── Dockerfile
    └── railway_deploy.sh
```

# Core Components
-Video Buffer System: Continuous 15-second circular buffer using efficient deque implementation
-AI Event Detection: Mock YOLO integration with real YOLO capabilities for production
-Intelligent Recording: Captures 30-second clips (15s before + 15s after events)
-Metadata Management: GPS coordinates, confidence scores, timestamps, and event classification
-Web Interface: Professional Flask dashboard for remote monitoring and management
-CLI Interface: Command-line tools for system administration and data analysis
---

# Adding New Event Types

Update EVENT_TYPES in config.py
Modify detection logic in event_detector.py
Update web interface trigger buttons

Database Integration
Replace JSON storage in metadata_manager.py with:

SQLite for development
PostgreSQL/MySQL for production
MongoDB for document-based storage

Real YOLO Integration
Install: pip install ultralytics
Use RealYOLODetector class in event_detector.py
Set use_real_yolo=True in system initialization
---
