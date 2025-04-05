import os
from moviepy import *

def annotate(clip, txt, txt_color='white'):
    """
    Writes a text at the bottom of the clip.
    """
    txtclip = TextClip(txt, font = "Hatten", font_size = 24, color=txt_color, stroke_color="black", stroke_width=5)
    annotated_clip = CompositeVideoClip([clip, txtclip.set_position(('center', 'bottom'))])
    return annotated_clip.set_duration(clip.duration)

def add_subtitles_to_videos(video_folder, subtitle_folder, output_folder, font_name):
    """
    Adds subtitles to video clips using corresponding .srt files.
    """

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]

    for video_file in video_files:
        video_name, _ = os.path.splitext(video_file)
        subtitle_file = os.path.join(subtitle_folder, f"{video_name}.srt")
        video_path = os.path.join(video_folder, video_file)

        if os.path.exists(subtitle_file):
            try:
                try:
                    video = VideoFileClip(video_path)
                except Exception as e:
                    print(f"❌ Error loading video {video_file}: {e}")
                    continue

                print(f"Processing video: {video_file}")

                if not hasattr(video, 'subclipped'):
                    print(f"❌ Error: 'subclipped' method not found in VideoFileClip")
                    video.close()
                    continue

                # Sample subtitles - In reality, you should parse the .srt file
                subs = [((0, 4), "Subtitle 1"),
                        ((4, 9), "Subtitle 2"),
                        ((9, 12), "Subtitle 3"),
                        ((12, 16), "Subtitle 4")]

                annotated_clips = []
                for (from_t, to_t), txt in subs:
                    try:
                        sub_clip = video.subclipped(from_t, to_t)
                        annotated_clips.append(annotate(sub_clip, txt, font_name=font_name))
                        sub_clip.close()
                    except Exception as e:
                        print(f"❌ Error processing subtitle ({from_t}-{to_t}): {e}")

                final_clip = concatenate_videoclips(annotated_clips)
                output_path = os.path.join(output_folder, f"{video_name}_with_subs.mp4")
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

                print(f"✅ Subtitles added to {video_file} and saved as {os.path.basename(output_path)}")
                video.close()
                final_clip.close()

            except Exception as e:
                print(f"❌ Error adding subtitles to {video_file}: {e}")
        else:
            print(f"⚠ Subtitle file not found for {video_file}: {subtitle_file}")

if __name__ == "__main__":
    video_folder = "output_videos"
    subtitle_folder = "output_videos"
    output_folder = "final_videos"
      # Use the actual installed font name

    add_subtitles_to_videos(video_folder, subtitle_folder, output_folder)
    print("✅ Subtitle addition process complete.")
