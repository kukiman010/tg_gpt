from groq import Groq
# https://console.groq.com/keys

client = Groq(api_key="TOKEN_API")
messages = []
message ="кто был противником в войне 1812 года?"
# global messages

messages.append({"role": 'user', "content": message})
# if len(messages) > 6:
#     messages = messages[-6:]
response = client.chat.completions.create(model='llama3-70b-8192', messages=messages, temperature=0)
print( response.choices[0].message.content)



# import requests
# import json

# url = 'https://api.aimlapi.com/chat/completions'
# api_token = 'TOKEN_API'  # Замените на ваш API токен

# headers = {
#     'Content-Type': 'application/json',
#     'Accept': 'application/json',
#     'Authorization': f'Bearer {api_token}'  
# }

# data = {
#     #"model": "mistralai/Mistral-7B-Instruct-v0.2",
#     "model": "meta-llama/Meta-Llama-3-70B",
#     "messages": [
#         {
#             "role": "user",
#             "content": "кто был противником в войне 1812 года?"
#         }
#         # ,
#         # {
#         #     "role": "assistant",
#         #     "content": "The Los Angeles Dodgers won the World Series in 2020."
#         # },
#         # {
#         #     "role": "user",
#         #     "content": "Where was it played?"
#         # }
#     ],
#     "temperature": 1,
#     "top_p": 1,
#     "n": 1,
#     "stream": False,
#     "max_tokens": 250,
#     "presence_penalty": 0,
#     "frequency_penalty": 0
# }

# response = requests.post(url, headers=headers, data=json.dumps(data))

# if response.status_code == 200:
#     response_data = response.json()
#     print(json.dumps(response_data, indent=4))
# else:
#     print(f"Failed to get response: {response.status_code}")
#     print(response.text)