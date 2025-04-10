import gradio as gr
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import mediainfo
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import os

def convert_audio_format(uploaded_file):
    audio = AudioSegment.from_file(uploaded_file)
    converted_file = "converted_audio.wav"
    audio.export(converted_file, format="wav")
    return converted_file

def transcribe_audio(audio_file, language_code):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        transcribed_text = recognizer.recognize_google(audio_data, language=language_code)
    return transcribed_text

def get_word_timestamps(transliterated_text, search_word, audio_duration):
    words = transliterated_text.split()
    total_words = len(words)
    word_duration = audio_duration / total_words
    occurrences = []
    for i, word in enumerate(words):
        if search_word.lower() in word.lower():
            start_time = i * word_duration
            end_time = start_time + word_duration
            occurrences.append((start_time, end_time))
    return occurrences

def process_audio(audio_file, language_code, search_word):
    converted_file = convert_audio_format(audio_file)
    transcribed_text = transcribe_audio(converted_file, language_code)

    if language_code == "te":
        transliterated_text = transliterate(transcribed_text, sanscript.TELUGU, sanscript.ITRANS)
    elif language_code == "hi":
        transliterated_text = transliterate(transcribed_text, sanscript.DEVANAGARI, sanscript.ITRANS)
    elif language_code == "ta":
        transliterated_text = transliterate(transcribed_text, sanscript.TAMIL, sanscript.ITRANS)
    elif language_code == "ml":
        transliterated_text = transliterate(transcribed_text, sanscript.MALAYALAM, sanscript.ITRANS)
    elif language_code == "kn":
        transliterated_text = transliterate(transcribed_text, sanscript.KANNADA, sanscript.ITRANS)
    else:
        transliterated_text = transcribed_text

    audio_info = mediainfo(converted_file)
    audio_duration = float(audio_info['duration'])

    timestamps = get_word_timestamps(transliterated_text, search_word, audio_duration)

    return transcribed_text, transliterated_text, timestamps

iface = gr.Interface(
    fn=process_audio,
    inputs=[
        gr.Audio(type="filepath", label="Upload Audio File"),
        gr.Radio(["en", "te", "hi", "ta", "ml", "kn"], label="Select Language Code"),
        gr.Textbox(label="Enter the word to search for timestamps")
    ],
    outputs=[
        gr.Textbox(label="Transcribed Text"),
        gr.Textbox(label="Transliterated Text (English)"),
        gr.Textbox(label="Timestamps")
    ],
    title="Audio Transcription and Word Timestamp Extraction"
)

iface.launch(iface.launch(server_name="0.0.0.0", server_port=int(os.environ.get("PORT", 8000))))
