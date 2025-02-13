from flask import Flask, render_template, request, redirect, url_for
import os
from clipsai import ClipFinder, Transcriber, MediaEditor,AudioVideoFile
from datetime import datetime



app = Flask(__name__)

# Specify the upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)

    
    # Generate a new filename based on the current time
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Keep the original file extension
    _, file_extension = os.path.splitext(file.filename)
    new_filename = f"{timestamp}{file_extension}"




    # Save the uploaded file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
    file.save(filepath)




    transcriber = Transcriber()
    transcription = transcriber.transcribe(audio_file_path=filepath)

    
    clipfinder = ClipFinder()
    clips = clipfinder.find_clips(transcription=transcription)



    media_editor = MediaEditor()

    # use this if the file contains audio stream only
    # media_file = clipsai.AudioFile("/abs/path/to/audio_only_file.mp4")
    # use this if the file contains both audio and video stream
    media_file = AudioVideoFile(filepath)

    trimmed_clip_links = []

    # Loop through each clip in the clips list
    for index, clip in enumerate(clips):
        trimmed_filename = f'clipped_{index}_{new_filename}'  # Create a unique filename for each trimmed clip
        trimmed_media_file_path = f'static/{trimmed_filename}'  # Define the path for the trimmed media file
        
        # Call the trim method for each clip
        clip_media_file = media_editor.trim(
            media_file=media_file,
            start_time=clip.start_time,
            end_time=clip.end_time,
            trimmed_media_file_path=trimmed_media_file_path,
        )

        # Add the link to the trimmed clip in the list
        trimmed_clip_links.append(trimmed_media_file_path)
    

    # Generate HTML <a> tags for each trimmed clip link
    html_links = ''.join(f'<a href="{link}">Download Clip {index}</a><br>' for index, link in enumerate(trimmed_clip_links))

    # Now you can return or render the `html_links` wherever needed
    return html_links
    
   



if __name__ == '__main__':
    app.run(debug=True)