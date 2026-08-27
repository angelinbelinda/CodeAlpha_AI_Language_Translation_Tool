# 🌐 AI Language Translator

An AI-powered language translation application developed using Python and Tkinter. The application allows users to translate text between multiple languages and also provides voice input, text-to-speech, translation history, copy, and language swap features.

## 📌 Project Overview

The AI Language Translator is a desktop-based translation application that provides real-time text translation between multiple languages.

The application uses an online translation service to translate the entered text. It also supports voice input using speech recognition and can read translated text aloud using text-to-speech.

Translation history is automatically stored locally in a JSON file so previous translations can be accessed easily.

## ✨ Features

- 🌐 Translate text between multiple languages
- 🔄 Swap source and target languages
- 🎤 Voice input using microphone
- 🔊 Text-to-speech for translated text
- 📋 Copy translated text
- 🗑️ Clear input and output
- 🕘 Translation history
- 💾 Save translation history in JSON format
- ⚡ Background translation using threading
- ⚠️ Error handling for translation and voice services
- 🖥️ User-friendly Tkinter graphical interface
- 📝 Supports up to 5000 characters per translation

## 🛠️ Technologies Used

- Python
- Tkinter – Graphical User Interface
- Requests – Communication with the translation API
- MyMemory Translation API – Text translation
- SpeechRecognition – Voice-to-text conversion
- SoundDevice – Microphone audio recording
- gTTS (Google Text-to-Speech) – Text-to-speech generation
- playsound3 – Playing generated speech
- JSON – Storing translation history
- Threading – Running translation in the background

## 📂 Project Structure

AI-Language-Translator/
│
├── app.py
│
├── translation_history.json
│
└── README.md

## 📄 File Description

app.py
Main Python application containing the GUI, translation system, voice input, text-to-speech, language selection, history, and other features.

translation_history.json
Stores the user's previous translation history.

README.md
Contains information about the project, features, technologies, and project structure.

## 🚀 How to Run

1. Clone the repository

git clone YOUR_GITHUB_REPOSITORY_LINK

2. Open the project folder

cd AI-Language-Translator

3. Install the required libraries

pip install deep-translator requests pyttsx3 SpeechRecognition sounddevice gTTS playsound3

4. Run the application

python app.py

## 💡 How It Works

1. Select the source language.
2. Select the target language.
3. Enter text or use the Voice button.
4. Click Translate.
5. The translated text appears in the output area.
6. Use Copy to copy the translation.
7. Use Speak to hear the translated text.
8. Previous translations are saved in the translation history.

## 🎯 Project Objective

The main objective of this project is to create a simple and user-friendly translation application that combines text translation, speech recognition, text-to-speech, and translation history in one desktop application.

## 👩‍💻 Developed By

Angelin Belinda A
