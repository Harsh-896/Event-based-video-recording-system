# Mock AI event detection system

import random
import time
import threading
from datetime import datetime
import config

class MockEventDetector:
    def __init__(self):
        self.is_running = False
        self.detection_thread = None
        self.event_callback = None
        self.last_event_time = 0
        self.min_event_interval = 3  # Minimum seconds between events
        
    def set_event_callback(self, callback_function):
        """Set the callback function to call when an event is detected"""
        self.event_callback = callback_function
    
    def start_detection(self):
        """Start the mock event detection in a separate thread"""
        if self.is_running:
            print("Event detection is already running")
            return
            
        self.is_running = True
        self.detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
        self.detection_thread.start()
        print("🔍 Mock event detection started...")
        print(f"Event probability: {config.EVENT_PROBABILITY * 100:.1f}% per second")
    
    def _detection_loop(self):
        """Main detection loop - runs in separate thread"""
        while self.is_running:
            current_time = time.time()
            
            # Check if enough time has passed since last event
            if current_time - self.last_event_time >= self.min_event_interval:
                # Simulate event detection with configured probability
                if random.random() < config.EVENT_PROBABILITY:
                    event = self._generate_mock_event()
                    if self.event_callback:
                        self.event_callback(event)
                    self.last_event_time = current_time
            
            # Check every second
            time.sleep(1.0)
    
    def _generate_mock_event(self):
        """Generate a mock event with realistic data"""
        event_type = random.choice(config.EVENT_TYPES)
        confidence = round(random.uniform(config.MIN_CONFIDENCE, 0.98), 2)
        
        # Simulate bounding box coordinates (normalized 0-1)
        bbox = {
            'x': round(random.uniform(0.1, 0.7), 3),
            'y': round(random.uniform(0.1, 0.7), 3),
            'width': round(random.uniform(0.1, 0.3), 3),
            'height': round(random.uniform(0.1, 0.3), 3)
        }
        
        # Generate realistic GPS coordinates (around Delhi)
        lat = config.DEFAULT_LAT + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        lon = config.DEFAULT_LON + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        
        event = {
            'type': event_type,
            'confidence': confidence,
            'timestamp': datetime.now(),
            'bbox': bbox,
            'gps': {
                'latitude': round(lat, 6),
                'longitude': round(lon, 6)
            },
            'model_version': 'YOLOv8-mock',
            'detection_id': f"evt_{int(time.time())}"
        }
        
        # Print event detection (for debugging)
        if config.DEBUG:
            print(f"🚨 Event detected: {event_type} (confidence: {confidence})")
            print(f"   📍 GPS: {lat:.4f}, {lon:.4f}")
        
        return event
    
    def simulate_specific_event(self, event_type=None):
        """Manually trigger a specific event (for testing)"""
        if event_type is None:
            event_type = random.choice(config.EVENT_TYPES)
        elif event_type not in config.EVENT_TYPES:
            print(f"Warning: Unknown event type '{event_type}'. Using random type.")
            event_type = random.choice(config.EVENT_TYPES)
        
        # Create event with specified type
        confidence = round(random.uniform(config.MIN_CONFIDENCE, 0.98), 2)
        
        bbox = {
            'x': round(random.uniform(0.1, 0.7), 3),
            'y': round(random.uniform(0.1, 0.7), 3),
            'width': round(random.uniform(0.1, 0.3), 3),
            'height': round(random.uniform(0.1, 0.3), 3)
        }
        
        lat = config.DEFAULT_LAT + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        lon = config.DEFAULT_LON + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        
        event = {
            'type': event_type,
            'confidence': confidence,
            'timestamp': datetime.now(),
            'bbox': bbox,
            'gps': {
                'latitude': round(lat, 6),
                'longitude': round(lon, 6)
            },
            'model_version': 'YOLOv8-mock-manual',
            'detection_id': f"manual_evt_{int(time.time())}"
        }
        
        print(f"🎯 Manual event triggered: {event_type} (confidence: {confidence})")
        
        if self.event_callback:
            self.event_callback(event)
        
        return event
    
    def analyze_frame(self, frame):
        """
        Simulate real-time frame analysis (for future integration with real YOLO)
        Currently returns mock detection results
        """
        # This is where you would integrate real YOLO detection
        # For now, we'll return mock results occasionally
        
        if random.random() < 0.01:  # 1% chance per frame
            return self._generate_mock_event()
        
        return None
    
    def get_detection_stats(self):
        """Get statistics about detection system"""
        return {
            'is_running': self.is_running,
            'event_types': config.EVENT_TYPES,
            'detection_probability': config.EVENT_PROBABILITY,
            'min_confidence': config.MIN_CONFIDENCE,
            'min_event_interval': self.min_event_interval
        }
    
    def stop_detection(self):
        """Stop the event detection system"""
        self.is_running = False
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=2)
        print("Event detection stopped")

