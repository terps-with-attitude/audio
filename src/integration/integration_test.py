import pyaudio
import webrtcvad
import wave
import numpy as np
import adaptfilt as adf
from scipy.io.wavfile import write
import speech_recognition as sr
from os import path

#CONSTANTS
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 32000
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "voice.wav"
FRAME_DURATION = 30  # ms


#INITIALIZATION
audio = pyaudio.PyAudio()
vad = webrtcvad.Vad(3)

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,
                frames_per_buffer=CHUNK)
print("recording...")

frames = [""]*160000

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("finished recording")
print(len(frames))

# cleanup stream
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()


music = wave.open("music.wav", "r")
voice = wave.open("voice.wav", "r")


music.readframes(10000000)

music_frames = music.readframes(80000)
voice_frames = voice.readframes(160000)

u = np.fromstring(music_frames, np.int16)
u = np.float64(u)


v = np.fromstring(voice_frames, np.int16)
v = np.float64(v)
v = np.pad(v, (0, 160000 - len(v)%160000), mode = 'constant')
#v = ''.join(frames)
#v = np.fromstring(v, np.int16)
#v = np.float64(v)

d = u+v


# Apply adaptive filter
M = 100  # Number of filter taps in adaptive filter
step = .0001  # Step size
y, e, w = adf.nlms(u, d, M, step, returnCoeffs=True)

scaled_voice = np.int16(e/np.max(np.abs(e)) * 32767)

voice_len = len(scaled_voice)

write('test.wav', 32000, scaled_voice)

# scaled_voice_file = wave.open("test.wav", "r")

# scaled_voice = scaled_voice_file.readframes(320000)

# print(len(scaled_voice))
# print(RATE * FRAME_DURATION / 1000)

# speech_ratio = 0
# speech_total = 0

# samples =  int(RATE*RECORD_SECONDS/(RATE * FRAME_DURATION / 1000))

# for i in range(0, samples):
# 	sample = b''.join(scaled_voice[((2*RATE * FRAME_DURATION / 1000))*i : ((2*RATE * FRAME_DURATION / 1000))*(i+1)])
# 	print(len(sample))
# 	speech_exists = vad.is_speech(sample, RATE)
# 	speech_total = speech_total + speech_exists
# 	print('Contains speech: %s' % (vad.is_speech(sample, RATE)))

# speech_ratio = speech_total/float(samples)

print("Sending the file over to google for speech recognition...")

AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "test.wav")

r = sr.Recognizer()
with sr.AudioFile(AUDIO_FILE) as source:
    audio = r.record(source)

try:
    print("Google Speech Recognition thinks you said " + r.recognize_google(audio))
except sr.UnknownValueError:
    print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
    print("Could not request results from Google Speech Recognition service; {0}".format(e))