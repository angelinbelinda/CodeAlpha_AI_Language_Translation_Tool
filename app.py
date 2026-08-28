import tkinter as tk
from tkinter import ttk, messagebox
from deep_translator import GoogleTranslator
import json
import os
import threading
import tempfile
import time
import speech_recognition as sr
import sounddevice as sd
from gtts import gTTS
from playsound3 import playsound


# =========================================================
# LANGUAGE LIST
# =========================================================

LANGUAGES = {
    "English": "en",
    "Tamil": "ta",
    "Hindi": "hi",
    "Telugu": "te",
    "Malayalam": "ml",
    "Kannada": "kn",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "Punjabi": "pa",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Italian": "it",
    "Portuguese": "pt",
    "Russian": "ru",
    "Arabic": "ar",
    "Japanese": "ja",
    "Korean": "ko",
    "Chinese": "zh-CN"
}


# =========================================================
# HISTORY
# =========================================================

HISTORY_FILE = "translation_history.json"


def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception:
        pass

    return []


history = load_history()


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                history,
                file,
                ensure_ascii=False,
                indent=4
            )
    except Exception:
        pass


# =========================================================
# TRANSLATION
# =========================================================

def start_translation():

    text = input_text.get("1.0", tk.END).strip()

    if not text:
        messagebox.showwarning(
            "Empty Text",
            "Please enter some text."
        )
        return

    if len(text) > 5000:
        messagebox.showwarning(
            "Text Too Long",
            "Please enter less than 5000 characters."
        )
        return

    source = source_language.get()
    target = target_language.get()

    if not source or not target:
        messagebox.showwarning(
            "Language Selection",
            "Please select both languages."
        )
        return

    # Same language
    if source == target:

        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, text)

        status_label.config(
            text="✓ Same language selected"
        )

        return

    source_code = LANGUAGES[source]
    target_code = LANGUAGES[target]

    translate_button.config(
        state="disabled"
    )

    status_label.config(
        text="⏳ Translating..."
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    # Run translation in background
    thread = threading.Thread(
        target=translate_text,
        args=(
            text,
            source,
            target,
            source_code,
            target_code
        ),
        daemon=True
    )

    thread.start()


# =========================================================
# GOOGLE TRANSLATION
# =========================================================

def translate_text(
    text,
    source,
    target,
    source_code,
    target_code
):

    max_retries = 3

    for attempt in range(max_retries):

        try:

            translator = GoogleTranslator(
                source=source_code,
                target=target_code
            )

            translated = translator.translate(text)

            if not translated:
                raise Exception(
                    "No translation was received."
                )

            # Return result to main Tkinter thread
            window.after(
                0,
                lambda: translation_success(
                    text,
                    source,
                    target,
                    translated
                )
            )

            return

        except Exception as error:

            # If this was not the final attempt,
            # wait briefly and try again
            if attempt < max_retries - 1:

                time.sleep(1)

            else:

                # All 3 attempts failed
                window.after(
                    0,
                    lambda e=str(error): translation_failed(e)
                )

# =========================================================
# TRANSLATION SUCCESS
# =========================================================

def translation_success(
    original,
    source,
    target,
    translated
):

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        translated
    )

    # Add to history
    history.insert(
        0,
        {
            "source": source,
            "target": target,
            "original": original,
            "translation": translated
        }
    )

    # Keep latest 50 translations
    del history[50:]

    save_history()
    refresh_history()

    translate_button.config(
        state="normal"
    )

    status_label.config(
        text="✓ Translation completed successfully"
    )


# =========================================================
# TRANSLATION ERROR
# =========================================================

def translation_failed(error):

    translate_button.config(
        state="normal"
    )

    status_label.config(
        text="✗ Translation failed"
    )

    messagebox.showerror(
        "Translation Error",
        "Could not translate the text.\n\n"
        "Please check your internet connection "
        "and try again.\n\n"
        f"Details: {error}"
    )


# =========================================================
# CLEAR
# =========================================================

