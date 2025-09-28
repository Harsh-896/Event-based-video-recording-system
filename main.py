# main.py - Main application for Event-Based Video Recording System

import sys
import time
import signal
import threading
from datetime import datetime

from video_buffer import VideoBuffer
from event_detector import MockEventDetector
from metadata_manager import MetadataManager
from cli_interface import CLIInterface
import config

class EventBasedRecordingSystem:
    def __init__(self):
        self.video_buffer = VideoBuffer()
        self.event_detector = MockEventDetector()
        self.metadata_manager = MetadataManager()
        self.is_running = False
        self.events_detected = 0
        self.clips_saved = 0
        
    def on_event_detected(self, event_data):
        """Callback function when an event is detected"""
        self.events_detected += 1
        
        print(f"\n🚨 EVENT DETECTED #{self.events_detected}")
        print(f"   Type: {event_data['type']}")
        print(f"   Confidence: {event_data['confidence']:.2f}")
        print(f"   GPS: {event_data['gps']['latitude']:.4f}, {event_data['gps']['longitude']:.4f}")
        print(f"   Time: {event_data['timestamp'].strftime('%H:%M:%S')}")
        print("   📹 Saving video clip...")
        
        # Save video clip
        clip_info = self.video_buffer.save_event_clip(event_data)
        
        if clip_info:
            # Save metadata
            metadata = self.metadata_manager.save_event_metadata(clip_info)
            if metadata:
                self.clips_saved += 1
                print(f"   ✅ Clip saved successfully! (Total clips: {self.clips_saved})")
            else:
                print("   ❌ Failed to save metadata")
        else:
            print("   ❌ Failed to save video clip")
    
    def start_system(self):
        """Start the entire recording system"""
        print("\n🚀 Starting Event-Based Video Recording System...")
        
        # Start video buffering
        if not self.video_buffer.start_buffering():
            print("❌ Failed to start video buffering")
            return False
        
        # Set up event detection callback
        self.event_detector.set_event_callback(self.on_event_detected)
        
        # Start event detection
        self.event_detector.start_detection()
        
        self.is_running = True
        print("✅ System started successfully!")
        
        # Print system status
        buffer_info = self.video_buffer.get_buffer_info()
        detection_stats = self.event_detector.get_detection_stats()
        
        print(f"\n📊 System Configuration:")
        print(f"   Buffer: {config.BUFFER_SECONDS}s before + {config.POST_EVENT_SECONDS}s after = {config.TOTAL_CLIP_SECONDS}s clips")
        print(f"   Resolution: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT} @ {config.FPS} FPS")
        print(f"   Event probability: {detection_stats['detection_probability']*100:.1f}% per second")
        print(f"   Event types: {', '.join(detection_stats['event_types'])}")
        print(f"   Storage: {config.RECORDINGS_DIR}")
        
        return True
    
    def stop_system(self):
        """Stop the recording system"""
        print(f"\n🛑 Stopping system...")
        
        self.is_running = False
        
        # Stop event detection
        self.event_detector.stop_detection()
        
        # Stop video buffering
        self.video_buffer.stop_buffering()
        
        print(f"📊 Session Summary:")
        print(f"   Events detected: {self.events_detected}")
        print(f"   Clips saved: {self.clips_saved}")
        print("✅ System stopped successfully")
    
    def run_interactive_mode(self):
        """Run in interactive mode with manual event triggering"""
        if not self.start_system():
            return
        
        print(f"\n🎮 Interactive Mode Started!")
        print(f"Commands:")
        print(f"  'trigger' or 't' - Manually trigger an event")
        print(f"  'trigger <event_type>' - Trigger specific event type")
        print(f"  'status' or 's' - Show system status")
        print(f"  'stats' - Show session statistics")
        print(f"  'quit' or 'q' - Stop system and exit")
        print(f"\nSystem is running... Events will be detected automatically.")
        print(f"You can also manually trigger events using the commands above.\n")
        
        try:
            while self.is_running:
                user_input = input(">> ").strip().lower()
                
                if user_input in ['quit', 'q', 'exit']:
                    break
                elif user_input in ['trigger', 't']:
                    event = self.event_detector.simulate_specific_event()
                    print(f"🎯 Manually triggered: {event['type']}")
                elif user_input.startswith('trigger '):
                    event_type = user_input.split(' ', 1)[1]
                    event = self.event_detector.simulate_specific_event(event_type)
                elif user_input in ['status', 's']:
                    self.print_system_status()
                elif user_input == 'stats':
                    self.print_session_stats()
                elif user_input == 'help':
                    print(f"\nAvailable commands:")
                    print(f"  trigger, t - Trigger random event")
                    print(f"  trigger <type> - Trigger specific event")
                    print(f"  status, s - Show system status")
                    print(f"  stats - Show session statistics")
                    print(f"  quit, q - Exit")
                elif user_input:
                    print(f"Unknown command: {user_input}. Type 'help' for commands.")
                
        except KeyboardInterrupt:
            pass
        
        self.stop_system()
    
    def run_automatic_mode(self, duration_minutes=5):
        """Run in automatic mode for specified duration"""
        if not self.start_system():
            return
        
        print(f"\n⏰ Automatic Mode: Running for {duration_minutes} minutes...")
        print(f"Press Ctrl+C to stop early")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time and self.is_running:
                remaining = int(end_time - time.time())
                if remaining % 30 == 0:  # Status update every 30 seconds
                    print(f"⏳ {remaining//60}:{remaining%60:02d} remaining - "
                          f"Events: {self.events_detected}, Clips: {self.clips_saved}")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⏹️ Stopped by user")
        
        self.stop_system()
    
    def print_system_status(self):
        """Print current system status"""
        buffer_info = self.video_buffer.get_buffer_info()
        
        print(f"\n📊 System Status:")
        print(f"   Running: {self.is_running}")
        print(f"   Buffer: {buffer_info['frames_in_buffer']} frames ({buffer_info['seconds_buffered']}s)")
        print(f"   Events detected: {self.events_detected}")
        print(f"   Clips saved: {self.clips_saved}")
        print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
    
    def print_session_stats(self):
        """Print session statistics"""
        metadata_stats = self.metadata_manager.get_statistics()
        
        print(f"\n📈 Session Statistics:")
        print(f"   This session - Events: {self.events_detected}, Clips: {self.clips_saved}")
        print(f"   Total recorded - Events: {metadata_stats['total_events']}")
        print(f"   Total storage: {metadata_stats['total_storage_mb']} MB")
        print(f"   Average confidence: {metadata_stats['average_confidence']:.2f}")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n⏹️ Interrupt received, shutting down...')
    sys.exit(0)

