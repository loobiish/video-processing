print("1")
import whisper
print("2")
model = whisper.load_model("medium")
print("3")
result = model.transcribe("output_videos/clip_1.mp4", language="hi")
print(result["text"])
print("4")