def clear_text():

    input_text.delete(
        "1.0",
        tk.END
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    status_label.config(
        text="Ready"
    )


# =========================================================
# SWAP LANGUAGES
# =========================================================

def swap_languages():

    source = source_language.get()
    target = target_language.get()

    source_language.set(target)
    target_language.set(source)

    old_input = input_text.get(
        "1.0",
        tk.END
    ).strip()

    old_output = output_text.get(
        "1.0",
        tk.END
    ).strip()

    input_text.delete(
        "1.0",
        tk.END
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    input_text.insert(
        tk.END,
        old_output
    )

    output_text.insert(
        tk.END,
        old_input
    )

    status_label.config(
        text="✓ Languages swapped"
    )


# =========================================================
# COPY
# =========================================================

def copy_translation():

    translated = output_text.get(
        "1.0",
        tk.END
    ).strip()

    if not translated:

        messagebox.showwarning(
            "Nothing to Copy",
            "There is no translation to copy."
        )

        return

    window.clipboard_clear()
    window.clipboard_append(translated)
    window.update()

    status_label.config(
        text="✓ Translation copied"
    )


# =========================================================
# SPEAK TRANSLATION
# =========================================================

def speak_translation():

    text = output_text.get(
        "1.0",
        tk.END
    ).strip()

    if not text:

        messagebox.showwarning(
            "Nothing to Speak",
            "Please translate some text first."
        )

        return

    target = target_language.get()
    target_code = LANGUAGES[target]

    speak_button.config(
        state="disabled"
    )

    status_label.config(
        text=f"🔊 Preparing speech in {target}..."
    )

    thread = threading.Thread(
        target=speak_text,
        args=(text, target, target_code),
        daemon=True
    )

    thread.start()


def speak_text(text, target, target_code):

    audio_file = None

    try:

        # Create temporary MP3 file
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        audio_file = temp_file.name
        temp_file.close()

        speech = gTTS(
            text=text,
            lang=target_code,
            slow=False
        )

        speech.save(audio_file)

        window.after(
            0,
            lambda: status_label.config(
                text=f"🔊 Speaking in {target}"
            )
        )

        playsound(audio_file)

        window.after(
            0,
            lambda: speech_finished()
        )

    except Exception as error:

        window.after(
            0,
            lambda: speech_failed(
                str(error)
            )
        )

    finally:

        if audio_file:

            try:
                os.remove(audio_file)
            except Exception:
                pass


def speech_finished():

    speak_button.config(
        state="normal"
    )

    status_label.config(
        text="✓ Speech completed"
    )


def speech_failed(error):

    speak_button.config(
        state="normal"
    )

    status_label.config(
        text="✗ Speech failed"
    )

    messagebox.showerror(
        "Speech Error",
        f"Could not generate speech.\n\n{error}"
    )


# =========================================================
# VOICE INPUT
# =========================================================

def voice_input():

    voice_button.config(
        state="disabled"
    )

    status_label.config(
        text="🎤 Listening..."
    )

    thread = threading.Thread(
        target=record_voice,
        daemon=True
    )

    thread.start()


def record_voice():

    try:

        recognizer = sr.Recognizer()

        sample_rate = 16000
        duration = 5

        # Record microphone
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="int16"
        )

        sd.wait()

        audio_data = sr.AudioData(
            recording.tobytes(),
            sample_rate,
            2
        )

        source = source_language.get()

        language_codes = {
            "English": "en-IN",
            "Tamil": "ta-IN",
            "Hindi": "hi-IN",
            "Telugu": "te-IN",
            "Malayalam": "ml-IN",
            "Kannada": "kn-IN",
            "Bengali": "bn-IN",
            "Marathi": "mr-IN",
            "Gujarati": "gu-IN",
            "Punjabi": "pa-IN",
            "French": "fr-FR",
            "German": "de-DE",
            "Spanish": "es-ES",
            "Italian": "it-IT",
            "Portuguese": "pt-PT",
            "Russian": "ru-RU",
            "Arabic": "ar-SA",
            "Japanese": "ja-JP",
            "Korean": "ko-KR",
            "Chinese": "zh-CN"
        }

        language_code = language_codes.get(
            source,
            LANGUAGES[source]
        )

        window.after(
            0,
            lambda: status_label.config(
                text="⏳ Converting speech to text..."
            )
        )

        text = recognizer.recognize_google(
            audio_data,
            language=language_code
        )

        window.after(
            0,
            lambda: voice_success(text)
        )

    except sr.UnknownValueError:

        window.after(
            0,
            lambda: voice_error(
                "Sorry, I could not understand what you said."
            )
        )

    except sr.RequestError as error:

        window.after(
            0,
            lambda: voice_error(
                f"Could not connect to speech recognition service.\n\n{error}"
            )
        )

    except Exception as error:

        window.after(
            0,
            lambda: voice_error(
                str(error)
            )
        )


def voice_success(text):

    input_text.delete(
        "1.0",
        tk.END
    )

    input_text.insert(
        tk.END,
        text
    )

    voice_button.config(
        state="normal"
    )

    status_label.config(
        text="✓ Voice input completed"
    )


def voice_error(error):

    voice_button.config(
        state="normal"
    )

    status_label.config(
        text="✗ Voice input failed"
    )

    messagebox.showerror(
        "Voice Input Error",
        error
    )


# =========================================================
# LOAD SELECTED HISTORY
# =========================================================

def load_selected_history(event=None):

    selection = history_list.curselection()

    if not selection:
        return

    index = selection[0]

    if index >= len(history):
        return

    item = history[index]

    source_language.set(
        item["source"]
    )

    target_language.set(
        item["target"]
    )

    input_text.delete(
        "1.0",
        tk.END
    )

    input_text.insert(
        tk.END,
        item["original"]
    )

    output_text.delete(
        "1.0",
        tk.END
    )

    output_text.insert(
        tk.END,
        item["translation"]
    )

    status_label.config(
        text="✓ History translation loaded"
    )


# =========================================================
# MAIN WINDOW
# =========================================================

window = tk.Tk()

window.title(
    "AI Language Translation Tool"
)

window.geometry(
    "950x720"
)

window.minsize(
    850,
    650
)


# =========================================================
# COLOUR THEME
# =========================================================

BG_COLOR = "#EEF2FF"
CARD_COLOR = "#FFFFFF"

PRIMARY_COLOR = "#4F46E5"
PRIMARY_DARK = "#3730A3"

SECONDARY_COLOR = "#7C3AED"
SECONDARY_DARK = "#6D28D9"

SUCCESS_COLOR = "#16A34A"
SUCCESS_DARK = "#15803D"

CLEAR_COLOR = "#64748B"
CLEAR_DARK = "#475569"

TEXT_COLOR = "#1E1B4B"
MUTED_COLOR = "#64748B"


window.configure(
    bg=BG_COLOR
)


# =========================================================
# TITLE
# =========================================================

title = tk.Label(
    window,
    text="🌐 AI LANGUAGE TRANSLATOR",
    font=("Arial", 24, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
)

title.pack(
    pady=(20, 5)
)


subtitle = tk.Label(
    window,
    text="REAL-TIME AI-POWERED LANGUAGE TRANSLATION",
    font=("Arial", 11),
    bg=BG_COLOR,
    fg=MUTED_COLOR
)

subtitle.pack(
    pady=(0, 15)
)


# =========================================================
# LANGUAGE SELECTION
# =========================================================

language_frame = tk.Frame(
    window,
    bg=BG_COLOR
)

language_frame.pack(
    pady=10
)


tk.Label(
    language_frame,
    text="From:",
    font=("Arial", 11, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).grid(
    row=0,
    column=0,
    padx=5
)


source_language = ttk.Combobox(
    language_frame,
    values=list(LANGUAGES.keys()),
    state="readonly",
    width=18
)

source_language.set(
    "English"
)

source_language.grid(
    row=0,
    column=1,
    padx=5
)


swap_button = tk.Button(
    language_frame,
    text="⇄ SWAP",
    command=swap_languages,
    font=("Arial", 10, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    relief="flat",
    padx=12,
    pady=5,
    cursor="hand2"
)

swap_button.grid(
    row=0,
    column=2,
    padx=15
)


tk.Label(
    language_frame,
    text="To:",
    font=("Arial", 11, "bold"),
    bg=BG_COLOR,
    fg=TEXT_COLOR
).grid(
    row=0,
    column=3,
    padx=5
)


target_language = ttk.Combobox(
    language_frame,
    values=list(LANGUAGES.keys()),
    state="readonly",
    width=18
)

target_language.set(
    "Tamil"
)

target_language.grid(
    row=0,
    column=4,
    padx=5
)


# =========================================================
# TEXT FRAME
# =========================================================

text_frame = tk.Frame(
    window,
    height=330,
    bg=BG_COLOR
)

text_frame.pack(
    fill="x",
    padx=20,
    pady=10
)

text_frame.pack_propagate(False)


# =========================================================
# INPUT
# =========================================================

input_frame = tk.LabelFrame(
    text_frame,
    text="  Enter Text  ",
    font=("Arial", 11, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=10
)

input_frame.pack(
    side="left",
    fill="both",
    expand=True,
    padx=(0, 8)
)


input_text = tk.Text(
    input_frame,
    font=("Arial", 12),
    wrap="word",
    bg="#FFFFFF",
    fg=TEXT_COLOR,
    insertbackground=PRIMARY_COLOR,
    relief="flat",
    bd=0,
    padx=10,
    pady=10
)

input_text.pack(
    fill="both",
    expand=True
)


# =========================================================
# OUTPUT
# =========================================================

output_frame = tk.LabelFrame(
    text_frame,
    text="  Translation  ",
    font=("Arial", 11, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=10
)

output_frame.pack(
    side="right",
    fill="both",
    expand=True,
    padx=(8, 0)
)


output_text = tk.Text(
    output_frame,
    font=("Arial", 12),
    wrap="word",
    bg="#FFFFFF",
    fg=TEXT_COLOR,
    insertbackground=PRIMARY_COLOR,
    relief="flat",
    bd=0,
    padx=10,
    pady=10
)

output_text.pack(
    fill="both",
    expand=True
)


# =========================================================
# BUTTONS
# =========================================================

button_frame = tk.Frame(
    window,
    bg=BG_COLOR
)

button_frame.pack(
    pady=12
)


translate_button = tk.Button(
    button_frame,
    text="🌐 TRANSLATE",
    command=start_translation,
    font=("Arial", 11, "bold"),
    bg=PRIMARY_COLOR,
    fg="white",
    activebackground=PRIMARY_DARK,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
)

translate_button.grid(
    row=0,
    column=0,
    padx=5
)


clear_button = tk.Button(
    button_frame,
    text="🗑 CLEAR",
    command=clear_text,
    font=("Arial", 11, "bold"),
    bg=CLEAR_COLOR,
    fg="white",
    activebackground=CLEAR_DARK,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
)

clear_button.grid(
    row=0,
    column=1,
    padx=5
)


copy_button = tk.Button(
    button_frame,
    text="📋 COPY",
    command=copy_translation,
    font=("Arial", 11, "bold"),
    bg=SECONDARY_COLOR,
    fg="white",
    activebackground=SECONDARY_DARK,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
)

copy_button.grid(
    row=0,
    column=2,
    padx=5
)


speak_button = tk.Button(
    button_frame,
    text="🔊 SPEAK",
    command=speak_translation,
    font=("Arial", 11, "bold"),
    bg=SUCCESS_COLOR,
    fg="white",
    activebackground=SUCCESS_DARK,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
)

speak_button.grid(
    row=0,
    column=3,
    padx=5
)


voice_button = tk.Button(
    button_frame,
    text="🎤 VOICE",
    command=voice_input,
    font=("Arial", 11, "bold"),
    bg=SECONDARY_COLOR,
    fg="white",
    activebackground=SECONDARY_DARK,
    activeforeground="white",
    relief="flat",
    padx=20,
    pady=8,
    cursor="hand2"
)

voice_button.grid(
    row=0,
    column=4,
    padx=5
)


# =========================================================
# STATUS
# =========================================================

status_label = tk.Label(
    window,
    text="Ready",
    font=("Arial", 10, "bold"),
    bg=BG_COLOR,
    fg=SUCCESS_COLOR
)

status_label.pack(
    pady=5
)


# =========================================================
# HISTORY
# =========================================================

history_frame = tk.LabelFrame(
    window,
    text=" 🕘 Translation History ",
    font=("Arial", 11, "bold"),
    bg=CARD_COLOR,
    fg=TEXT_COLOR,
    padx=10,
    pady=8,
    bd=1,
    relief="solid"
)

history_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


history_list = tk.Listbox(
    history_frame,
    height=5,
    font=("Arial", 10),
    bg="#F8FAFC",
    fg=TEXT_COLOR,
    selectbackground=PRIMARY_COLOR,
    selectforeground="white",
    relief="flat",
    bd=0
)

history_list.pack(
    fill="x"
)


history_list.bind(
    "<Double-Button-1>",
    load_selected_history
)


# =========================================================
# REFRESH HISTORY
# =========================================================

def refresh_history():

    history_list.delete(
        0,
        tk.END
    )

    for item in history:

        original = item.get(
            "original",
            ""
        )

        display = (
            f"{item.get('source', '')} → "
            f"{item.get('target', '')} | "
            f"{original[:50]}"
        )

        history_list.insert(
            tk.END,
            display
        )


# =========================================================
# LOAD HISTORY AT STARTUP
# =========================================================

refresh_history()


# =========================================================
# RUN APPLICATION
# =========================================================

window.mainloop()