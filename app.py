# web_app.py - Flask web interface for Event-Based Video Recording System

from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for
import threading
import time
import os
import json
from datetime import datetime
import base64
import cv2

from video_buffer import VideoBuffer
from event_detector import MockEventDetector
from metadata_manager import MetadataManager
import config

app = Flask(__name__)

# Global system components
system = None
system_thread = None
is_system_running = False

class WebVideoRecordingSystem:
    def __init__(self):
        self.video_buffer = VideoBuffer()
        self.event_detector = MockEventDetector()
        self.metadata_manager = MetadataManager()
        self.is_running = False
        self.events_detected = 0
        self.clips_saved = 0
        self.start_time = None
        self.latest_event = None
        
    def on_event_detected(self, event_data):
        """Callback function when an event is detected"""
        self.events_detected += 1
        self.latest_event = event_data
        
        # Save video clip
        clip_info = self.video_buffer.save_event_clip(event_data)
        
        if clip_info:
            # Save metadata
            metadata = self.metadata_manager.save_event_metadata(clip_info)
            if metadata:
                self.clips_saved += 1
        
    def start_system(self):
        """Start the recording system"""
        if self.is_running:
            return {"status": "error", "message": "System is already running"}
            
        # Start video buffering
        if not self.video_buffer.start_buffering():
            return {"status": "error", "message": "Failed to start video buffering"}
        
        # Set up event detection callback
        self.event_detector.set_event_callback(self.on_event_detected)
        
        # Start event detection
        self.event_detector.start_detection()
        
        self.is_running = True
        self.start_time = datetime.now()
        self.events_detected = 0
        self.clips_saved = 0
        
        return {"status": "success", "message": "System started successfully"}
    
    def stop_system(self):
        """Stop the recording system"""
        if not self.is_running:
            return {"status": "error", "message": "System is not running"}
            
        self.is_running = False
        
        # Stop event detection
        self.event_detector.stop_detection()
        
        # Stop video buffering
        self.video_buffer.stop_buffering()
        
        return {"status": "success", "message": "System stopped successfully"}
    
    def trigger_event(self, event_type=None):
        """Manually trigger an event"""
        if not self.is_running:
            return {"status": "error", "message": "System is not running"}
        
        event = self.event_detector.simulate_specific_event(event_type)
        return {"status": "success", "event": event, "message": f"Triggered {event['type']} event"}
    
    def get_status(self):
        """Get current system status"""
        buffer_info = self.video_buffer.get_buffer_info() if self.is_running else {}
        
        runtime = None
        if self.start_time and self.is_running:
            runtime = int((datetime.now() - self.start_time).total_seconds())
        
        return {
            "is_running": self.is_running,
            "events_detected": self.events_detected,
            "clips_saved": self.clips_saved,
            "runtime_seconds": runtime,
            "buffer_info": buffer_info,
            "latest_event": self.latest_event
        }
    
    def get_current_frame(self):
        """Get current camera frame as base64 encoded image"""
        if not self.is_running:
            return None
            
        frame = self.video_buffer.get_current_frame()
        if frame is not None:
            # Resize frame for web display
            frame_small = cv2.resize(frame, (320, 240))
            
            # Encode as JPEG
            ret, buffer = cv2.imencode('.jpg', frame_small)
            if ret:
                # Convert to base64
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                return f"data:image/jpeg;base64,{frame_base64}"
        
        return None

# Initialize global system
system = WebVideoRecordingSystem()

