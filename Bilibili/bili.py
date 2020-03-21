# down ffmpeg first [https://www.ffmpeg.org/]

import shutil
from pathlib import Path
import json
import os
import concurrent.futures
import time

def go(path):
    home_dir = Path(path)
    # print(list(home_dir.iterdir()))
    video_dirs = home_dir.iterdir()

    title, files = None, []
    for i, video_dir in enumerate(video_dirs):
        if not video_dir.is_dir():
            continue

        with open(str(video_dir / 'entry.json'), 'r', encoding='utf8') as f:
            p_info = json.loads(f.read())
        p_name = p_info['page_data']['part']

        if not title:
            title = p_info['title']

        try:
            audio = list(video_dir.rglob('audio.m4s'))[0]
            video = list(video_dir.rglob('video.m4s'))[0]
            audio_path = home_dir / (p_name + '.mp3')
            video_path = home_dir / (p_name + '.mp4')
            audio.rename(audio_path)
            video.rename(video_path)
            print(audio, video)
            files.append([video_path, audio_path])
        except IndexError:
            pass

        # if not list(video_dir.rglob('*.m4s')):
        #     shutil.rmtree(video_dir)

    combine_audio_video(home_dir, files, title)


def combine_audio_video(home_dir: Path, files, title):
    Path(home_dir / title).mkdir()

    c = 'ffmpeg -i "{video}" -i "{audio}" -c:v copy -c:a aac -strict experimental "{mp4_name}"'
    commands = [c.format(video=str(file[0]), audio=str(file[1]), mp4_name=str(home_dir.joinpath(title, file[0].name))) for file in files]
    print(commands)

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(execute_ffmpeg, command) for command in commands]
        for future in concurrent.futures.as_completed(futures):
            if not future.exception():
                print('ok')

def execute_ffmpeg(command):
    t1 = time.time()
    os.system(command)
    print('TIME USE:', time.time() - t1)


# videos = home_dir.rglob('*.m4s')
# print(list(videos))


if __name__ == '__main__':
    go(r'D:\Resources\84375914')