import youtube_transcript_api

# Check what's available in the module
print(dir(youtube_transcript_api))
print("\nVersion:", youtube_transcript_api.__version__ if hasattr(youtube_transcript_api, '__version__') else "Unknown")

# Try to import the class
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("\nYouTubeTranscriptApi imported successfully")
    print("Available methods:", [m for m in dir(YouTubeTranscriptApi) if not m.startswith('_')])
except Exception as e:
    print(f"\nError importing: {e}")