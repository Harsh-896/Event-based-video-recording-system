# Event-based-video-recording-system

A Python-based video recording and event detection system with a web interface.  
This project allows you to record video streams, detect events (e.g. Vehicle or person detection), manage metadata, and view recordings from a simple dashboard.

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

#🚀 Features
- Record video streams
- Event detection (e.g., person detected)
- Save & manage video recordings
- Metadata storage
- Web dashboard to view and manage recordings
- Configurable settings

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
