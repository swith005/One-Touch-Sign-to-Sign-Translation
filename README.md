# One-Touch-Sign-to-Sign-Translation

## Table of Contents
- [Description](#description)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [How to Run](#how-to-run)
- [Demo](#demo)

## Description <a name="description"></a>
One-Touch-Sign-to-Sign Translation is an API service for enabling Sign-to-Sign Language Translation and Sign-to-Text Interpretation for inclusive global communication. 
<html>
<div style="text-align: center;">
<img src="images/STS_STT Design Diagram.jpg" width="100%">
</div>
</html>

## Prerequisites <a name="prerequisites"></a>
Before you begin, ensure that you have the following prerequisites:
- [Azure AI Translation Credentials](https://learn.microsoft.com/en-us/azure/ai-services/translator/translator-overview)
- [Azure Speech Credentials](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech)
- [gcloud CLI](https://cloud.google.com/sdk/docs/install)
- [gcloud SDK](https://cloud.google.com/sdk?hl=en)

## Getting Started <a name="getting-started"></a>
To get started with the One-Touch-Sign-to-Sign-Translation project, follow these steps:

### 1. Install required python libraries: 
```
pip install -r requirements.txt
```
### 2. Modify .env file for Azure AI services
Open the [.env](.env) file and add the required credentials for **Azure AI Translation** in the   `SUBSCRIPTION_KEY` and `SUBSCRIPTION_REGION`. Then add the required credentials for the **Azure Text-to-Speech** service in 
`SPEECH_KEY` and `SPEECH_REGION`

### 3. Add gcloud credentials for authentication to action recognition service 
- Copy the [limited access service_account](https://storage.googleapis.com/asl_signed_videos/service_key/key1.json) details provided for demoing to [gkey.json](demo/artifacts/gkey.json) 

### 4. Add gcloud to ~/.bash_profile
```
source '[path-to-my-home]/google-cloud-sdk/path.bash.inc'

source '[path-to-my-home]/google-cloud-sdk/completion.bash.inc'

```

## How to Run <a name="how-to-run"></a>
 Start the One Touch flask web service:
```
python sign_translation.py
```

Now you can utilize the web service to enable Sign-to-Sign and Sign-to-Text following the [notebook demo](demo/STS_STT_Demo.ipynb) 

## Demo <a name="demo"></a>
### You can watch a demo of our service [here](https://drive.google.com/file/d/1ilivBsuo1bOXym33dONgIB7F7jJaIJHQ/view?usp=drive_link)
