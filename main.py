# Improting Libraries

import os
from moviepy import VideoFileClip
from moviepy.video.fx import Crop
import whisper
import subprocess


def extract_clip_moviepy(video_path, start_time, end_time, output_path):
    """Extracts video clips using MoviePy's precise subclip method."""
    
    try:
        clip = VideoFileClip(video_path)
        # Check if the duration of movie is 0
        if clip.duration == 0:
            raise ValueError("Video duration is 0. Check the file.")

        # Ensure times are within the valid range
        start_time = max(0, min(start_time, clip.duration))
        end_time = max(0, min(end_time, clip.duration))

        # Extract subclip
        subclip = clip.subclipped(start_time, end_time)
        subclip.write_videofile(output_path, codec="libx264", fps=clip.fps, audio_codec="aac")

        # Cleanup
        clip.close()
        subclip.close()
        print(f"✅ Saved clip: {output_path}")
    except Exception as e:
        print(f"❌ Error extracting clip: {e}")

def read_timestamps(file_path):
    """Reads timestamps from a text file and returns a list of tuples."""
    print(f"📂 Reading timestamps from: {file_path}")

    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        timestamps = []
        for line in lines:
            if '-' in line:
                start, end = line.strip().split('-')
                timestamps.append((start.strip(), end.strip()))
            else:
                print(f"⚠ Skipping invalid line: {line.strip()}")

        print(f"✅ Timestamps read successfully: {timestamps}")
        return timestamps
    except Exception as e:
        print(f"❌ Error reading timestamps file: {e}")
        return []

def time_to_seconds(timestamp):
    """Converts a timestamp (MM:SS or HH:MM:SS) to total seconds."""
    print(f"⏱ Converting timestamp to seconds: {timestamp}")

    try:
        parts = list(map(int, timestamp.split(':')))
        if len(parts) == 2:  # Format: MM:SS
            minutes, seconds = parts
            return minutes * 60 + seconds
        elif len(parts) == 3:  # Format: HH:MM:SS
            hours, minutes, seconds = parts
            return hours * 3600 + minutes * 60 + seconds
    except Exception as e:
        print(f"❌ Error converting timestamp {timestamp}: {e}")
        return None

def extract_and_resize_clips(video_path, timestamps, output_folder):
    """Extracts video segments based on timestamps and resizes them to 1080x1920."""
    print(f"📹 Processing video: {video_path}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"📁 Created output directory: {output_folder}")

    clip_paths = []
    
    for idx, (start, end) in enumerate(timestamps):
        print(f"🎬 Processing clip {idx + 1}: {start} to {end}")

        start_sec = time_to_seconds(start)
        end_sec = time_to_seconds(end)

        if start_sec is None or end_sec is None:
            print(f"⚠ Skipping invalid timestamps: {start} - {end}")
            continue

        temp_output_path = os.path.join(output_folder, f"temp_clip_{idx + 1}.mp4")

        try:
            print(f"🔪 Extracting subclip: {start_sec}s to {end_sec}s")
            extract_clip_moviepy(video_path, start_sec, end_sec, temp_output_path)
            
            temp_file_size = os.path.getsize(temp_output_path)
            print(f"Temporary file size: {temp_file_size}")

            if temp_file_size == 0:
                print(f"❌ ERROR: Extracted temp clip is empty. MoviePy extraction failed.")
                continue

            temp_clip_test = VideoFileClip(temp_output_path)
            if temp_clip_test.duration == 0:
                print(f"❌ ERROR: Extracted temp clip has 0 duration, extraction failed")
                temp_clip_test.close()
                os.remove(temp_output_path)
                continue
            temp_clip_test.close()

        except Exception as e:
            print(f"❌ Error extracting subclip: {e}")
            continue

        try:
            print(f"📏 Checking extracted clip {idx + 1}")
            clip = VideoFileClip(temp_output_path)
            fps = clip.fps

            if clip.duration == 0:
                print(f"⚠ Extracted clip {idx + 1} is empty! Skipping...")
                clip.close()
                os.remove(temp_output_path)
                continue
            
            
            # Resize the video dimensions in 1080 x 1920
            clip = clip.resized(height=1920)
            cropper = Crop(width=1080, height=1920, x_center=clip.w / 2, y_center=clip.h / 2)
            clip = cropper.apply(clip)
            
            final_output_path = os.path.join(output_folder, f"clip_{idx + 1}.mp4")
            clip.write_videofile(final_output_path, codec="libx264", fps=fps, audio_codec="aac")
            print(f"✅ Saved clip {idx + 1} at {final_output_path}")
            clip_paths.append(final_output_path)

        except Exception as e:
            print(f"❌ Error saving clip {idx + 1}: {e}")
        finally:
            if 'clip' in locals():
                clip.close()

        try:
            os.remove(temp_output_path)
            print(f"🗑 Deleted temporary file: {temp_output_path}")
        except Exception as e:
            print(f"⚠ Error deleting temp file: {e}")
    return clip_paths

def get_video_duration(video_path):
    """Gets the duration of a video file in seconds."""
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception as e:
        print(f"❌ Error getting video duration: {e}")
        return 0

def time_to_seconds_to_timestamp(seconds):
    """Converts seconds to a timestamp string (MM:SS)."""
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def generate_subtitles(clip_paths, output_folder):
    """Extracts audio from clips and generates subtitles."""
    model = whisper.load_model("small", device="cpu")  # For better Hindi accuracy change it to medium
    for clip_path in clip_paths:
        try:
            audio_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(clip_path))[0]}.mp3") # changed to .mp3
            video_clip = VideoFileClip(clip_path)
            video_clip.audio.write_audiofile(audio_path, codec="mp3") # changed to mp3
            video_clip.close()

            result = model.transcribe(audio_path, language="hi")
            segments = result["segments"]

            srt_path = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(clip_path))[0]}.srt")
            with open(srt_path, "w", encoding="utf-8") as srt_file:
                for segment in segments:
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"].strip()
                    start_ms = int(start * 1000)
                    end_ms = int(end * 1000)
                    start_str = f"{start_ms // 3600000:02d}:{(start_ms % 3600000) // 60000:02d}:{(start_ms % 60000) // 1000:02d},{start_ms % 1000:03d}"
                    end_str = f"{end_ms // 3600000:02d}:{(end_ms % 3600000) // 60000:02d}:{(end_ms % 60000) // 1000:02d},{end_ms % 1000:03d}"
                    srt_file.write(f"{segment['id'] + 1}\n{start_str} --> {end_str}\n{text}\n\n")

            print(f"✅ Subtitles generated for {clip_path} at {srt_path}")
            os.remove(audio_path)  # Delete the audio file after subtitle creation.

        except Exception as e:
            print(f"❌ Error generating subtitles for {clip_path}: {e}")
            print(f"Debug Info: {e}") # Debugging tool


