#!/usr/bin/env python3

# Made By:
# Aditya Arole
# Resul Ucar
# Zixiao Li

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from os.path import join, dirname
from tkinter import StringVar, Tk, ttk, HORIZONTAL
import ffmpeg
import subprocess
import os
import time
import threading
import glob
import math
import multiprocessing


class Editor:
	def __init__(self, root):
		self.start_val = StringVar(root, value='')
		self.end_val = StringVar(root, value='')
		self.stat_val = StringVar(root, value='')
		self.auth_val = StringVar(root, value='')
		self.path_val = StringVar(root, value='')
		
		root.title('Smart Video Editor')
		root.geometry('508x315')
		root.resizable(width=False, height=False)

		style = ttk.Style()
		style.configure('TButton', font='Arial 12', padding=10)

		style.configure('TEntry', font='Arial 15', padding=10)

		self.sl = ttk.Label(root, text="Start word:")
		self.sl.grid(row=0,column=0,columnspan=2)

		self.start = ttk.Entry(root,textvariable=self.start_val,width=59,state='normal')
		self.start.grid(row=0,column=2,columnspan=2)

		self.el = ttk.Label(root, text="End word:")
		self.el.grid(row=2,column=0,columnspan=2)

		self.end = ttk.Entry(root,textvariable=self.end_val,width=59,state='normal')
		self.end.grid(row=2,column=2, columnspan=2)

		self.aul = ttk.Label(root, text="Auth key:")
		self.aul.grid(row=4,column=0,columnspan=2)

		self.auth_txt = ttk.Entry(root,textvariable=self.auth_val,width=59,state='normal')
		self.auth_txt.grid(row=4,column=2, columnspan=2)

		self.pl = ttk.Label(root, text="Complete path to\n  ffmpeg binary:")
		self.pl.grid(row=6,column=0,columnspan=2)

		self.path_txt = ttk.Entry(root,textvariable=self.path_val,width=59,state='normal')
		self.path_txt.grid(row=6,column=2, columnspan=2)
		
		self.run_btn = ttk.Button(root, text='Run', command=lambda:self.run()).grid(row=8,column=1,columnspan=2)

		self.stl = ttk.Label(root, text="Status:")
		self.stl.grid(row=10,column=0,columnspan=2)

		self.stat = ttk.Entry(root,textvariable=self.stat_val,width=59,state='readonly')
		self.stat.grid(row=10,column=2, columnspan=2)
		
		self.progress = ttk.Progressbar(root, orient=HORIZONTAL, length = 315, mode = 'determinate') 
		self.progress.grid(row=12, column=1, columnspan=4)

		self.update_txt(self.stat, "Suspended")

	
	def update_txt(self, box, text):
		box['state'] = 'normal'
		box.delete(0, 'end')
		box.insert(0, text)
		box['state'] = 'readonly'

	
	def run(self):
		self.base_dir = os.getcwd()
		self.start_time = time.time()
		self.vid_count = 0
		self.progress['value'] = 0

		thread1 = threading.Thread(target=self.update_txt, args=(self.stat,"Running"))
		thread2 = threading.Thread(target=self.edit, args=())
		thread3 = threading.Thread(target=self.update_progress, args=())

		thread1.start()
		thread3.start()
		thread2.start()
	
	
	def update_progress(self):
		while self.progress['value'] != 85:
			self.progress['value'] += 1
			time.sleep(1)
	

	def clean_up(self):
		print('Cleaning up...')
		
		self.update_txt(self.stat, "Cleaning up")

		try:
			self.audio_file.close()
			self.init_video_list.close()
			self.text_file.close()
		except:
			pass

		file_list = list()
		file_list += glob.glob("p*.mp4")
		file_list += glob.glob("*.txt")
		file_list += glob.glob("*.mp3")
		file_list.append('combined.mp4')

		for f in file_list:
			try:
				os.remove(f)
			except FileNotFoundError:
				pass
		time.sleep(5)
		os.chdir(self.base_dir)

		self.complete_execution()

		
	def complete_execution(self):
		print('\nProgram complete!')
		end_time  = time.time()
		time_taken = math.ceil(end_time-self.start_time)
		print(f'Execution time: {time_taken} seconds.')

		self.progress['value'] = 100
		self.update_txt(self.stat, f"Complete. Execution time: {time_taken} seconds")
		
	
	def edit(self):
		start_word = str(self.start.get()).strip()
		end_word = str(self.end.get()).strip()
		ffmpeg_path = str(self.path_txt.get()).strip()

		os.chdir("files")

		videos = os.listdir()

		self.init_video_list = open(f'videos.txt','w')
		for video in videos:
			self.init_video_list.write(f"file '{video}'\n")
			self.vid_count += 1
		self.init_video_list.close()
 
		subprocess.call(f'{ffmpeg_path}/ffmpeg -f concat -safe 0 -i videos.txt -c copy combined.mp4',shell=True)

		video_file_path = 'combined.mp4'

		subprocess.call(f'{ffmpeg_path}/ffmpeg -i {video_file_path} -f mp3 -ab 192000 -vn audio_main.mp3',shell=True)

		self.audio_file = open('audio_main.mp3','rb')

		authenticator = IAMAuthenticator(str(self.auth_txt.get()).strip())

		speech_to_text = SpeechToTextV1(authenticator=authenticator)

		speech_to_text.set_service_url('https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/f7f5d78f-1da8-4a82-904c-e520bb249e9d')

		try:
			response = speech_to_text.recognize(audio=self.audio_file,content_type='audio/mp3',keywords_threshold=0.8,keywords=[start_word,end_word]).get_result()
		except:
			self.clean_up()
		self.audio_file.close()

		timestamps_all = []

		for item in response['results']:
			if 'keywords_result' in item.keys():
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
		self.text_file = open(f'files.txt','w')
		for item2 in good_timestamps_final:
			dur = item2[1]- item2[0]
			subprocess.call(f'{ffmpeg_path}/ffmpeg -ss {str(item2[0])} -t {str(dur)} -i {video_file_path} p{i}.mp4', shell=True)
			self.text_file.write(f"file 'p{i}.mp4'\n")
			i+=1
		self.text_file.close()

		subprocess.call(f'{ffmpeg_path}/ffmpeg -f concat -safe 0 -i files.txt -c copy output.mp4',shell=True)
		print('Output created...')
		self.update_txt(self.stat, "Output created")
		time.sleep(2)

		self.clean_up()


def main():
	root = Tk()
	root.wm_iconbitmap("logo.ico")

	_ = Editor(root)

	root.mainloop()


if __name__ == "__main__":
	main()