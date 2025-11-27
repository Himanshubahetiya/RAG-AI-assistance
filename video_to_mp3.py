import os 
import subprocess

files = os.listdir('videos')
# list the all videos file by spliting it then convert the video files into mp3

for file in files:
    tutotial_number = file.split("[")[0].split("#")[1]
    file_name = file.split("-")[1]
    # print(tutotial_number,file_name)
    # subprocess.run(["ffmpeg", "-i", f"videos/{file}",f"audios/{tutotial_number}_{file_name}.mp3"])

    input_path = f"videos/{file}"
    output_path = f"audios/{tutotial_number}_{file_name}.mp3"

    subprocess.run([
        "ffmpeg",
        "-i", input_path,        
        "-vn",            
        output_path
    ])