# Real YOLO Integration
class RealYOLODetector:
    """
    Real YOLO detection using OpenCV DNN module
    Works with pre-trained YOLO models
    """
    def __init__(self, weights_path=None, config_path=None, use_ultralytics=False):
        self.is_running = False
        self.detection_thread = None
        self.event_callback = None
        self.last_event_time = 0
        self.min_event_interval = 3
        
        # YOLO class names (COCO dataset)
        self.class_names = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck',
            'boat', 'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench',
            'bird', 'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra',
            'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
            'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove',
            'skateboard', 'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
            'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple', 'sandwich', 'orange',
            'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
            'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse',
            'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]
        
        # Mapping YOLO classes to our event types
        self.event_mapping = {
            'person': 'person_detected',
            'car': 'vehicle_detected',
            'truck': 'vehicle_detected',
            'bus': 'vehicle_detected',
            'motorcycle': 'vehicle_detected',
            'bicycle': 'vehicle_detected'
        }
        
        self.use_ultralytics = use_ultralytics
        self.net = None
        self.yolo_model = None
        
        # Try to initialize YOLO
        self.initialize_yolo(weights_path, config_path)
    
    def initialize_yolo(self, weights_path, config_path):
        """Initialize YOLO model"""
        try:
            if self.use_ultralytics:
                # Try to use Ultralytics YOLO
                try:
                    from ultralytics import YOLO
                    model_path = weights_path or 'yolov8n.pt'  # Will auto-download if not found
                    self.yolo_model = YOLO(model_path)
                    print(f" Ultralytics YOLO initialized with model: {model_path}")
                    return True
                except ImportError:
                    print(" Ultralytics not installed. Install with: pip install ultralytics")
                    print("Falling back to OpenCV DNN...")
                except Exception as e:
                    print(f"Failed to initialize Ultralytics YOLO: {e}")
                    print("Falling back to OpenCV DNN...")
            
            # Try OpenCV DNN approach
            if weights_path and config_path and os.path.exists(weights_path) and os.path.exists(config_path):
                self.net = cv2.dnn.readNet(weights_path, config_path)
                print(f" OpenCV YOLO initialized with weights: {weights_path}")
                return True
            else:
                print(" YOLO model files not found. Available options:")
                print("   1. Install ultralytics: pip install ultralytics")
                print("   2. Download YOLO files manually:")
                print("      - yolov4.weights + yolov4.cfg")
                print("      - yolov5s.onnx")
                print(" Using mock detection for now...")
                return False
                
        except Exception as e:
            print(f" Failed to initialize YOLO: {e}")
            print(" Using mock detection...")
            return False
    
    def set_event_callback(self, callback_function):
        """Set the callback function to call when an event is detected"""
        self.event_callback = callback_function
    
    def start_detection(self):
        """Start real-time YOLO detection"""
        if self.is_running:
            print("YOLO detection is already running")
            return
            
        self.is_running = True
        detection_method = "Real YOLO" if (self.net or self.yolo_model) else "Mock"
        print(f" {detection_method} detection started...")
    
    def detect_objects(self, frame):
        """Detect objects in a frame using real YOLO"""
        if self.yolo_model:
            return self._detect_with_ultralytics(frame)
        elif self.net:
            return self._detect_with_opencv(frame)
        else:
            # Fallback to mock detection
            return self._generate_mock_detection_from_frame(frame)
    
    def _detect_with_ultralytics(self, frame):
        """Detect using Ultralytics YOLO"""
        try:
            results = self.yolo_model(frame, verbose=False)
            events = []
            
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        confidence = float(box.conf[0])
                        
                        if confidence >= config.MIN_CONFIDENCE:
                            class_id = int(box.cls[0])
                            class_name = self.class_names[class_id]
                            
                            # Map to our event types
                            event_type = self.event_mapping.get(class_name, f"{class_name}_detected")
                            
                            # Get bounding box coordinates
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            # Convert to normalized coordinates
                            h, w = frame.shape[:2]
                            bbox = {
                                'x': round(x1 / w, 3),
                                'y': round(y1 / h, 3),
                                'width': round((x2 - x1) / w, 3),
                                'height': round((y2 - y1) / h, 3)
                            }
                            
                            event = self._create_event(event_type, confidence, bbox)
                            events.append(event)
            
            return events
            
        except Exception as e:
            print(f"Error in Ultralytics detection: {e}")
            return []
    
    def _detect_with_opencv(self, frame):
        """Detect using OpenCV DNN"""
        try:
            height, width = frame.shape[:2]
            
            # Create blob from image
            blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
            self.net.setInput(blob)
            
            # Run inference
            layer_names = self.net.getLayerNames()
            output_layers = [layer_names[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
            outputs = self.net.forward(output_layers)
            
            # Process detections
            boxes = []
            confidences = []
            class_ids = []
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > config.MIN_CONFIDENCE:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)
                        
                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
            
            # Apply non-maximum suppression
            indices = cv2.dnn.NMSBoxes(boxes, confidences, config.MIN_CONFIDENCE, 0.4)
            
            events = []
            if len(indices) > 0:
                for i in indices.flatten():
                    class_name = self.class_names[class_ids[i]]
                    event_type = self.event_mapping.get(class_name, f"{class_name}_detected")
                    
                    # Convert to normalized bbox
                    x, y, w, h = boxes[i]
                    bbox = {
                        'x': round(x / width, 3),
                        'y': round(y / height, 3),
                        'width': round(w / width, 3),
                        'height': round(h / height, 3)
                    }
                    
                    event = self._create_event(event_type, confidences[i], bbox)
                    events.append(event)
            
            return events
            
        except Exception as e:
            print(f"Error in OpenCV detection: {e}")
            return []
    
    def _generate_mock_detection_from_frame(self, frame):
        """Generate mock detection when real YOLO is not available"""
        # Simulate occasional detection based on frame content
        if random.random() < 0.02:  # 2% chance per frame
            return [self._create_mock_event()]
        return []
    
    def _create_event(self, event_type, confidence, bbox):
        """Create event object from detection"""
        # Generate GPS coordinates
        lat = config.DEFAULT_LAT + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        lon = config.DEFAULT_LON + random.uniform(-config.GPS_VARIANCE, config.GPS_VARIANCE)
        
        event = {
            'type': event_type,
            'confidence': round(confidence, 3),
            'timestamp': datetime.now(),
            'bbox': bbox,
            'gps': {
                'latitude': round(lat, 6),
                'longitude': round(lon, 6)
            },
            'model_version': self._get_model_version(),
            'detection_id': f"yolo_{int(time.time())}"
        }
        
        return event
    
    def _create_mock_event(self):
        """Create mock event when YOLO is not available"""
        event_type = random.choice(config.EVENT_TYPES)
        confidence = round(random.uniform(config.MIN_CONFIDENCE, 0.98), 2)
        
        bbox = {
            'x': round(random.uniform(0.1, 0.7), 3),
            'y': round(random.uniform(0.1, 0.7), 3),
            'width': round(random.uniform(0.1, 0.3), 3),
            'height': round(random.uniform(0.1, 0.3), 3)
        }
        
        return self._create_event(event_type, confidence, bbox)
    
    def _get_model_version(self):
        """Get model version string"""
        if self.yolo_model:
            return "YOLOv8-ultralytics"
        elif self.net:
            return "YOLO-OpenCV"
        else:
            return "YOLO-mock"
    
    def stop_detection(self):
        """Stop the detection system"""
        self.is_running = False
        print("YOLO detection stopped")

# Enhanced Event Detector with Real YOLO Support
class EnhancedEventDetector:
    """
    Enhanced event detector that can switch between mock and real YOLO
    """
    def __init__(self, use_real_yolo=False, weights_path=None, config_path=None):
        self.use_real_yolo = use_real_yolo
        
        if use_real_yolo:
            self.detector = RealYOLODetector(weights_path, config_path, use_ultralytics=True)
        else:
            self.detector = MockEventDetector()
        
        print(f"🎯 Enhanced Event Detector initialized ({'Real YOLO' if use_real_yolo else 'Mock'})")
    
    def set_event_callback(self, callback_function):
        """Set the callback function"""
        if hasattr(self.detector, 'set_event_callback'):
            self.detector.set_event_callback(callback_function)
    
    def start_detection(self):
        """Start detection"""
        return self.detector.start_detection()
    
    def stop_detection(self):
        """Stop detection"""
        return self.detector.stop_detection()
    
    def simulate_specific_event(self, event_type=None):
        """Simulate specific event"""
        if hasattr(self.detector, 'simulate_specific_event'):
            return self.detector.simulate_specific_event(event_type)
        else:
            # For real YOLO, create a mock event
            return self.detector._create_mock_event()
    
    def get_detection_stats(self):
        """Get detection stats"""
        if hasattr(self.detector, 'get_detection_stats'):
            return self.detector.get_detection_stats()
        else:
            return {
                'is_running': self.detector.is_running,
                'detection_method': 'Real YOLO',
                'model_version': self.detector._get_model_version()
            }