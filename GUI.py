import os
import threading
import tkinter as tk
from tkinter import scrolledtext
from tkinter import messagebox
import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI
import datetime

# Initialize the OpenAI client
client = OpenAI(api_key="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")

# Define the speech key and region for Azure Cognitive Services
speech_key = '04243e7483fd4106b20b6e0818ddc369'
service_region = 'eastus'

# Azure Speech Configuration
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_config.speech_recognition_language = "en-US"

# Initialize speech recognizer
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

class VoiceRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("区块链助手")
        self.master.wm_attributes("-topmost", 1)
        self.master.resizable(False, False)
        self.master.attributes('-alpha', 0.2)

        # place window in bottom right corner
        # self.master.update_idletasks()
        x = self.master.winfo_screenwidth() - 200 - 25
        y = self.master.winfo_screenheight() - 225 - 25
        self.master.geometry("200x150+{}+{}".format(x, y))

        

        self.isQuestion = False
        self.context = []
        self.done = False

        # Text box to show conversation
        self.text_area = scrolledtext.ScrolledText(master, wrap=tk.WORD)
        # place in 200x50
        self.text_area.place(x=0, y=0, width=200, height=125)
        # make font size small
        self.text_area.configure(font=("Times New Roman", 8))
        # set transparent
        self.text_area.configure(bg='black', fg='white')

        # Start button
        self.toggle_button = tk.Button(master, text="开始", command=self.toggle_listening, relief='flat', borderwidth=0)
        self.toggle_button.place(x=0, y=125, width=150, height=25)
        self.toggle_button.configure(bg='black', fg='white')

        #clear button
        self.clear_button = tk.Button(master, text="清除", command=self.clear_text, relief='flat', borderwidth=0)
        self.clear_button.place(x=150, y=125, width=50, height=25)
        self.clear_button.configure(bg='black', fg='red')
        # self.stop_button['state'] = 'disabled'

    def toggle_listening(self):
        if self.toggle_button['text'] == '开始':
            self.start_listening()
            self.toggle_button['text'] = '停止'
        else:
            self.stop_listening()
            self.toggle_button['text'] = '开始'

    def start_listening(self):
        threading.Thread(target=self.recognize_continuous_from_microphone).start()
        self.update_text(f"\n开始")
        # self.start_button['state'] = 'disabled'
        # self.stop_button['state'] = 'normal'

    def stop_listening(self):
        self.done = True
        speech_recognizer.stop_continuous_recognition()
        self.update_text(f"\n停止")
        # self.stop_button['state'] = 'disabled'
        # self.start_button['state'] = 'normal'

    def update_text(self, message):
        self.text_area.insert(tk.END, message + '\n')
        self.text_area.see(tk.END)

    def update_text_no_newline(self, message):
        self.text_area.insert(tk.END, message)
        self.text_area.see(tk.END)

    def clear_text(self):
        self.text_area.delete('1.0', tk.END)

    def recognize_continuous_from_microphone(self):
        self.done = False
        speech_recognizer.recognized.connect(self.recognizedPhrase)
        speech_recognizer.start_continuous_recognition()
        while not self.done:
            pass

    def recognizedPhrase(self, evt):
        sentence = evt.result.text
        self.update_text_no_newline(f".")

        if not self.isQuestion:
            self.isQuestion = "?" in sentence
        
        if self.isQuestion:
            self.update_text(f"\n\n{datetime.datetime.now()}: \n" + sentence + "\n" + "思维中")

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant answering questions. Try to make your answers concise."},
                    {"role": "user", "content": "Here's the context to the conversation: " + ", ".join(self.context)},
                    {"role": "user", "content": sentence}
                ]
            )

            self.text_area.delete('end-2l', tk.END)
            self.update_text("\n")

            if response.choices:
                message_content = response.choices[0].message.content
                self.update_text( message_content)
                self.context = [message_content]
            else:
                self.update_text("Error: No response. Try again.")

            self.isQuestion = False
            # self.update_text("\n\n问题停止\n\n")
        else:
            self.context.append(sentence)


if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceRecognitionApp(root)
    root.mainloop()
