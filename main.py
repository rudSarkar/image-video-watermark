from flask import Flask, render_template, request, jsonify
from PIL import Image
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip, ImageClip
import random
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    # Get the uploaded file
    file = request.files['file']

    # Save the file temporarily
    file_path = f'static/{file.filename}'
    file.save(file_path)

    # Check if it's an image or video
    if file.mimetype.startswith('image'):
        add_watermark_to_image(file_path)
        return jsonify(
            file=file_path,
            success="Image has been watermarked success"
        )
    elif file.mimetype.startswith('video'):
        add_watermark_video(file_path)
        return jsonify(
            file=file_path,
            success="Video has been watermarked success"
        )


def add_watermark_to_image(file_path):
    # Open the image file
    image = Image.open(file_path)

    # Convert the image to RGB mode
    image = image.convert("RGB")

    # Add a watermark to the image
    # Replace 'watermark.png' with your watermark image path
    watermark = Image.open('watermark.png')
    # Adjust the size of the watermark as per your preference
    watermark_size = (300, 300)
    watermark = watermark.resize(watermark_size, Image.ANTIALIAS)
    # Adjust the position of the watermark as per your preference
    watermark_position = (
        0, image.height - watermark_size[1])  # Left-down corner
    image.paste(watermark, watermark_position, mask=watermark)

    # Save the image with the watermark as a JPEG file
    image.save(file_path, "JPEG")

def delete_mp4_files(directory):
    # List all files in the directory
    files = os.listdir(directory)

    # Iterate over each file
    for file in files:
        # Check if the file ends with .mp4
        if file.endswith(".mp4"):
            # Construct the full file path
            file_path = os.path.join(directory, file)
            # Delete the file
            os.remove(file_path)

def add_watermark(video_clip, watermark_image):
    watermark = (ImageClip(watermark_image)
                 .set_duration(video_clip.duration)
                 .resize(height=200)  # adjust watermark size as needed
                 .margin(right=8, bottom=8, opacity=0)  # adjust margin and opacity
                 .set_position(("right", "bottom")))
    return CompositeVideoClip([video_clip, watermark])

def add_watermark_video(file_path):

    audio_path = "background.mp3"
    watermark_path = "watermark.png"

    # Remove audio from the video
    video_clip = VideoFileClip(file_path).subclip(0, 13)

    # Add new audio
    new_audio = AudioFileClip(audio_path)
    video_clip = video_clip.set_audio(new_audio)

    # Add watermark
    watermarked_clip = add_watermark(video_clip, watermark_path)

    # Write the final video with watermark using libx264 codec for both video and audio
    watermarked_clip.write_videofile(file_path, codec='libx264', audio_codec='aac')

    delete_mp4_files(os.getcwd())

if __name__ == '__main__':
    app.run(debug=True)
