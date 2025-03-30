import whisper
import os

model = whisper.load_model('base.en')

# Construct the audio path relative to the current script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
audio_path = os.path.join(script_dir, "output_videos", "clip_1.mp3")

try:
    result = model.transcribe(audio_path, fp16=False, language='English')
    print(result)
except FileNotFoundError:
    print(f"Error: Audio file not found at {audio_path}")
except Exception as e:
    print(f"An error occurred: {e}")