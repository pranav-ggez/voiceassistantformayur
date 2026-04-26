import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import datetime
import pyjokes
import PySimpleGUI as sg
import pyqrcode
from newsapi import NewsApiClient
import threading

# ---------------- CONFIG ----------------
phone_numbers = {"rishi": "1234567890", "sakshi": "0000000123", "mangesh": "0000000000"}
bank_account_numbers = {"tt": "123456789", "mm": "99999999933"}

newsapi = NewsApiClient(api_key="NEWS_API_KEY")

# ---------------- TTS INIT ----------------
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error:", e)

# ---------------- SAFE GUI UPDATE ----------------
def update_ui(window, message):
    window.write_event_value('-UPDATE-', message)

# ---------------- COMMAND MATCHING ----------------
def contains(command, *keywords):
    return any(word in command for word in keywords)

# ---------------- COMMAND EXECUTION ----------------
def execute_command(command, window):
    try:
        command = command.lower()

        if contains(command, "play"):
            song = command.replace("play", "").strip()
            if song:
                msg = f"Playing {song}"
                update_ui(window, msg)
                speak(msg)
                pywhatkit.playonyt(song)
            else:
                speak("What should I play?")

        elif contains(command, "date"):
            msg = str(datetime.date.today())
            update_ui(window, msg)
            speak(msg)

        elif contains(command, "time"):
            msg = datetime.datetime.now().strftime('%H:%M')
            update_ui(window, msg)
            speak(msg)

        elif "who is" in command:
            person = command.replace("who is", "").strip()
            try:
                info = wikipedia.summary(person, 1)
                update_ui(window, info)
                speak(info)
            except:
                speak("Couldn't find information")

        elif contains(command, "phone number"):
            found = False
            for name in phone_numbers:
                if name in command:
                    msg = f"{name} phone number is {phone_numbers[name]}"
                    update_ui(window, msg)
                    speak(msg)
                    found = True
            if not found:
                speak("Contact not found")

        elif contains(command, "account number"):
            found = False
            for bank in bank_account_numbers:
                if bank in command:
                    msg = f"{bank} account number is {bank_account_numbers[bank]}"
                    update_ui(window, msg)
                    speak(msg)
                    found = True
            if not found:
                speak("Account not found")

        elif contains(command, "joke", "funny"):
            joke = pyjokes.get_joke()
            update_ui(window, joke)
            speak(joke)

        elif contains(command, "qr", "code"):
            data = command.replace("generate", "").replace("qr", "").replace("code", "").strip()
            if data:
                qr = pyqrcode.create(data)
                qr.png('qrcode.png', scale=8)
                msg = "QR code generated"
                update_ui(window, msg)
                speak(msg)
            else:
                speak("What should I encode?")

        elif contains(command, "news"):
            fetch_news(window)

        else:
            msg = "Command not recognized"
            update_ui(window, msg)
            speak(msg)

    except Exception as e:
        update_ui(window, f"Error: {e}")
        speak("Something went wrong")

# ---------------- NEWS ----------------
def fetch_news(window, num_articles=3):
    try:
        headlines = newsapi.get_top_headlines(language='en', country='us')
        articles = headlines.get('articles', [])[:num_articles]

        if not articles:
            speak("No news available")
            return

        for article in articles:
            title = article['title']
            update_ui(window, title)
            speak(title)

    except Exception as e:
        update_ui(window, f"News error: {e}")
        speak("Failed to fetch news")

# ---------------- THREAD ----------------
def listen(window):
    recognizer = sr.Recognizer()

    try:
        with sr.Microphone() as source:
            update_ui(window, "Listening...")
            recognizer.adjust_for_ambient_noise(source)

            audio = recognizer.listen(source, timeout=5)
            text = recognizer.recognize_google(audio).lower()

            update_ui(window, f"You said: {text}")
            execute_command(text, window)

    except sr.WaitTimeoutError:
        update_ui(window, "No speech detected")
    except sr.UnknownValueError:
        update_ui(window, "Could not understand")
    except Exception as e:
        update_ui(window, f"Error: {e}")

# ---------------- MAIN ----------------
def main():
    layout = [
        [sg.Text('Voice Assistant')],
        [sg.Output(size=(70, 12), key='-OUTPUT-')],
        [sg.Button('Start'), sg.Button('Exit')]
    ]

    window = sg.Window('Voice Assistant', layout)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break

        elif event == 'Start':
            threading.Thread(target=listen, args=(window,), daemon=True).start()

        elif event == '-UPDATE-':
            window['-OUTPUT-'].print(values['-UPDATE-'])

    window.close()

if __name__ == "__main__":
    main()
