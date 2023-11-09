from openai import OpenAI
client = OpenAI(api_key="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")

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Who won the world series in 2020?"},
    {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
    {"role": "user", "content": "Where was it played?"}
  ]
)

if response.choices:
    message_content = response.choices[0].message.content
    print("The response from the assistant is:", message_content)
else:
    print("There was no response.")