
#  To ertract the text from the audio file using the "pydub speech recoginition library"



from fastapi import FastAPI, UploadFile, File
from pydub import AudioSegment
import speech_recognition as sr
import re
import os
import uuid

app = FastAPI()

def convert_audio_to_wav(input_path, output_path):
    audio = AudioSegment.from_file(input_path)
    audio.export(output_path, format="wav")
    return output_path

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand audio"
    except sr.RequestError:
        return "Speech recognition API unavailable"

def extract_amount_and_description(text):
    amount_match = re.search(r'\b(?:Rs\.?|INR)?\s?(\d+(?:\.\d{1,2})?)\b', text)
    amount = amount_match.group(1) if amount_match else "Not found"
    description = text.replace(amount_match.group(0), "").strip() if amount != "Not found" else text.strip()
    return {"amount": amount, "description": description}

@app.post("/upload-audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Save uploaded file temporarily
    input_filename = f"temp_{uuid.uuid4().hex}.m4a"
    with open(input_filename, "wb") as f:
        f.write(await file.read())

    wav_filename = input_filename.replace(".m4a", ".wav")
    convert_audio_to_wav(input_filename, wav_filename)

    # Transcribe and extract data
    transcribed_text = transcribe_audio(wav_filename)
    parsed_data = extract_amount_and_description(transcribed_text)

    # Clean up
    os.remove(input_filename)
    os.remove(wav_filename)

    return {
        "transcript": transcribed_text,
        "parsed_data": parsed_data
    }
#  To run the program use the cmd as  the  "uvicorn main1:app --reload"
