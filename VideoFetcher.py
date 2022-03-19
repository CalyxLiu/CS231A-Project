import os
import cv2

from pytube import YouTube
from pytube.exceptions import PytubeError

# typing imports
from collections.abc import Iterator
from typing import Literal, TextIO
from numpy import ndarray

DEBUG = True

def safeCreatePath(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path)

def downloadVideo(url: str, path: str, filename: str = 'full_video.mp4') -> bool:
    '''
    Downloads a video from youtube and saves it under the given path and filename.
    Selects the highest resolution mp4 file available.
    '''

    # make sure we're saving to a valid place
    safeCreatePath(path)

    try:
        video_filename = os.path.join(path, filename)
        # download the highest resolution mp4 that youtube has for this video
        YouTube(url).streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(video_filename)

        if DEBUG:
            print(f'Downloaded a video (url: {url}) to {path}')

        return True
    except PytubeError as err:

        print(f'Pytube encountered an error when downloading {url}')

        if DEBUG:
            print(f'{err}')

        return False

def framesGenerator(video_path: str) -> Iterator[ndarray]:
    '''
    Turns a saved video into a sequence of frame images
    '''
    # read the video
    videoCapture = cv2.VideoCapture(video_path)
    fps = videoCapture.get(cv2.CAP_PROP_FPS)

    success, image = videoCapture.read()
    while success:
        print("Frame read")
        yield image

        # set up for next loop
        success, image = videoCapture.read()


def extractVideoFramesWithMetadata(video_path: str, frames_path: str, metadata_file: TextIO, dataset_file: TextIO) -> None:
    '''
    Requires that the URL line of the dataset file has already been read.

    1. Saves the metadata lines for the successfully read frames to the metadata file
    2. Saves the extracted frames as images to the frames path
    '''
    print("Extracting")

    # make sure the frames path exists
    safeCreatePath(frames_path)

    
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

def handleDatasetFile(category: Literal['train', 'test'], filename: str) -> None:
    '''
    1. Saves the video ID to the location file
    2. Downloads the youtube video from the url in the dataset file
    3. Creates the metadata files and extracts the video frames
    '''

    print("Handling file")

    # dataset filenames are <id>.txt
    video_id = filename.split('.')[0]

    # stores the locations of each video
    video_loc_path = os.path.join('frames', category, 'video_loc.txt')
    # stores the metadata for successfully downloaded frames
    video_metadata_path = os.path.join('frames', category, filename)
    # stores video frame pngs and the full_video.mp4
    video_content_path = os.path.join('frames', category, video_id)

    dataset_file_path = os.path.join(category, filename)

    # save the video location metadata
    with open(video_loc_path, 'a') as location_file:
        location_file.write(f'{video_id}\n')
    
    with open(dataset_file_path, 'r') as dataset_file, open(video_metadata_path, 'w') as metadata_file:
        
        # download and process video
        url = dataset_file.readline().strip()
        downloadVideo(url, video_content_path, 'full_video.mp4')
        '''    video_mp4_path = os.path.join(video_content_path, 'full_video.mp4')
            extractVideoFramesWithMetadata(
                video_path=video_mp4_path, 
                frames_path=video_content_path, 
                metadata_file=metadata_file, 
                dataset_file=dataset_file)'''

def processDatasetCategory(category: Literal['train', 'test']) -> None:
    '''
    Iterates over the files in the given dataset category and processes them.
    '''
    numFiles = len(os.listdir(category))
    currIndex = 1
    for dataset_filename in os.listdir(category):
        print(f"Processing file {currIndex} out of {numFiles}")
        dataset_file_path = os.path.join(category, dataset_filename)
        frame_file_path = os.path.join('frames', category, dataset_filename)

        if os.path.isfile(dataset_file_path) and not os.path.isfile(frame_file_path):
            handleDatasetFile(category, dataset_filename)

        currIndex += 1

def main():
#    processDatasetCategory('test')
    processDatasetCategory('train')

if __name__ == '__main__':
    # MUST BE RUN FROM THE SAME DIRECTORY AS THE TRAIN AND TEST DIRECTORIES
    main()



