# pip install openai
# pip install pydub
# pip install moviepy
# pip install ffmpeg-python

import openai
import os
import json
# import pydub
# from pydub import AudioSegment

# program_directory = os.path.dirname(os.path.abspath(__file__))

# pydub.AudioSegment.ffmpeg = program_directory + "\\"

# print(program_directory)

# ogg_audio = AudioSegment.from_file(program_directory + "\\format.ogg", format="ogg")
# ogg_audio = AudioSegment.from_file( "C:\Users\kukiman\Documents\Python\tg_run_serv\audio.ogg", format="ogg")

# экспортируем в mp3
# mp3_audio = ogg_audio.export(program_path +"/audio.mp3", format="mp3")


openai.api_key = "test"


# audio_file = open(program_path +"/audio.mp3", "rb")
# audio_file = open("./audio/audio4.mp3", "rb")
# transcript = openai.Audio.translate("whisper-1", audio_file)

# print(transcript)
# text = transcript.to_dict()['text']

# print(text)

# # prompt = "Write poem about how cool readers of uproger website"



# import soundfile as sf

# input_file = 'input.ogg'
# output_file = 'output.mp3'

# data, samplerate = sf.read(input_file)
# sf.write(output_file, data, samplerate, format='MP3')




completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "test"},
    # {"role": "user", "content": "sing me a song in Russian!"}
    # {"role": "user", "content": text}
  ]
)

ansver = str( completion.choices[0].message )

decoded_s = ansver.encode().decode('unicode-escape')
print(decoded_s)



