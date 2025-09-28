# metadata_manager.py - Metadata storage and management system

import json
import os
from datetime import datetime, timedelta
import config

class MetadataManager:
    def __init__(self):
        self.metadata_file = os.path.join(config.METADATA_DIR, "events_metadata.json")
        self.ensure_metadata_file_exists()
    
    def ensure_metadata_file_exists(self):
        """Create metadata file if it doesn't exist"""
        if not os.path.exists(self.metadata_file):
            self.save_metadata([])
            print(f"Created new metadata file: {self.metadata_file}")
    
    def save_event_metadata(self, clip_info):
        """Save metadata for a recorded event clip"""
        try:
            # Load existing metadata
            existing_metadata = self.load_metadata()
            
            # Create metadata entry
            metadata_entry = {
                'id': len(existing_metadata) + 1,
                'filename': clip_info['filename'],
                'filepath': clip_info['filepath'],
                'timestamp': clip_info['timestamp'].isoformat(),
                'duration': clip_info['duration'],
                'frames_count': clip_info['frames_count'],
                'file_size': self.get_file_size(clip_info['filepath']),
                'event': {
                    'type': clip_info['event_data']['type'],
                    'confidence': clip_info['event_data']['confidence'],
                    'detection_id': clip_info['event_data']['detection_id'],
                    'model_version': clip_info['event_data']['model_version'],
                    'bbox': clip_info['event_data']['bbox']
                },
                'gps': clip_info['event_data']['gps'],
                'recording_info': {
                    'fps': config.FPS,
                    'resolution': f"{config.FRAME_WIDTH}x{config.FRAME_HEIGHT}",
                    'codec': config.VIDEO_CODEC,
                    'buffer_seconds': config.BUFFER_SECONDS,
                    'post_event_seconds': config.POST_EVENT_SECONDS
                },
                'created_at': datetime.now().isoformat()
            }
            
            # Add to existing metadata
            existing_metadata.append(metadata_entry)
            
            # Save updated metadata
            self.save_metadata(existing_metadata)
            
            if config.VERBOSE:
                print(f"📝 Metadata saved for event ID: {metadata_entry['id']}")
            
            return metadata_entry
            
        except Exception as e:
            print(f"Error saving metadata: {e}")
            return None
    
    def load_metadata(self):
        """Load all metadata from file"""
        try:
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_metadata(self, metadata):
        """Save metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving metadata file: {e}")
    
    def get_file_size(self, filepath):
        """Get file size in MB"""
        try:
            size_bytes = os.path.getsize(filepath)
            size_mb = round(size_bytes / (1024 * 1024), 2)
            return size_mb
        except OSError:
            return 0
    
    def get_all_events(self):
        """Get all recorded events"""
        return self.load_metadata()
    
    def get_event_by_id(self, event_id):
        """Get specific event by ID"""
        metadata = self.load_metadata()
        for event in metadata:
            if event['id'] == event_id:
                return event
        return None
    
    def get_events_by_type(self, event_type):
        """Get all events of a specific type"""
        metadata = self.load_metadata()
        return [event for event in metadata if event['event']['type'] == event_type]
    
    def get_events_by_date(self, date_str):
        """Get events from a specific date (YYYY-MM-DD format)"""
        metadata = self.load_metadata()
        events = []
        
        for event in metadata:
            event_date = datetime.fromisoformat(event['timestamp']).date()
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if event_date == target_date:
                events.append(event)
        
        return events
    
    def get_recent_events(self, hours=24):
        """Get events from the last N hours"""
        metadata = self.load_metadata()
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_events = []
        for event in metadata:
            event_time = datetime.fromisoformat(event['timestamp'])
            if event_time >= cutoff_time:
                recent_events.append(event)
        
        return sorted(recent_events, key=lambda x: x['timestamp'], reverse=True)
    
    def get_statistics(self):
        """Get statistics about recorded events"""
        metadata = self.load_metadata()
        
        if not metadata:
            return {
                'total_events': 0,
                'total_storage_mb': 0,
                'event_types': {},
                'average_confidence': 0,
                'date_range': None
            }
        
        # Calculate statistics
        total_events = len(metadata)
        total_storage = sum(event.get('file_size', 0) for event in metadata)
        
        # Event type distribution
        event_types = {}
        confidences = []
        
        for event in metadata:
            event_type = event['event']['type']
            event_types[event_type] = event_types.get(event_type, 0) + 1
            confidences.append(event['event']['confidence'])
        
        # Date range
        timestamps = [datetime.fromisoformat(event['timestamp']) for event in metadata]
        date_range = {
            'earliest': min(timestamps).isoformat() if timestamps else None,
            'latest': max(timestamps).isoformat() if timestamps else None
        }
        
        return {
            'total_events': total_events,
            'total_storage_mb': round(total_storage, 2),
            'event_types': event_types,
            'average_confidence': round(sum(confidences) / len(confidences), 2) if confidences else 0,
            'date_range': date_range,
            'average_duration': round(sum(event['duration'] for event in metadata) / total_events, 1) if metadata else 0
        }
    
    def cleanup_old_events(self, days=7):
        """Remove events and files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        metadata = self.load_metadata()
        
        events_to_keep = []
        deleted_count = 0
        freed_space = 0
        
        for event in metadata:
            event_date = datetime.fromisoformat(event['timestamp'])
            
            if event_date >= cutoff_date:
                events_to_keep.append(event)
            else:
                # Delete the video file
                if os.path.exists(event['filepath']):
                    try:
                        file_size = event.get('file_size', 0)
                        os.remove(event['filepath'])
                        deleted_count += 1
                        freed_space += file_size
                        print(f"Deleted old event: {event['filename']}")
                    except OSError as e:
                        print(f"Error deleting file {event['filepath']}: {e}")
        
        # Save updated metadata
        self.save_metadata(events_to_keep)
        
        return {
            'deleted_events': deleted_count,
            'freed_space_mb': round(freed_space, 2),
            'remaining_events': len(events_to_keep)
        }
    
    def export_metadata(self, filepath=None):
        """Export metadata to a file"""
        if filepath is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = os.path.join(config.METADATA_DIR, f"metadata_export_{timestamp}.json")
        
        try:
            metadata = self.load_metadata()
            with open(filepath, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            print(f"Metadata exported to: {filepath}")
            return filepath
        except Exception as e:
            print(f"Error exporting metadata: {e}")
            return None
    
    def search_events(self, query):
        """Search events by event type, detection ID, or filename"""
        metadata = self.load_metadata()
        query = query.lower()
        
        matching_events = []
        for event in metadata:
            # Search in event type, filename, and detection ID
            searchable_fields = [
                event['event']['type'].lower(),
                event['filename'].lower(),
                event['event']['detection_id'].lower()
            ]
            
            if any(query in field for field in searchable_fields):
                matching_events.append(event)
        
        return matching_events