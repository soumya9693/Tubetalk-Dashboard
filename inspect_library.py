import sys
print("--- Inspecting the youtube_transcript_api library ---")
print(f"Python version being used: {sys.version}\n")

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    print("Successfully imported the YouTubeTranscriptApi class.")

    print("\n--- Listing all available attributes and methods on the class ---")

    # Use the built-in dir() function to get a list of everything on the object
    attributes = dir(YouTubeTranscriptApi)

    # Print them one per line to make it easy to read
    for attr in attributes:
        print(attr)

    print("\n--- Inspection Complete ---")

    if 'get_transcript' in attributes:
        print("\n✅ RESULT: 'get_transcript' WAS FOUND. The library appears to be correct.")
    else:
        print("\n❌ CRITICAL RESULT: 'get_transcript' WAS NOT FOUND. The installed library is broken or has a different function name.")

except ImportError:
    print("\n❌ ERROR: Could not import the library. It may not be installed correctly.")
except Exception as e:
    print(f"\n❌ An unexpected error occurred during inspection: {e}")