import requests
import subprocess
import jsonlines
from tempfile import TemporaryDirectory

def get_sign_translation(video_uri, headers):
    print('calling action recognition service')
    # with TemporaryDirectory() as tmpdirname:
    #     content = {'content': video_uri, 'mimeType': 'video/mp4','timeSegmentStart': '0.0s', 'timeSegmentEnd': 'Infinity'}
    #     with jsonlines.open('output.jsonl', 'w') as writer:
    #         writer.write_all(content)

    data = {
    "displayName": "hello_python_test",
    "model": "projects/helpful-house-425117-p1/locations/us-central1/models/8671383114850762752",
    "modelParameters": {
      "confidenceThreshold": 0.7,
    },
    "inputConfig": {
        "instancesFormat": "jsonl",
        "gcsSource": {
            "uris": [video_uri],
        },
    },
    "outputConfig": {
        "predictionsFormat": "jsonl",
        "gcsDestination": {
            "outputUriPrefix": "gs://asl_signed_videos/",
        },
    },
    }

    response = requests.post('https://us-central1-aiplatform.googleapis.com/v1/projects/helpful-house-425117-p1/locations/us-central1/batchPredictionJobs', headers=headers, json=data)
    jobid = response.json()['name'].split('/')[-1]

    
    state = 'JOB_STATE_RUNNING'
    while state == 'JOB_STATE_RUNNING':
        response = requests.get('https://us-central1-aiplatform.googleapis.com/v1/projects/helpful-house-425117-p1/locations/us-central1/batchPredictionJobs/' + jobid, headers=headers)
        state = response.json()['state']
        
    if state == 'JOB_STATE_SUCCEEDED':
        output = response.json()['outputInfo']['gcsOutputDirectory']  
        output = output.split('gs://')[-1]  
        r = requests.get(f'https://storage.googleapis.com/{output}/predictions_00001.jsonl')
        translation = r.json()['prediction'][0]['displayName']

        print('done with action recognition service')
        return {'translation': translation}