def main():
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎥 Event-Based Video Recording System")
    print("=" * 50)
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python main.py interactive    - Interactive mode with manual triggers")
        print("  python main.py auto [minutes] - Automatic mode (default 5 minutes)")
        print("  python main.py cli           - Command line interface for viewing recordings")
        print("  python main.py test          - Test system components")
        sys.exit(1)
    
    mode = sys.argv[1].lower()
    
    if mode == 'interactive':
        system = EventBasedRecordingSystem()
        system.run_interactive_mode()
        
    elif mode == 'auto':
        duration = 5  # Default 5 minutes
        if len(sys.argv) > 2:
            try:
                duration = int(sys.argv[2])
            except ValueError:
                print("❌ Invalid duration. Using default 5 minutes.")
        
        system = EventBasedRecordingSystem()
        system.run_automatic_mode(duration)
        
    elif mode == 'cli':
        cli = CLIInterface()
        cli.run()
        
    elif mode == 'test':
        # Test system components
        print("🧪 Testing system components...")
        
        # Test video buffer
        print("\n1. Testing video buffer...")
        buffer = VideoBuffer()
        if buffer.initialize_camera():
            print("✅ Camera initialized successfully")
            buffer.stop_buffering()
        else:
            print("❌ Camera initialization failed")
        
        # Test event detection
        print("\n2. Testing event detection...")
        detector = MockEventDetector()
        test_event = detector._generate_mock_event()
        print(f"✅ Generated test event: {test_event['type']} (confidence: {test_event['confidence']})")
        
        # Test metadata
        print("\n3. Testing metadata manager...")
        metadata_mgr = MetadataManager()
        stats = metadata_mgr.get_statistics()
        print(f"✅ Metadata system working. Total events: {stats['total_events']}")
        
        print("\n✅ All tests completed!")
        
    else:
        print(f"❌ Unknown mode: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()