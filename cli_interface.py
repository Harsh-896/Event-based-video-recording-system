#  Command Line Interface for managing recordings

import os
import sys
from datetime import datetime
from metadata_manager import MetadataManager
import config

class CLIInterface:
    def __init__(self):
        self.metadata_manager = MetadataManager()
    
    def print_banner(self):
        """Print application banner"""
        print("\n" + "="*60)
        print("Event-Based Video Recording System")
        print("AI-Powered Fleet & Driver Monitoring")
        print("="*60)
    
    def print_menu(self):
        """Print main menu options"""
        print("\n Available Commands:")
        print("1. List all events")
        print("2. Show event details")
        print("3. Filter events by type")
        print("4. Show recent events")
        print("5. Search events")
        print("6. Show statistics")
        print("7. Export metadata")
        print("8. Cleanup old events")
        print("9. Show system status")
        print("0. Exit")
    
    def list_all_events(self):
        """List all recorded events"""
        events = self.metadata_manager.get_all_events()
        
        if not events:
            print("\n📭 No events recorded yet.")
            return
        
        print(f"\n All Recorded Events ({len(events)} total):")
        print("-" * 80)
        print(f"{'ID':<4} {'Type':<20} {'Confidence':<10} {'Duration':<10} {'Date & Time':<20}")
        print("-" * 80)
        
        for event in events:
            timestamp = datetime.fromisoformat(event['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d %H:%M')
            print(f"{event['id']:<4} {event['event']['type']:<20} {event['event']['confidence']:<10.2f} "
                  f"{event['duration']:<10.1f}s {date_str:<20}")
    
    def show_event_details(self):
        """Show detailed information about a specific event"""
        try:
            event_id = int(input("\nEnter event ID: "))
            event = self.metadata_manager.get_event_by_id(event_id)
            
            if not event:
                print(f"Event with ID {event_id} not found.")
                return
            
            timestamp = datetime.fromisoformat(event['timestamp'])
            
            print(f"\n🔍 Event Details (ID: {event['id']})")
            print("-" * 50)
            print(f"📁 Filename: {event['filename']}")
            print(f"📅 Date & Time: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"🏷️ Event Type: {event['event']['type']}")
            print(f"📊 Confidence: {event['event']['confidence']:.2f}")
            print(f"⏱️ Duration: {event['duration']:.1f} seconds")
            print(f"🎞️ Frames: {event['frames_count']}")
            print(f"💾 File Size: {event['file_size']:.2f} MB")
            print(f"📍 GPS: {event['gps']['latitude']:.6f}, {event['gps']['longitude']:.6f}")
            print(f"🎯 Detection ID: {event['event']['detection_id']}")
            print(f"🤖 Model: {event['event']['model_version']}")
            print(f"📐 Resolution: {event['recording_info']['resolution']}")
            
            # Check if file exists
            if os.path.exists(event['filepath']):
                print(f"Video file exists at: {event['filepath']}")
            else:
                print(f" Video file missing at: {event['filepath']}")
                
        except ValueError:
            print("Please enter a valid event ID (number).")
        except Exception as e:
            print(f"Error: {e}")
    
    def filter_events_by_type(self):
        """Filter and show events by type"""
        print(f"\nAvailable event types: {', '.join(config.EVENT_TYPES)}")
        event_type = input("Enter event type to filter: ").strip()
        
        if event_type not in config.EVENT_TYPES:
            print(f" Invalid event type. Available types: {', '.join(config.EVENT_TYPES)}")
            return
        
        events = self.metadata_manager.get_events_by_type(event_type)
        
        if not events:
            print(f"📭 No events found for type: {event_type}")
            return
        
        print(f"\n🔍 Events of type '{event_type}' ({len(events)} found):")
        print("-" * 70)
        print(f"{'ID':<4} {'Confidence':<10} {'Duration':<10} {'Date & Time':<20}")
        print("-" * 70)
        
        for event in events:
            timestamp = datetime.fromisoformat(event['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d %H:%M')
            print(f"{event['id']:<4} {event['event']['confidence']:<10.2f} "
                  f"{event['duration']:<10.1f}s {date_str:<20}")
    
    def show_recent_events(self):
        """Show recent events"""
        try:
            hours = int(input("\nEnter number of hours to look back (default 24): ") or "24")
            events = self.metadata_manager.get_recent_events(hours)
            
            if not events:
                print(f"📭 No events found in the last {hours} hours.")
                return
            
            print(f"\n⏰ Recent Events (last {hours} hours, {len(events)} found):")
            print("-" * 80)
            print(f"{'ID':<4} {'Type':<20} {'Confidence':<10} {'Duration':<10} {'Time Ago':<15}")
            print("-" * 80)
            
            now = datetime.now()
            for event in events:
                timestamp = datetime.fromisoformat(event['timestamp'])
                time_diff = now - timestamp
                
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days}d ago"
                elif time_diff.seconds > 3600:
                    time_ago = f"{time_diff.seconds//3600}h ago"
                else:
                    time_ago = f"{time_diff.seconds//60}m ago"
                
                print(f"{event['id']:<4} {event['event']['type']:<20} {event['event']['confidence']:<10.2f} "
                      f"{event['duration']:<10.1f}s {time_ago:<15}")
                
        except ValueError:
            print("Please enter a valid number of hours.")
    
    def search_events(self):
        """Search events by keyword"""
        query = input("\nEnter search term (event type, filename, or detection ID): ").strip()
        
        if not query:
            print("Please enter a search term.")
            return
        
        events = self.metadata_manager.search_events(query)
        
        if not events:
            print(f"No events found matching: '{query}'")
            return
        
        print(f"\nSearch Results for '{query}' ({len(events)} found):")
        print("-" * 80)
        print(f"{'ID':<4} {'Type':<20} {'Confidence':<10} {'Duration':<10} {'Date & Time':<20}")
        print("-" * 80)
        
        for event in events:
            timestamp = datetime.fromisoformat(event['timestamp'])
            date_str = timestamp.strftime('%Y-%m-%d %H:%M')
            print(f"{event['id']:<4} {event['event']['type']:<20} {event['event']['confidence']:<10.2f} "
                  f"{event['duration']:<10.1f}s {date_str:<20}")
    
    def show_statistics(self):
        """Show system statistics"""
        stats = self.metadata_manager.get_statistics()
        
        print("\n System Statistics:")
        print("-" * 40)
        print(f"Total Events: {stats['total_events']}")
        print(f"Total Storage: {stats['total_storage_mb']} MB")
        print(f"Average Confidence: {stats['average_confidence']:.2f}")
        print(f"Average Duration: {stats['average_duration']} seconds")
        
        if stats['event_types']:
            print(f"\n Event Type Distribution:")
            for event_type, count in stats['event_types'].items():
                percentage = (count / stats['total_events']) * 100
                print(f"  {event_type}: {count} events ({percentage:.1f}%)")
        
        if stats['date_range']['earliest']:
            earliest = datetime.fromisoformat(stats['date_range']['earliest'])
            latest = datetime.fromisoformat(stats['date_range']['latest'])
            print(f"\n Date Range:")
            print(f"  Earliest: {earliest.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Latest: {latest.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def export_metadata(self):
        """Export metadata to file"""
        filepath = self.metadata_manager.export_metadata()
        if filepath:
            print(f"Metadata exported successfully to: {filepath}")
        else:
            print(" Failed to export metadata.")
    
    def cleanup_old_events(self):
        """Clean up old events"""
        try:
            days = int(input(f"\nEnter number of days to keep (default {config.MAX_RECORDING_AGE_DAYS}): ") 
                           or str(config.MAX_RECORDING_AGE_DAYS))
            
            print(f" This will delete all events older than {days} days.")
            confirm = input("Are you sure? (yes/no): ").lower().strip()
            
            if confirm in ['yes', 'y']:
                result = self.metadata_manager.cleanup_old_events(days)
                print(f" Cleanup completed:")
                print(f"  Deleted events: {result['deleted_events']}")
                print(f"  Freed space: {result['freed_space_mb']} MB")
                print(f"  Remaining events: {result['remaining_events']}")
            else:
                print(" Cleanup cancelled.")
                
        except ValueError:
            print(" Please enter a valid number of days.")
    
    def show_system_status(self):
        """Show current system status"""
        print("\n System Status:")
        print("-" * 40)
        print(f"Buffer Duration: {config.BUFFER_SECONDS}s")
        print(f"Post-Event Duration: {config.POST_EVENT_SECONDS}s")
        print(f"Total Clip Duration: {config.TOTAL_CLIP_SECONDS}s")
        print(f"Frame Rate: {config.FPS} FPS")
        print(f"Resolution: {config.FRAME_WIDTH}x{config.FRAME_HEIGHT}")
        print(f"Video Format: {config.VIDEO_FORMAT}")
        print(f"Event Types: {', '.join(config.EVENT_TYPES)}")
        print(f"Event Probability: {config.EVENT_PROBABILITY * 100:.1f}% per second")
        print(f"Min Confidence: {config.MIN_CONFIDENCE}")
        
        # Check directory status
        recordings_count = len([f for f in os.listdir(config.RECORDINGS_DIR) 
                              if f.endswith(f'.{config.VIDEO_FORMAT}')])
        
        print(f"\n Storage Status:")
        print(f"Recordings Directory: {config.RECORDINGS_DIR}")
        print(f"Video Files: {recordings_count}")
        
        # Calculate total size
        total_size = 0
        for filename in os.listdir(config.RECORDINGS_DIR):
            if filename.endswith(f'.{config.VIDEO_FORMAT}'):
                filepath = os.path.join(config.RECORDINGS_DIR, filename)
                total_size += os.path.getsize(filepath)
        
        total_size_mb = total_size / (1024 * 1024)
        print(f"Total Storage Used: {total_size_mb:.2f} MB")
    
    def run(self):
        """Main CLI loop"""
        self.print_banner()
        
        while True:
            self.print_menu()
            try:
                choice = input("\nEnter your choice (0-9): ").strip()
                
                if choice == '0':
                    print(" Goodbye!")
                    break
                elif choice == '1':
                    self.list_all_events()
                elif choice == '2':
                    self.show_event_details()
                elif choice == '3':
                    self.filter_events_by_type()
                elif choice == '4':
                    self.show_recent_events()
                elif choice == '5':
                    self.search_events()
                elif choice == '6':
                    self.show_statistics()
                elif choice == '7':
                    self.export_metadata()
                elif choice == '8':
                    self.cleanup_old_events()
                elif choice == '9':
                    self.show_system_status()
                else:
                    print(" Invalid choice. Please enter a number between 0-9.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                input("\nPress Enter to continue...")

if __name__ == "__main__":
    cli = CLIInterface()
    cli.run()