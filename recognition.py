# sudo apt-get install portaudio19-dev
# pip install grpcio-tools PyAudio
# pip install pydub
import wave
import pyaudio
import grpc

import cloudapi.yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_service_pb2_grpc
# import cloudapi.yandex.cloud.ai.stt.v3.stt_service_pb2_grpc as stt_grpc

# FORMAT = pyaudio.paInt16
# CHANNELS = 1
RATE = 8000
CHUNK = 4096
RECORD_SECONDS = 30
# WAVE_OUTPUT_FILENAME = "audio.wav"
audio_file = "/home/test/speech.wav"
secret = "t1"


def read_audio_file(filename):
    wf = wave.open(filename, 'rb')
    p = pyaudio.PyAudio()

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    frames = []
    data = wf.readframes(CHUNK)
    while data:
        frames.append(data)
        if len(frames) == int(RATE / CHUNK * RECORD_SECONDS):
            yield frames
            frames = []
        data = wf.readframes(CHUNK)

    if frames:
        yield frames

    stream.stop_stream()
    stream.close()
    p.terminate()



# Пример использования функции

for audio_chunk in read_audio_file(audio_file):
    data = b''.join(audio_chunk)
    print(len(data))
    # Здесь вы можете сделать что-то с данными фрагмента, например, передать их дальше для обработки


cred = grpc.ssl_channel_credentials()
channel = grpc.secure_channel('stt.api.cloud.yandex.net:443', cred)
stub = stt_service_pb2_grpc.RecognizerStub(channel)

# Отправьте данные для распознавания.
it = stub.RecognizeStreaming(gen(), metadata=(
    ('authorization', f'Api-Key {secret}'),
))
