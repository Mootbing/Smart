import os
import azure.cognitiveservices.speech as speechsdk

from openai import OpenAI
client = OpenAI(api_key="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")

questionWords = ["where", "who", "what", "how", "when", "do"]

def recognize_continuous_from_microphone():
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_key = '04243e7483fd4106b20b6e0818ddc369'
    service_region = 'eastus'
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    done = False

    def stop_cb(evt):
        """callback that stops continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        speech_recognizer.stop_continuous_recognition()
        nonlocal done
        done = True

    isQuestion = False
    context = []
    
    def recognizedPhrase (evt): 
        nonlocal isQuestion, context

        sentence = evt.result.text
        if not isQuestion:
            isQuestion = "?" in sentence
        
        if isQuestion:
            print("\n\n\nThinking...")

            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering a question like a student in class. Phrase it in a one-sentence answer from the perspective of a student answering the question just asked. Sounds semi-formal and appropriate. Try to make it as short as possible that covers key points. Cut the introduction like 'I would think..., Yeah, I agree..., etc' and a lot of filler words."},
                {"role": "user", "content": "Here's the context to the conversation " + ",".join(context)},
                {"role": "user", "content": sentence}
            ]
            )

            if response.choices:
                message_content = response.choices[0].message.content
                print("\n\n", message_content)
                context = [message_content]
            else:
                print("Error: No response. Try again.")

            isQuestion = False

        else:
            context.append(sentence)

    speech_recognizer.recognized.connect(recognizedPhrase)

    speech_recognizer.start_continuous_recognition()
    while not done:
        command = input("Type 'stop' to exit: ")
        if command == 'stop':
            speech_recognizer.stop_continuous_recognition()
            done = True

    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Wait for completion
    speech_recognizer.session_started.disconnect()
    speech_recognizer.session_stopped.disconnect()
    speech_recognizer.canceled.disconnect()

recognize_continuous_from_microphone()