def add_subtitles(video_path, subtitles_path, output_path):
    """Adds subtitles using FFmpeg with proper path escaping."""
    # Convert to absolute paths and normalize
    
    video_path = os.path.abspath(video_path)
    subtitles_path = os.path.abspath(subtitles_path)
    output_path = os.path.abspath(output_path)


    # Subtitle path
    font_path = "input_files/font.ttf"
    font_path = os.path.abspath(font_path).replace("\\", "\\\\")
    subtitles_path_escaped = os.path.abspath(subtitles_path).replace("\\", "\\\\")
    
    # Escape backslashes in paths
    subtitles_path = subtitles_path.replace("\\", "\\\\")
    # Remove all files in final_videos
    [os.remove(os.path.join(base_dir, "final_videos", f)) for f in os.listdir(os.path.join(base_dir, "final_videos")) if os.path.isfile(os.path.join(base_dir, "final_videos", f))]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    escaped_path = subtitles_path.replace(':', '\\:').replace('\\', '\\\\')

    cmd = [
    "ffmpeg",
    "-i", video_path,
    "-vf", f"subtitles={escaped_path}:force_style='FontFile={font_path}'",
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
    video_path = "input_files/sample_video.mp4"  # Replace with your video path
    timestamps_file = "input_files/timestamps.txt"  # Replace with your timestamps file path
    output_folder = "output_videos"  # Replace with the path where you want to save initial video

    folder_name = "final_videos"

# Method 1: Using os.mkdir() - creates only one directory
    try:
        os.mkdir(folder_name)
        print(f"Folder '{folder_name}' created successfully using os.mkdir()")
    except FileExistsError:
        print(f"Folder '{folder_name}' already exists.")


    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
    elif not os.path.exists(timestamps_file):
        print(f"❌ Timestamps file not found: {timestamps_file}")
    else:
        video_duration = get_video_duration(video_path)
        print("Found the file!!!")
        print(f"ℹ️ Video duration: {video_duration} seconds")

        timestamps = read_timestamps(timestamps_file)

        adjusted_timestamps = []
        for start, end in timestamps:
            start_sec = time_to_seconds(start)
            end_sec = time_to_seconds(end)

            if start_sec is None or end_sec is None:
                print(f"⚠ Skipping invalid timestamps: {start} - {end}")
            elif start_sec >= video_duration:
                print(f"⚠ Start time {start} exceeds video duration. Skipping.")
            elif end_sec > video_duration:
                print(f"⚠ End time {end} exceeds video duration. Adjusting end time.")
                adjusted_timestamps.append((start, time_to_seconds_to_timestamp(video_duration)))
            else:
                adjusted_timestamps.append((start, end))

        clip_paths = extract_and_resize_clips(video_path, adjusted_timestamps, output_folder)
        generate_subtitles(clip_paths, output_folder)
        print("✅ Video processing complete! Clips and subtitles saved in 'output_videos' folder.")
        
        
        # Burning subtitles in the video
        print("✅ Now Burning Subtitles in the video.")
        
        # Make an iteration over the files present in folder
        # Still have to add
        VIDEO_FILE = "output_videos/clip_1.mp4"
        SUBTITLES_FILE = "output_videos/clip_1.srt"
        OUTPUT_FILE = "final_videos/final_file.mp4"
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        VIDEO_FILE_ABS = os.path.join(base_dir, VIDEO_FILE)
        SUBTITLES_FILE_ABS = os.path.join(base_dir, SUBTITLES_FILE)
        OUTPUT_FILE_ABS = os.path.join(base_dir, OUTPUT_FILE)

        add_subtitles(VIDEO_FILE_ABS, SUBTITLES_FILE_ABS, OUTPUT_FILE_ABS)
        print("✅ Subtitle addition process (using FFmpeg) initiated.")