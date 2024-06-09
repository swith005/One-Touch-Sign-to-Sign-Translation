import os
import subprocess
import urllib.parse
import tempfile
import requests
import azure.cognitiveservices.speech as speech_sdk
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from action_recognition import get_sign_translation


ALLOWED_EXTENSIONS = {'mp4'}
SUPPORTED_SOURCE_LANGUAGES = {'asl'}
SUPPORTED_TARGET_LANGUAGES = {'ssl', 'csl'}
language_map = {'asl' : 'en', 'ssl' : 'es', 'csl' : 'zh'}

subprocess.run("gcloud auth activate-service-account ms-innovation-challenge@helpful-house-425117-p1.iam.gserviceaccount.com --key-file=demo/artifacts/gkey.json --project=helpful-house-425117-p1", shell=True, check=True, capture_output=True)
access_token = subprocess.check_output(['gcloud', 'auth', 'print-access-token']).decode().strip()
headers = {'Authorization': 'Bearer ' + access_token}

load_dotenv()

app = Flask(__name__)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/sign_translation', methods=['POST'])
def sign_translation():
    args = request.json
    source = args['source']
    target = args['target']
    output_format = args['output_format']
    video_uri = args['video_uri']   

    # get the sign translation from video recognition API
    text_translation = get_sign_translation(video_uri, headers)
    text_translation = text_translation['translation']
    print('got translation: {}'.format(text_translation))

    # Call the appropriate function based on the output_format
    if output_format == 'speech':
        return send_file(sign_to_speech(source, target, text_translation))
    elif output_format == 'sign_language':
        output = sign_to_sign(target, text_translation)
        return send_file(output)
    else:
        return jsonify(sign_to_text(source, target, text_translation))
    

# def sign_translation():
#     # check if the post request has the file part
#     if 'file' not in request.files:
#         return jsonify({'error': 'No file part'})
    
#     file = request.files['file']
#     # If the user does not select a file, the browser submits an
#     # empty file without a filename.
#     if file.filename == '':
#         return jsonify({'error': 'No selected file'})
    
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         # store to temporary file
#         with tempfile.TemporaryDirectory() as tmpdirname:
#             file.save(os.path.join(tmpdirname, filename))
            
#             # Call the sign language recognition API
#             test = "Hello World!"
#             args = request.form
#             source = args['source']
#             target = args['target']
#             output_format = args['output_format']

#             # Call the appropriate function based on the output_format
#             if output_format == 'speech':
#                 return send_file(sign_to_speech(source, target, test))
#             elif output_format == 'sign_language':
#                 return sign_to_sign(source, target, test)
#             else:
#                 return jsonify(sign_to_text(source, target, test))

#     return jsonify({'error': 'Invalid file extension'})

def sign_to_text(source, target, text):
    print('getting translation in text form')
    if source not in SUPPORTED_SOURCE_LANGUAGES or target not in SUPPORTED_TARGET_LANGUAGES:
        return {'error': 'Unsupported language'}
    
    text = text.replace('_', ' ')

    headers = {'Ocp-Apim-Subscription-Key': os.getenv('SUBSCRIPTION_KEY'), 
               'Ocp-Apim-Subscription-Region': os.getenv('SUBSCRIPTION_REGION'),
               'Content-Type': 'application/json; charset=UTF-8'}
    
    url = "https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={}&to={}".format(language_map[source], language_map[target])
    body = [{'Text': text}]
    response = requests.post(url, headers=headers, data=str(body))

    if response.status_code == 200:
        translation = response.json()[0]['translations'][0]['text']    
        return {'translation': translation}
    
    return None

def sign_to_speech(source, target, text):
    print('getting translation in speech form')
    if source not in SUPPORTED_SOURCE_LANGUAGES or target not in SUPPORTED_TARGET_LANGUAGES:
        return {'error': 'Unsupported sign language'}

    translation = sign_to_text(source, target, text)

    speech_config = speech_sdk.SpeechConfig(os.getenv('SPEECH_KEY'), os.getenv('SPEECH_REGION'))
    # The neural multilingual voice can speak different languages based on the input text.
    speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'  
    speech_synthesizer = speech_sdk.SpeechSynthesizer(speech_config)
    result = speech_synthesizer.speak_text_async(translation['translation']).get()    

    if result.reason == speech_sdk.ResultReason.SynthesizingAudioCompleted:
        file_path = os.path.join(tempfile.gettempdir(), 'output.wav')
        with open(file_path, 'wb') as file:
            file.write(result.audio_data)
        return file_path
    
    return {'error': 'Failed to synthesize audio'}
        
def sign_to_sign(target, text):
    # Call the sign language recognition API
    if target not in SUPPORTED_TARGET_LANGUAGES:
        return {'error': 'Unsupported language'}
    
    if target == 'csl':
        object_name = urllib.parse.quote_plus(f'zh/csl_{text}.mp4')

    elif target == 'ssl':
        object_name = urllib.parse.quote_plus(f'es/ssl_{text}.mp4')
     
    r = requests.get(f'https://storage.googleapis.com/storage/v1/b/asl_signed_videos/o/{object_name}?alt=media', headers=headers)

    if r.status_code == 200:
        
        file_path = os.path.join(tempfile.gettempdir(), 'output.mp4')
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
            return file_path
    
    return {'error': 'Failed to get translated sign language video'}

def get_voice_name(language):
    language = language_map[language]
    if language == 'en':
        return 'en-US-AriaNeural'
    elif language == 'es':
        return 'es-ES-AlvaroNeural'
    elif language == 'zh':
        return 'zh-CN-XiaochenMultilingualNeural'
    else:
        return 'en-US-AvaMultilingualNeural'  


def upload_to_GCS_blob(bucket_name, source_file_name, destination_blob_name):
    from google.cloud import storage
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    return blob.public_url

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False)