@app.route('/')
def index():
    """Main dashboard"""
    try:
        return render_template('index.html')
    except:
        # Fallback if template not found
        return """
        <html>
        <head><title>Video Recording System</title></head>
        <body style="font-family: Arial; padding: 20px; background: #f0f0f0;">
            <h1>🎥 Event-Based Video Recording System</h1>
            <p>Templates not found. Please create the templates folder and HTML files.</p>
            <div>
                <button onclick="fetch('/api/start', {method: 'POST'})">Start System</button>
                <button onclick="fetch('/api/stop', {method: 'POST'})">Stop System</button>
                <button onclick="fetch('/api/trigger', {method: 'POST'})">Trigger Event</button>
            </div>
            <div id="status"></div>
            <script>
                setInterval(async () => {
                    const response = await fetch('/api/status');
                    const status = await response.json();
                    document.getElementById('status').innerHTML = 
                        `<p>Running: ${status.is_running}<br>
                         Events: ${status.events_detected}<br>
                         Clips: ${status.clips_saved}</p>`;
                }, 1000);
            </script>
        </body>
        </html>
        """

@app.route('/api/status')
def api_status():
    """Get system status"""
    return jsonify(system.get_status())

@app.route('/api/start', methods=['POST'])
def api_start():
    """Start the recording system"""
    global is_system_running
    result = system.start_system()
    if result["status"] == "success":
        is_system_running = True
    return jsonify(result)

@app.route('/api/stop', methods=['POST'])
def api_stop():
    """Stop the recording system"""
    global is_system_running
    result = system.stop_system()
    if result["status"] == "success":
        is_system_running = False
    return jsonify(result)

@app.route('/api/trigger', methods=['POST'])
def api_trigger():
    """Trigger an event manually"""
    event_type = request.json.get('event_type') if request.json else None
    result = system.trigger_event(event_type)
    return jsonify(result)

@app.route('/api/video_feed')
def video_feed():
    """Get current video frame"""
    frame = system.get_current_frame()
    if frame:
        return jsonify({"frame": frame})
    return jsonify({"frame": None})

@app.route('/recordings')
def recordings():
    """View recordings page"""
    return render_template('recordings.html')

@app.route('/api/recordings')
def api_recordings():
    """Get all recordings"""
    events = system.metadata_manager.get_all_events()
    return jsonify(events)

@app.route('/api/recordings/<int:event_id>')
def api_recording_detail(event_id):
    """Get recording details"""
    event = system.metadata_manager.get_event_by_id(event_id)
    if event:
        return jsonify(event)
    return jsonify({"error": "Recording not found"}), 404

@app.route('/api/statistics')
def api_statistics():
    """Get system statistics"""
    stats = system.metadata_manager.get_statistics()
    return jsonify(stats)

@app.route('/download/<int:event_id>')
def download_recording(event_id):
    """Download a recording"""
    event = system.metadata_manager.get_event_by_id(event_id)
    if event and os.path.exists(event['filepath']):
        return send_file(event['filepath'], as_attachment=True, 
                        download_name=event['filename'])
    return jsonify({"error": "Recording not found"}), 404

@app.route('/api/search')
def api_search():
    """Search recordings"""
    query = request.args.get('q', '')
    if query:
        results = system.metadata_manager.search_events(query)
        return jsonify(results)
    return jsonify([])

@app.route('/api/filter')
def api_filter():
    """Filter recordings by type"""
    event_type = request.args.get('type')
    if event_type:
        results = system.metadata_manager.get_events_by_type(event_type)
        return jsonify(results)
    return jsonify([])

@app.route('/settings')
def settings():
    """Settings page"""
    return render_template('settings.html')

@app.route('/api/config')
def api_config():
    """Get current configuration"""
    config_data = {
        'BUFFER_SECONDS': config.BUFFER_SECONDS,
        'POST_EVENT_SECONDS': config.POST_EVENT_SECONDS,
        'FPS': config.FPS,
        'FRAME_WIDTH': config.FRAME_WIDTH,
        'FRAME_HEIGHT': config.FRAME_HEIGHT,
        'EVENT_PROBABILITY': config.EVENT_PROBABILITY,
        'EVENT_TYPES': config.EVENT_TYPES,
        'MIN_CONFIDENCE': config.MIN_CONFIDENCE,
        'VIDEO_FORMAT': config.VIDEO_FORMAT
    }
    return jsonify(config_data)

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("🌐 Starting Web Interface...")
    print("📱 Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)