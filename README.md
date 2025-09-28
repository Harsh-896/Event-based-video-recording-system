# Event-based-video-recording-system

A Python-based video recording and event detection system with a web interface.  
This project allows you to record video streams, detect events (e.g. Vehicle or person detection), manage metadata, and view recordings from a simple dashboard.

---

## 📂 Project Structure

Video_recorder_system/
├── source_code/
│ ├── main.py # Entry point for the system
│ ├── app.py # Web application (Flask)
│ ├── video_buffer.py # Handles video buffering
│ ├── event_detector.py # Detects events (motion/person)
│ ├── metadata_manager.py # Stores and manages metadata
│ ├── cli_interface.py # Command-line interface
│ ├── config.py # Configuration settings
│ ├── requirements.txt # Python dependencies
│ ├── Procfile # Deployment process (Heroku)
│ ├── runtime.txt # Runtime version info
│ └── templates/ # HTML templates
│ ├── index.html
│ ├── recordings.html
│ └── settings.html

##🚀 Features
- Record video streams
- Event detection (e.g., person detected)
- Save & manage video recordings
- Metadata storage
- Web dashboard to view and manage recordings
- Configurable settings
