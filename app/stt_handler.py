import speech_recognition as sr
import requests
import os
import sys

# Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080/voice-receive")

def transcribe_and_send(audio_file_path):
    """
    This script would be called by Asterisk as an AGI script.
    It takes a recorded WAV file, transcribes it, and sends it to the FastAPI backend.
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio_data = recognizer.record(source)
            # Using Google Web Speech API (Free tier)
            text = recognizer.recognize_google(audio_data)
            print(f"Transcribed Text: {text}")
            
            # Send to FastAPI Backend
            payload = {
                "text": text,
                "phone": "919876543210" # In real AGI, you'd get this from Asterisk variables
            }
            response = requests.post(BACKEND_URL, json=payload)
            return response.json()
            
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        transcribe_and_send(sys.argv[1])
    else:
        print("Usage: python stt_handler.py <path_to_wav_file>")