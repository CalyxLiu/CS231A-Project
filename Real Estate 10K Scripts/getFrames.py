import os
import cv2

from pytube import YouTube
from pytube.exceptions import PytubeError

# typing imports
from collections.abc import Iterator
from typing import Literal, TextIO
from numpy import ndarray

def framesGenerator(video_path: str) -> Iterator[ndarray]:
    '''
    Turns a saved video into a sequence of frame images
    '''
    # read the video
    videoCapture = cv2.VideoCapture(video_path)

    success, image = videoCapture.read()
    while success:
        yield image

        # set up for next loop
        success, image = videoCapture.read()


def extractVideoFramesWithMetadata(video_path: str, frames_path: str, metadata_file: TextIO, dataset_file: TextIO) -> None:
    '''
    Requires that the URL line of the dataset file has already been read.

    1. Saves the metadata lines for the successfully read frames to the metadata file
    2. Saves the extracted frames as images to the frames path
    '''

    # save off each frame
    for metadata_line, image in zip(dataset_file.readlines(), framesGenerator(video_path)):
        # save metadata line to file for successful image read
        metadata_file.write(metadata_line)
        # timestamp is first item in space-delimited line
        timestamp = metadata_line.split(' ')[0]

        # save image
        frame_filename = os.path.join(video_path, f'{timestamp}.png')
        cv2.imwrite(frame_filename, image)

        if DEBUG:
            print(f'Saved frame {timestamp} from {video_path} to {frames_path}')

def extractFrames(video_path, metadata_path):
    cam = cv2.VideoCapture(video_path)
    ind = 0
    while(True):
        ret, frame = cam.read()
        if ret:
            name = f'{ind}.jpg'
            cv2.imwrite(name, frame)
            ind += 1
        else:
            break

    cam.release()

#frames/test/{name}/full_video.mpr/{name}
for dataset_filename in os.listdir("test"):
    dataFilename = dataset_filename.split(".")[0]
    video_directory = os.path.join("frames/test", dataFilename, "full_video.mp4")
    print(f"File: {dataset_filename} Path: {video_directory}")
 

    if(not os.path.exists(video_directory)):
        print("   No video folder")
        continue
    
    if(len(os.listdir(video_directory)) > 2):
        print("   Already extracted")
        continue

    video_name = os.listdir(video_directory)
    if(not video_name):
        print("   No video")
        continue

    video_path = os.path.join(video_directory, video_name[0])
    cam = cv2.VideoCapture(video_path)
    ind = 0
    with open(os.path.join("test", dataset_filename), 'r') as dataFile, open(os.path.join("frames/test", dataset_filename), 'w') as metadata:
        fps = cam.get(cv2.CAP_PROP_FPS)
        ind = 0.
        for line in dataFile:
            if("https" in line):
                continue
            info = line.split(" ")
            timestamp = int(info[0])
            print(f"   Timestamp: {timestamp}")
            time = 0
            while(time < timestamp):
                ret, frame = cam.read()
                if ret:
                    ind += 1.
                    time = (ind / fps) * 10**6
                    if(time >= timestamp):
                        print("      Writing")
                        name = f'{timestamp}.jpg'
                        if not cv2.imwrite(os.path.join(video_directory, name), frame):
                            print(f"         Error: {video_path}")
                        metadata.write(line)
                else:
                    break
    
    cam.release()
    

