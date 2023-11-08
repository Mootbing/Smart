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

    # Connect callbacks to the events fired by the speech recognizer
    def recognizedPhrase (evt): 
        nonlocal isQuestion, context

        sentence = evt.result.text
        if not isQuestion:
            isQuestion = "?" in sentence
        
        if isQuestion:
            # print('\n\n\nFinished Questionable: {}'.format(evt.result.text))
            # print("Ctx: {}".format(context))
            print("\n\n\n--Incoming--")

            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant answering a question like a student in class. Phrase it in a one-sentence answer from the perspective of a student answering the question just asked. Sound like a student and not a teacher. Make a one-sentence response that sounds semi-formal but appropriate to the classroom. Try to make it as short as possible. even better if you can answer in a few words. Cut the introduction like 'I would think..., Yeah, I agree..., etc'"},
                {"role": "user", "content": "Here's the context to the conversation " + ",".join(context)},
                {"role": "user", "content": sentence}
            ]
            )

            if response.choices:
                message_content = response.choices[0].message.content
                print("\n\n\nResponse:", message_content)
                context = [message_content]
            else:
                print("There was no response.")

            isQuestion = False

        else:
            context.append(sentence)
            # print('Context: {}'.format(evt.result.text))

    # def recongizingPhrase (evt): 
    #     nonlocal isQuestion

    #     print('Recognizing: {}'.format(evt.result.text))
    #     sentence = evt.result.text
    #     for word in sentence:
    #         word = word.lower()
    #         if word in questionWords:
    #             isQuestion = True
    #             print("question found")
    #             break


    # speech_recognizer.recognizing.connect(recongizingPhrase)
    speech_recognizer.recognized.connect(recognizedPhrase)
    # speech_recognizer.session_started.connect(lambda evt: print('SESSION STARTED: {}'.format(evt)))
    # speech_recognizer.session_stopped.connect(lambda evt: print('SESSION STOPPED {}'.format(evt)))
    # speech_recognizer.canceled.connect(lambda evt: print('CANCELED {}'.format(evt)))

    # Start continuous speech recognition
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
