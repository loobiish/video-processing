import subprocess
import os

def add_subtitles(video_path, subtitles_path, output_path):
    """Adds subtitles using raw FFmpeg command with Windows path workaround."""
    # Convert to absolute paths and normalize
    video_path = os.path.abspath(video_path)
    subtitles_path = os.path.abspath(subtitles_path)
    output_path = os.path.abspath(output_path)
    
    print("==================================================")
    print(video_path, subtitles_path, output_path)
    print("==================================================")
    # Windows-specific path formatting
    subtitles_filter_path = subtitles_path.replace('\\', '\\\\').replace(':', '\\:')
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"subtitles={subtitles_filter_path}",  # No quotes!
        "-c:a", "copy",
        output_path
    ]
    
    # Debug: Print the exact command being executed
    print("Executing:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Success! Output saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed with error:\n{e.stderr}")

if __name__ == "__main__":
    add_subtitles(
        "video-processing/output_videos/clip_1.mp4",
        "video-processing/output_videos/clip_1.srt",
        "video-processing/final_videos/final_file.mp4"
    )