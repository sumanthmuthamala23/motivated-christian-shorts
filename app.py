import os
import streamlit as st
from yt_dlp import YoutubeDL
from moviepy.editor import VideoFileClip

st.set_page_config(page_title="Motivatedchristian Shorts Clipper", page_icon="✝️", layout="centered")

st.title("✝️ Motivatedchristian: Shorts Generator")
st.markdown("Upload an MP4 file or paste a YouTube link to automatically slice it into vertical 9:16 Shorts!")

uploaded_file = st.file_uploader("Upload Long Video File (.mp4):", type=["mp4", "mov"])
yt_url = st.text_input("Or Paste YouTube Video Link (optional):")

num_clips = st.slider("How many Shorts to generate?", min_value=3, max_value=10, value=5)
clip_duration = 30

output_dir = "generated_shorts"
os.makedirs(output_dir, exist_ok=True)

if st.button("🚀 Generate YouTube Shorts"):
    video_path = "source_video.mp4"
    success = False
    
    # Priority to uploaded file to avoid all YouTube/FFmpeg errors instantly
    if uploaded_file is not None:
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success("Using your uploaded video file successfully!")
        success = True
    elif yt_url:
        with st.spinner("Downloading video..."):
            ydl_opts = {
                'format': 'b',  # Single muxed format, zero FFmpeg required
                'outtmpl': video_path,
                'overwrites': True,
                'noplaylist': True
            }
            try:
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([yt_url])
                if os.path.exists(video_path):
                    st.success("YouTube video downloaded successfully!")
                    success = True
            except Exception as e:
                st.error(f"Download failed: {e}. Please use the file uploader above for instant results!")
    else:
        st.warning("Please either upload an MP4 file or paste a YouTube link.")

    if success and os.path.exists(video_path):
        with st.spinner("Slicing video into vertical (9:16) shorts..."):
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
                    subclip.write_videofile(out_name, codec="libx264", audio_codec="aac", fps=30, logger=None)
                    clip_files.append(out_name)
                
                st.success(f"Successfully generated {len(clip_files)} YouTube Shorts!")
                
                st.markdown("### 📥 Download Your Shorts:")
                for file in clip_files:
                    with open(file, "rb") as f:
                        st.download_button(
                            label=f"Download {os.path.basename(file)}",
                            data=f,
                            file_name=os.path.basename(file),
                            mime="video/mp4"
                        )
            except Exception as e:
                st.error(f"Error processing video clips: {e}")
