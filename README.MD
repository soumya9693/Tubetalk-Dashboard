TubeTalk: Your AI YouTube Assistant 
TubeTalk is an intelligent web application that transforms YouTube videos into concise, well-structured summaries using Google Gemini AI. Save time and get the key insights from any YouTube video in seconds!

                         Features
 Video Summarization: Convert lengthy YouTube videos into concise summaries

 AI-Powered: Utilizes Google Gemini AI for intelligent content analysis

 Transcript Extraction: Automatically extracts subtitles and captions

 Analytics: Provides transcript statistics and metrics

 Download: Save summaries for offline reading

 User-Friendly: Clean, intuitive interface with progress tracking

                      Technologies Used
Frontend: Streamlit

AI Model: Google Gemini AI

Video Processing: yt-dlp

Transcript Handling: Custom subtitle parser (supports JSON, VTT, SRT formats)

Environment Management: python-dotenv

                     Prerequisites
Before running TubeTalk, ensure you have:

Python 3.8 or higher installed

Google Gemini API Key (Get it here)

Stable internet connection

                  Installation & Setup
Step 1: Clone or Download the Project
Download all the project files to your local machine.

Step 2: Install Required Dependencies
Open your terminal/command prompt and run:

                        bash
pip install streamlit python-dotenv langchain-google-genai langchain-core yt-dlp requests

Step 3: Set Up Environment Variables
Create a file named .env in the project root directory

             Add your Google Gemini API key to the file:

env
GOOGLE_API_KEY="your_actual_api_key_here"
Replace your_actual_api_key_here with your actual Google Gemini API key.

Step 4: Run the Application
Execute the following command in your terminal:

                        bash
streamlit run app.py
(Replace app.py with the actual name of your Python file)

Step 5: Access the Application
Once running, the application will automatically open in your default web browser at:

                       text
http://localhost:8501
If it doesn't open automatically, you can manually navigate to this address.

 How to Use
Enter YouTube URL:

Go to the "Video Summary" tab

Paste any YouTube video URL in the input field

Example formats:

https://www.youtube.com/watch?v=VIDEO_ID

https://youtu.be/VIDEO_ID

Generate Summary:

Click the "Generate Summary" button

The app will:

Fetch video information and thumbnail

Extract available transcripts

Generate AI-powered summary

View Results:

Read the comprehensive summary

Preview the transcript if needed

Download the summary as a text file

Check analytics in the "Analytics" tab

               Configuration
Available Gemini Models
The application automatically tries these models in order:

gemini-2.5-flash (Primary)

gemini-2.0-flash (Fallback)

gemini-2.5-pro (Pro version)

gemini-flash-latest (Latest flash)

gemini-pro-latest (Latest pro)

              Customization
You can modify the AI behavior by adjusting:

temperature parameter in the setup_llm() function

Prompt template in the prompt_template variable

            Supported Video Types
Videos with manual subtitles (preferred)

Videos with automatic captions

Videos in multiple languages (English prioritized)

Various subtitle formats (JSON, VTT, SRT)

             Important Notes
Subtitles Required: The video must have subtitles or automatic captions enabled

API Limits: Be mindful of Google Gemini API usage limits

Video Availability: Some videos may restrict transcript access

Internet Connection: Required for all operations

              Troubleshooting
Common Issues:
"API Key Not Found"

Ensure .env file exists in the correct directory

Verify the API key format: GOOGLE_API_KEY="your_key_here"

Restart the application after adding the API key

"No subtitles available"

Try a different YouTube video with enabled subtitles

Check if the video has English subtitles or captions

Module Import Errors

Run: pip install -r requirements.txt (if available)

Or manually install missing packages

Application Won't Start

Ensure Python 3.8+ is installed

Check if Streamlit is properly installed

Verify no syntax errors in the code

                     Project Structure
text
tubetalk/
├── app.py                 # Main application file
├── .env                   # Environment variables (create this)
├── requirements.txt       # Python dependencies
└── README.md             # This file
🔒 Privacy & Security
Your Google API key is stored locally in the .env file

Video URLs and transcripts are processed temporarily

No data is stored permanently on external servers

API calls are made directly to Google's servers

                        Support
If you encounter any issues:

Check the troubleshooting section above

Ensure all dependencies are properly installed

Verify your Google Gemini API key is valid and active

Check that the YouTube video has available subtitles

                   Enjoy Using TubeTalk!
Transform your YouTube learning experience with AI-powered summaries. Perfect for students, researchers, content creators, and anyone looking to save time while consuming video content!

Note: This application is for educational and personal use. Please respect YouTube's Terms of Service and content creators' rights.

