import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import yt_dlp
import requests
import tempfile
import json
import time

# Load environment variables from .env file
load_dotenv()

# --- Set up the LLM and the Prompt ---
def setup_llm():
    """Setup Gemini LLM with correct model names"""
    # Try available models in order of preference
    models_to_try = [
        "gemini-2.5-flash",          # Fast and free - should work
        "gemini-2.0-flash",          # Good alternative
        "gemini-2.5-pro",            # Pro version
        "gemini-flash-latest",       # Latest flash
        "gemini-pro-latest",         # Latest pro
    ]
    
    for model_name in models_to_try:
        try:
            # REMOVED: st.write(f"🔄 Trying model: {model_name}") - This line is removed as requested
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=0.3,
                google_api_key=os.getenv("GOOGLE_API_KEY")
            )
            # Test the model with a simple prompt
            test_response = llm.invoke("Say 'Hello' in one word.")
            # REMOVED: Success message from UI - backend only
            return llm
        except Exception as e:
            # REMOVED: Warning messages from UI - backend only
            continue
    
    # REMOVED: Error message from UI - will handle in main app
    return None

# Initialize LLM
llm = setup_llm()

prompt_template = """
You are an expert in summarizing YouTube videos.
You will be given a transcript of a YouTube video and your job is to provide a concise summary.

Please provide a well-structured summary that includes:
1. Main topic and key points
2. Important insights or findings
3. Conclusion or main takeaways

Here is the transcript:
{transcript}

Summary:
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["transcript"])
output_parser = StrOutputParser()

if llm:
    summarizer_chain = prompt | llm | output_parser
else:
    summarizer_chain = None

# --- Helper function to get video info using yt-dlp ---
def get_video_info(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        video_title = info_dict.get('title', 'No title found')
        video_thumbnail_url = info_dict.get('thumbnail', None)
        video_duration = info_dict.get('duration', 0)
        return video_title, video_thumbnail_url, video_duration

# --- Improved transcript function using yt-dlp ---
def get_youtube_transcript(url):
    try:
        video_id = ""
        if "watch?v=" in url:
            video_id = url.split("v=")[1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("/")[-1].split("?")[0]
        else:
            raise ValueError("Invalid YouTube URL format")
        
        ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'skip_download': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            
            # Check for available subtitles
            subtitles = info_dict.get('subtitles', {})
            automatic_captions = info_dict.get('automatic_captions', {})
            
            # Display available languages
            available_subs = list(subtitles.keys())[:5] if subtitles else []
            available_auto = list(automatic_captions.keys())[:5] if automatic_captions else []
            
            if available_subs:
                st.sidebar.write("📝 Manual subtitles:", available_subs)
            if available_auto:
                st.sidebar.write("🤖 Auto-captions:", available_auto)
            
            # Try to get English subtitles first
            transcript_text = None
            
            # Priority 1: Manual English subtitles
            if 'en' in subtitles and subtitles['en']:
                subtitle_url = subtitles['en'][0]['url']
                transcript_text = download_and_parse_subtitle(subtitle_url)
                if transcript_text:
                    st.success("✓ Using English manual subtitles")
            
            # Priority 2: Automatic English captions
            if not transcript_text and 'en' in automatic_captions and automatic_captions['en']:
                subtitle_url = automatic_captions['en'][0]['url']
                transcript_text = download_and_parse_subtitle(subtitle_url)
                if transcript_text:
                    st.success("✓ Using English automatic captions")
            
            # Priority 3: Any available manual subtitle
            if not transcript_text and subtitles:
                for lang in list(subtitles.keys())[:3]:  # Try first 3 languages
                    if subtitles[lang]:
                        subtitle_url = subtitles[lang][0]['url']
                        transcript_text = download_and_parse_subtitle(subtitle_url)
                        if transcript_text:
                            st.success(f"✓ Using {lang} manual subtitles")
                            break
            
            # Priority 4: Any available auto-caption
            if not transcript_text and automatic_captions:
                for lang in list(automatic_captions.keys())[:3]:  # Try first 3 languages
                    if automatic_captions[lang]:
                        subtitle_url = automatic_captions[lang][0]['url']
                        transcript_text = download_and_parse_subtitle(subtitle_url)
                        if transcript_text:
                            st.success(f"✓ Using {lang} automatic captions")
                            break
            
            if transcript_text:
                return transcript_text
            else:
                return "Error: No subtitles or captions available for this video."
                
    except Exception as e:
        return f"Error fetching transcript: {str(e)}"

def download_and_parse_subtitle(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content = response.text
            
            # Handle different subtitle formats
            if url.endswith('.json3') or url.endswith('.json'):
                return parse_json_subtitle(response.json())
            elif url.endswith('.vtt'):
                return parse_vtt_subtitle(content)
            elif url.endswith('.srt'):
                return parse_srt_subtitle(content)
            else:
                # Try to auto-detect format
                if content.strip().startswith('WEBVTT'):
                    return parse_vtt_subtitle(content)
                elif '-->' in content and any(char.isdigit() for char in content):
                    return parse_srt_subtitle(content)
                else:
                    # Try JSON parsing as fallback
                    try:
                        return parse_json_subtitle(response.json())
                    except:
                        return content  # Return raw content as last resort
        return None
    except Exception as e:
        st.warning(f"Subtitle parsing error: {e}")
        return None

def parse_json_subtitle(data):
    """Parse JSON3 subtitle format"""
    try:
        events = data.get('events', [])
        transcript_parts = []
        
        for event in events:
            if 'segs' in event:
                for seg in event['segs']:
                    if 'utf8' in seg:
                        text = seg['utf8'].strip()
                        if text and text not in ['\n', ' ']:
                            transcript_parts.append(text)
        
        return " ".join(transcript_parts)
    except Exception as e:
        st.warning(f"JSON subtitle parsing failed: {e}")
        return None

def parse_vtt_subtitle(content):
    """Parse WebVTT subtitle format"""
    try:
        lines = content.split('\n')
        transcript_parts = []
        in_cue = False
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                in_cue = True
                continue
            if not line or line.isdigit() or line == 'WEBVTT':
                in_cue = False
                continue
            if in_cue and line and not line.startswith('NOTE'):
                transcript_parts.append(line)
        
        return " ".join(transcript_parts)
    except Exception as e:
        st.warning(f"VTT subtitle parsing failed: {e}")
        return None

def parse_srt_subtitle(content):
    """Parse SRT subtitle format"""
    try:
        lines = content.split('\n')
        transcript_parts = []
        in_cue = False
        
        for line in lines:
            line = line.strip()
            if '-->' in line:
                in_cue = True
                continue
            if not line or line.isdigit():
                in_cue = False
                continue
            if in_cue and line:
                transcript_parts.append(line)
        
        return " ".join(transcript_parts)
    except Exception as e:
        st.warning(f"SRT subtitle parsing failed: {e}")
        return None

# --- Enhanced Streamlit User Interface ---
st.set_page_config(
    page_title="TubeTalk: Your YouTube Assistant", 
    layout="wide",
    page_icon="📺"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem !important;
        color: #262730;
        margin-bottom: 1rem;
    }
    .video-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #FF4B4B;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    .summary-card {
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #00D4AA;
        background-color: #f0f8ff;
        margin-bottom: 1rem;
    }
    .stProgress > div > div > div > div {
        background-color: #FF4B4B;
    }
    .url-input {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
    }
    /* Custom button color */
    .stButton>button {
        background-color: #00D4AA !important;
        color: white !important;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #00B894 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<h1 class="main-header">🎬 TubeTalk: Your AI YouTube Assistant</h1>', unsafe_allow_html=True)
st.markdown("### 🚀 Transform YouTube videos into concise summaries in seconds!")

# Create tabs for better organization
tab1, tab2, tab3 = st.tabs(["📹 Video Summary", "📊 Analytics", "ℹ️ About"])

with tab1:
    # Enhanced URL Input Section
    st.markdown("---")
    st.markdown('<div class="url-input">', unsafe_allow_html=True)
    st.markdown("### 📥 Enter YouTube Video URL")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        youtube_url = st.text_input(
            "Paste YouTube URL here:",
            placeholder="https://www.youtube.com/watch?v=... or https://youtu.be/...",
            label_visibility="collapsed"
        )
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        # REMOVED: Generate button from URL section
    
    st.markdown('</div>', unsafe_allow_html=True)

    if youtube_url:
        try:
            # Video Information Card
            with st.spinner("🔍 Fetching video information..."):
                video_title, video_thumbnail_url, video_duration = get_video_info(youtube_url)
            
            st.markdown("---")
            st.markdown("### 📺 Video Preview")
            
            # Enhanced Video Display
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if video_thumbnail_url:
                    # FIXED: Replaced use_column_width with use_container_width
                    st.image(video_thumbnail_url, use_container_width=True, caption="Video Thumbnail")
                
                # Video metadata
                st.markdown("**Video Details:**")
                if video_duration:
                    minutes = video_duration // 60
                    seconds = video_duration % 60
                    st.write(f"⏱️ **Duration:** {minutes}m {seconds}s")
                st.write(f"📝 **Title:** {video_title}")
            
            with col2:
                st.markdown("### Ready to Summarize!")
                st.write("Click the **'Generate Summary'** button below to get started!")
                st.info("💡 **Tip:** Make sure the video has subtitles or captions enabled for best results.")
                
                # MOVED: Generate button inside the video preview section
                summarize_clicked = st.button("🚀 **Generate Summary**", type="primary", use_container_width=True)

            # Generate Summary with Enhanced Effects
            if summarize_clicked:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Fetching transcript
                status_text.text("🔄 Step 1/3: Fetching video transcript...")
                with st.spinner("📥 Downloading transcript..."):
                    transcript = get_youtube_transcript(youtube_url)
                    progress_bar.progress(33)
                    time.sleep(0.5)  # Smooth progress effect
                
                if "Error" not in transcript:
                    status_text.text("✅ Step 2/3: Transcript fetched successfully!")
                    
                    # Transcript Preview with enhanced display
                    with st.expander("📜 **View Transcript Preview**", expanded=False):
                        st.text_area("Full Transcript", transcript, height=200, label_visibility="collapsed", key="transcript_preview")
                    
                    # Step 2: Generating summary
                    status_text.text("🤖 Step 3/3: Generating AI summary...")
                    progress_bar.progress(66)
                    
                    if summarizer_chain:
                        try:
                            # Animated summary generation
                            with st.spinner("🧠 AI is analyzing and summarizing the content..."):
                                summary = summarizer_chain.invoke({"transcript": transcript})
                                progress_bar.progress(100)
                                time.sleep(0.5)
                            
                            status_text.text("✅ Summary generated successfully!")
                            
                            # Display Summary in Enhanced Card
                            st.markdown("---")
                            st.markdown("### 📝 **AI Generated Summary**")
                            st.markdown('<div class="summary-card">', unsafe_allow_html=True)
                            st.write(summary)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Enhanced Download Section
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                st.download_button(
                                    "💾 **Download Summary**",
                                    summary,
                                    file_name=f"summary_{video_title[:30]}.txt",
                                    mime="text/plain",
                                    use_container_width=True
                                )
                            
                            # Clear button
                            if st.button("🔄 Analyze Another Video", use_container_width=True):
                                st.rerun()
                                
                        except Exception as e:
                            st.error(f"❌ Summary generation failed: {e}")
                    else:
                        st.error("🤖 AI service is currently unavailable. Please check your API configuration.")
                else:
                    st.error(f"❌ {transcript}")
                    progress_bar.empty()
                    status_text.empty()

        except Exception as e:
            st.error(f"⚠️ An error occurred. Please check the URL and try again. Details: {e}")

with tab2:
    st.markdown("### 📊 Analytics & Metrics")
    if youtube_url and 'transcript' in locals() and "Error" not in transcript:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Transcript Length", f"{len(transcript):,} chars")
        with col2:
            st.metric("Word Count", f"{len(transcript.split()):,} words")
        with col3:
            st.metric("Estimated Reading Time", f"{len(transcript.split())//200 + 1} min")
    else:
        st.info("👆 Enter a YouTube URL and generate a summary to see analytics here!")

with tab3:
    st.markdown("### ℹ️ About TubeTalk")
    st.write("""
    **TubeTalk** transforms your YouTube watching experience by providing intelligent video summaries using cutting-edge AI technology.
    
    ### 🛠️ How it works:
    1. **Input**: Paste any YouTube video URL
    2. **Processing**: Our system extracts and analyzes the video transcript
    3. **AI Analysis**: Google Gemini AI generates a comprehensive summary
    4. **Output**: Get a well-structured summary with key insights
    
    ### 🔧 Technologies Used:
    - **YouTube Transcript API** for caption extraction
    - **Google Gemini AI** for intelligent summarization
    - **Streamlit** for seamless user experience
    
    ### 💡 Perfect for:
    - Students and researchers
    - Content creators
    - Busy professionals
    - Lifelong learners
    """)

# Sidebar enhancements
with st.sidebar:
    st.markdown("### ⚡ Quick Actions")
    if youtube_url:
        st.success("✅ Video URL loaded")
        if summarize_clicked:
            st.balloons()  # Celebration effect
    
    st.markdown("### 🔍 Status")
    if llm:
        st.success("🤖 AI: Connected")
    else:
        st.error("🤖 AI: Disconnected")
    
    st.markdown("---")
    st.markdown("### 📈 Tips")
    st.info("""
    - Use videos with English subtitles
    - Longer videos may take more time
    - Results are best with clear audio
    - Save summaries for future reference
    """)