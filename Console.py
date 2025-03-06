import os
import azure.cognitiveservices.speech as speechsdk
from openai import OpenAI

# Move API keys to environment variables for security
client = OpenAI(
    api_key="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"
)  # Will use OPENAI_API_KEY environment variable

questionWords = ["where", "who", "what", "how", "when", "do"]

def recognize_continuous_from_microphone():
    # Configure speech service using environment variables
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv('AZURE_SPEECH_KEY', '04243e7483fd4106b20b6e0818ddc369'),
        region=os.getenv('AZURE_SPEECH_REGION', 'eastus')
    )
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
    
    def recognizedPhrase(evt): 
        nonlocal isQuestion, context

        sentence = evt.result.text
        if not isQuestion:
            isQuestion = "?" in sentence
        
        if isQuestion:
            print("\n\n\nThinking...")

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant answering a question like a student in class. Phrase it very concisely which represents the thought process of a student answering the question just asked. Sound appropriate. Make it as short as possible that covers key points. Use -> to connect thoughts which should be one or two words"},
                        {"role": "user", "content": f"Here's the context to the conversation: {', '.join(context)}"},
                        {"role": "user", "content": sentence}
                    ]
                )

                if response.choices:
                    message_content = response.choices[0].message.content
                    print("\n\n", "\n".join(message_content.split("->")))
                    context = [message_content]
                else:
                    print("Error: No response. Try again.")

            except Exception as e:
                print(f"Error occurred: {str(e)}")

            isQuestion = False
        else:
            context.append(sentence)

    # Set up event handlers
    speech_recognizer.recognized.connect(recognizedPhrase)
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start recognition
    speech_recognizer.start_continuous_recognition()
    
    try:
        while not done:
            command = input("Type 'stop' to exit: ")
            if command.lower() == 'stop':
                speech_recognizer.stop_continuous_recognition()
                done = True
    finally:
        # Cleanup
        speech_recognizer.recognized.disconnect_all()
        speech_recognizer.session_stopped.disconnect_all()
        speech_recognizer.canceled.disconnect_all()

if __name__ == "__main__":
    recognize_continuous_from_microphone()
