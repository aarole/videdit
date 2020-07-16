# Snips and Clips
This smart video editor uses IBM's Watson to reduce the amount of time you spend editing your videos.
For the program to work, your videos must be recorded in a certain way. View the Directions for recording section at the end of this document for more information.

## Dependencies:
* Python3
* ffmpeg
* ibm-watson

## Setup
* Install Python dependencies with:
```
pip install -r requirements.txt
```
* Install ffmpeg from [here](https://ffmpeg.org/download.html)
  * Make a note of the location of the executable/binary

## Prep
* In your working directory, have the program executable and a directory named *files*
* Put your video(s) in the *files* directory.
  * Follow the naming convention:
      RANDOM_STRING1.mp4
      RANDOM_STRING2.mp4
      RANDOM_STRING3.mp4
      Where *RANDOM_STRING* is any word.
* Run the program executable

## Usage
* Set *Start word* to the take start indicator (the word in the video(s) that indicates the start of a take)
* Set *End word* to the take end indicator (the word in the video(s) that indicates the end of a good take)
* Set *Auth key* to your IBM Watson API key
* Set *Path to ffmpeg binary* to the location of the ffmpeg executable (the location that you provided in the Setup section)
* Click **Run**

## Directions for recording
* When recording, pick a start and end word (these should not be present in the video script).
* Start a take with the start word. 
  * If you mess up, say the start word again. 
* Once you are happy with your take, say the end word.

Your final version can consist of all takes split into multiple video files. 
The program will search for all the good takes (start word to end word) from all of your input videos and combine them to create a single output file.