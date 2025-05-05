import subprocess
import os

def add_subtitles(video_path, subtitles_path, output_path):
    """Adds subtitles using FFmpeg with proper path escaping."""
    # Convert to absolute paths and normalize
    video_path = os.path.abspath(video_path)
    subtitles_path = os.path.abspath(subtitles_path)
    output_path = os.path.abspath(output_path)

    # Escape backslashes in paths
    subtitles_path = subtitles_path.replace("\\", "\\\\")

    print("==================================================")
    print(f"Video path: {video_path}")
    print(f"Subtitles path: {subtitles_path}")
    print(f"Output path: {output_path}")
    print("==================================================")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    cmd = [
    "ffmpeg",
    "-i", video_path,
    "-vf", f"subtitles={subtitles_path.replace(':', '\\:').replace('\\', '\\\\')}",
    "-c:v", "libx264",
    "-c:a", "copy",
    "-preset", "fast",
    "-crf", "22",
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
    # --- ADJUST THESE PATHS TO MATCH YOUR ACTUAL FILE LOCATIONS ---
    VIDEO_FILE = "output_videos/clip_1.mp4"
    SUBTITLES_FILE = "output_videos/clip_1.srt"
    OUTPUT_FILE = "final_videos/final_file.mp4"
    # -------------------------------------------------------------

    # Construct absolute paths for clarity
    base_dir = os.path.dirname(os.path.abspath(__file__))
    VIDEO_FILE_ABS = os.path.join(base_dir, VIDEO_FILE)
    SUBTITLES_FILE_ABS = os.path.join(base_dir, SUBTITLES_FILE)
    OUTPUT_FILE_ABS = os.path.join(base_dir, OUTPUT_FILE)

    add_subtitles(VIDEO_FILE_ABS, SUBTITLES_FILE_ABS, OUTPUT_FILE_ABS)
    print("✅ Subtitle addition process (using FFmpeg) initiated.")
