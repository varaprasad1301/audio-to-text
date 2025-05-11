from fastapi import FastAPI, UploadFile, File
import requests
import time
import re

app = FastAPI()

# Replace with your AssemblyAI API key
ASSEMBLYAI_API_KEY = "32d6d3bf843b4fc282150b8639dfbef6"

# Headers for API calls
HEADERS = {
    "authorization": ASSEMBLYAI_API_KEY,
    "content-type": "application/json"
}

upload_headers = {
    "authorization": ASSEMBLYAI_API_KEY,
}


def extract_amount_and_description(text):
    # Extract amount
    amount_match = re.search(r'\b(?:Rs\.?|INR)?\s?(\d+(?:\.\d{1,2})?)\b', text)
    amount = amount_match.group(1) if amount_match else "Not found"

    # Assume description is the remaining sentence without amount
    if amount != "Not found":
        description = text.replace(amount_match.group(0), "").strip()
    else:
        description = text.strip()

    return {"amount": amount, "description": description}


@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Upload audio file to AssemblyAI
    audio_data = await file.read()
    upload_response = requests.post(
        "https://api.assemblyai.com/v2/upload",
        headers=upload_headers,
        data=audio_data
    )

    if upload_response.status_code != 200:
        return {"error": "Failed to upload audio to AssemblyAI"}

    audio_url = upload_response.json()["upload_url"]

    # Request transcription
    transcript_request = {
        "audio_url": audio_url
    }

    transcript_response = requests.post(
        "https://api.assemblyai.com/v2/transcript",
        json=transcript_request,
        headers=HEADERS
    )

    if transcript_response.status_code != 200:
        return {"error": "Failed to request transcription"}

    transcript_id = transcript_response.json()["id"]
    polling_endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    # Poll for completion
    while True:
        poll_response = requests.get(polling_endpoint, headers=HEADERS)
        status = poll_response.json()["status"]

        if status == "completed":
            text = poll_response.json()["text"]
            result = extract_amount_and_description(text)
            return {
                "transcript": text,
                "parsed_data": result
            }
        elif status == "error":
            return {"error": "Transcription failed"}
        time.sleep(3)
#  TO run the code use this command  // uvicorn main:app --reload
