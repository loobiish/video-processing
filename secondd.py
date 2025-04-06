import os
from moviepy import *


def annotate(clip, txt, font_name): #, txt_color='white'
    """
    Writes a text at the bottom of the clip.
    """
    print("===============6=================")
    txtclip = TextClip(font = font_name, text=txt, font_size = 24, color='white', stroke_color="black", stroke_width=5) #, font = font_name
    print("===============7=================")
    annotated_clip = CompositeVideoClip([clip, txtclip.with_position(('center', 'bottom'))])
    print("===============8=================")
    return annotated_clip.with_duration(clip.duration)

def add_subtitles_to_videos(video_folder, subtitle_folder, output_folder, font_name): #, font_name
    """
    Adds subtitles to video clips using corresponding .srt files.
    """
    print("===============2=================")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
    print("===============3=================")
    for video_file in video_files:
        video_name, _ = os.path.splitext(video_file)
        subtitle_file = os.path.join(subtitle_folder, f"{video_name}.srt")
        video_path = os.path.join(video_folder, video_file)
        print("===============4=================")
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
                        print("===============5=================")
                        
                        sub_clip = video.subclipped(from_t, to_t)
                        annotated_clips.append(annotate(sub_clip, txt, font_name=font_name)) #, font_name=font_name
                        sub_clip.close()
                    except Exception as e:
                        print(f"❌ Error processing subtitle ({from_t}-{to_t}): {e}")

                final_clip = concatenate_videoclips(annotated_clips)
                output_path = os.path.join(output_folder, f"{video_name}_with_subs.mp4")
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
                print("===============9=================")

                print(f"✅ Subtitles added to {video_file} and saved as {os.path.basename(output_path)}")
                video.close()
                final_clip.close()
                print("===============10=================")
            except Exception as e:
                print(f"❌ Error adding subtitles to {video_file}: {e}")
        else:
            print(f"⚠ Subtitle file not found for {video_file}: {subtitle_file}")

if __name__ == "__main__":
    video_folder = "video-processing/output_videos"
    subtitle_folder = "video-processing/output_videos"
    output_folder = "video-processing/final_videos"
      # Use the actual installed font name
    print("===============1=================")
    add_subtitles_to_videos(video_folder, subtitle_folder, output_folder, font_name = "video-processing/input_files/font.ttf")
    print("✅ Subtitle addition process complete.")
    print("===============11=================")
