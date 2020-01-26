#!/usr/bin/python3

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
import ffmpeg
import subprocess
import os
import time

#file_name = str(input('Enter file names (CSV): '))

#videos = list(file_name.split(','))

start_time = time.time()

start_word = str(input('Enter start word: '))
end_word = str(input('Enter end word: '))

root_path = str(join(dirname(__file__),'./files'))

videos = os.listdir(root_path)
videos.reverse()

init_video_list = open(f'{root_path}/videos.txt','w')
for video in videos:
	init_video_list.write(f"file '{video}'\n")
init_video_list.close()

subprocess.call(f'ffmpeg -f concat -safe 0 -i {root_path}/videos.txt -c copy {root_path}/combined.mp4',shell=True)

video_file_path = str(join(dirname(__file__),'./files','combined.mp4'))

subprocess.call(f'ffmpeg -i {video_file_path} -f mp3 -ab 192000 -vn {root_path}/audio_main.mp3',shell=True)

audio_file = open(join(dirname(__file__),'./files','audio_main.mp3'),'rb')

authenticator = IAMAuthenticator('JKUGTvWM_J5SZI4sKXkfH52-VMR4H3io4eRvmZkqmhDO')

speech_to_text = SpeechToTextV1(authenticator=authenticator)

speech_to_text.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/f7f5d78f-1da8-4a82-904c-e520bb249e9d')

#audio_file = open(join(dirname(__file__),'./.','Voice_001_01.wav'),'rb')

response = speech_to_text.recognize(audio=audio_file,content_type='audio/mp3',keywords_threshold=0.8,keywords=[start_word,end_word]).get_result()

"""
#with open(join(dirname(__file__),'./.','Voice_001_01.wav'),'rb') as audio_file:
#	response = speech_to_text.recognize(audio=audio_file,content_type='audio/wav',keywords_threshold=0.8,keywords=['cactus','software']).get_result()
"""

timestamps_all = []

for item in response['results']:
	check = not item['keywords_result']
	word = item['keywords_result']
	if not check:
		for key in word:
			list_item = [str(key),float(word[key][0]['start_time']),float(word[key][0]['end_time'])]
			timestamps_all.append(list_item)

good_timestamps = []

for i in range(len(timestamps_all)):
	good_timestamps.append(0)

i = 0

for item1 in timestamps_all:
	if item1[0] == start_word:
		good_timestamps[i] = item1[2]
	elif item1[0] == end_word:
		i+=1
		good_timestamps[i] = item1[1]
		i+=1

good_timestamps = list(filter((0).__ne__, good_timestamps))

good_timestamps_final = []

j=0
while j <= (len(good_timestamps)-1):
	good_timestamps_final.append([good_timestamps[j],good_timestamps[j+1]])
	j += 2

print(good_timestamps_final)
i=1
text_file = open(f'{root_path}/files.txt','w')
for item2 in good_timestamps_final:
	dur = item2[1]- item2[0]
	subprocess.call(f'ffmpeg -ss {str(item2[0])} -t {str(dur)} -i {video_file_path} {root_path}/p{i}.mp4', shell=True)
	text_file.write(f"file 'p{i}.mp4'\n")
	i+=1
text_file.close()

subprocess.call(f'ffmpeg -f concat -safe 0 -i {root_path}/files.txt -c copy {root_path}/output.mp4',shell=True)
print('Finished...')

print('Cleaning up...')
subprocess.call(f'rm {root_path}/combined.mp4',shell=True)
subprocess.call(f'rm {root_path}/p*.mp4',shell=True)
subprocess.call(f'rm {root_path}/*.txt',shell=True)
subprocess.call(f'rm {root_path}/*.mp3',shell=True)
print('\nProgram complete!')
end_time  = time.time()
print(f'Execution time: {(end_time-start_time)} seconds.')
