import os
import zipfile
import io
import streamlit as st
from PIL import Image

# Pillow compatibility fix for MoviePy
if not hasattr(Image, 'ANTIALIAS'):
    Image.ANTIALIAS = Image.Resampling.LANCZOS

from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Motivatedchristian Shorts Clipper", page_icon="✝️", layout="centered")

if os.path.exists("banner.png"):
    st.image("banner.png", use_container_width=True)

st.title("✝️ Motivatedchristian: HD Shorts & Smart Metadata Generator")
st.markdown("Upload your video or paste a YouTube link to generate high-resolution vertical shorts with smart, unique titles and captions tailored per clip!")

if "clip_files" not in st.session_state:
    st.session_state.clip_files = []
if "video_title" not in st.session_state:
    st.session_state.video_title = "Telugu Christian Devotional"
if "generated" not in st.session_state:
    st.session_state.generated = False

uploaded_file = st.file_uploader("Upload Long Video File (.mp4):", type=["mp4", "mov"])
yt_url = st.text_input("Or Paste YouTube Video Link (optional):")

num_clips = st.slider("How many Shorts to generate?", min_value=3, max_value=10, value=5)
clip_duration = 30

output_dir = "generated_shorts"
os.makedirs(output_dir, exist_ok=True)

col1, col2 = st.columns([3, 1])
with col1:
    generate_btn = st.button("🚀 Generate HD Shorts & Captions")
with col2:
    reset_btn = st.button("🔄 Reset App")

if reset_btn:
    st.session_state.clip_files = []
    st.session_state.video_title = "Telugu Christian Devotional"
    st.session_state.generated = False
    st.rerun()

if generate_btn:
    video_path = "source_video.mp4"
    success = False
    extracted_title = "Telugu Christian Devotional"
    
    if uploaded_file is not None:
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        extracted_title = os.path.splitext(uploaded_file.name)[0].replace("_", " ")
        success = True
    elif yt_url:
        with st.spinner("Analyzing YouTube video metadata & downloading..."):
            ydl_info_opts = {'noplaylist': True}
            try:
                with YoutubeDL(ydl_info_opts) as ydl:
                    info_dict = ydl.extract_info(yt_url, download=False)
                    extracted_title = info_dict.get('title', 'Telugu Christian Devotional')
            except:
                pass

            ydl_opts = {
                'format': 'b',
                'outtmpl': video_path,
                'overwrites': True,
                'noplaylist': True
            }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
                if os.path.exists(video_path):
                    success = True
            except Exception as e:
                st.error(f"Download failed: {e}. Please use the file uploader above for instant results.")
    else:
        st.warning("Please upload an MP4 file or paste a YouTube link.")

    if success and os.path.exists(video_path):
        with st.spinner("Slicing and rendering clean HD vertical (9:16) shorts..."):
            try:
                clip_files = []
                video = VideoFileClip(video_path)
                total_duration = int(video.duration)
                
                interval = max(30, total_duration // (num_clips + 1))
                
                for i in range(num_clips):
                    start_t = i * interval
                    end_t = min(start_t + clip_duration, total_duration)
                    
                    if start_t >= total_duration:
                        break
                        
                    subclip = video.subclip(start_t, end_t)
                    
                    w, h = subclip.size
                    target_w = int(h * 9 / 16)
                    if target_w < w:
                        x_center = w / 2
                        subclip = subclip.crop(x1=x_center - target_w/2, y1=0, x2=x_center + target_w/2, y2=h)
                    
                    out_name = os.path.join(output_dir, f"short_{i+1}_t{start_t}s.mp4")
                    subclip.write_videofile(
                        out_name, 
                        codec="libx264", 
                        audio_codec="aac", 
                        fps=30, 
                        preset="medium", 
                        bitrate="3000k",
                        logger=None
                    )
                    clip_files.append(out_name)
                
                st.session_state.clip_files = clip_files
                st.session_state.video_title = extracted_title
                st.session_state.generated = True
                
            except Exception as e:
                st.error(f"Error processing video clips: {e}")

if st.session_state.generated and st.session_state.clip_files:
    st.success(f"Successfully generated {len(st.session_state.clip_files)} HD Shorts with unique captions!")
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in st.session_state.clip_files:
            zip_file.write(file, os.path.basename(file))
    zip_buffer.seek(0)
    
    st.markdown("### 📥 Download Bulk Package:")
    st.download_button(
        label=f"📦 Download All {len(st.session_state.clip_files)} Shorts as ZIP",
        data=zip_buffer,
        file_name="motivated_christian_hd_shorts.zip",
        mime="application/zip"
    )
    
    st.markdown("---")
    st.markdown("### 📝 Smart Ready-to-Use Titles & Captions (Unique per Short):")
    
    base_title = st.session_state.video_title
    for i, file in enumerate(st.session_state.clip_files):
        # Calculate approximate start time for unique context
        interval = max(30, int(300 // (len(st.session_state.clip_files) + 1)))
        approx_sec = i * interval
        m, s = divmod(approx_sec, 60)
        
        with st.expander(f"📌 Short {i+1} (Segment {m}m {s}s) - Details & Tags"):
            smart_title = f"{base_title[:45]} - Part {i+1} 🙏✨ #Jesus #TeluguChristian #Shorts"
            smart_desc = f"Powerful moment from '{base_title}': Watch, be blessed, and type 'Amen' in the comments!\n\n#TeluguChristian #JesusSaves #ChristianShorts #TeluguWorship #BiblePromise #MotivatedChristian"
            
            st.text_input(f"Title {i+1}", value=smart_title, key=f"title_{i}")
            st.text_area(f"Description & Hashtags {i+1}", value=smart_desc, key=f"desc_{i}")
