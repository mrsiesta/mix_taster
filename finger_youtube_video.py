#!/usr/bin/env python

import argparse
import glob
import json
import requests
from pathlib import Path

from youtube_dl import YoutubeDL

DOWNLOAD_DIR = str(Path.cwd()) + '/youtube_downloads'
PROCESSED_DIR = str(Path.cwd()) + '/processed_mp3s'
AUD_TOKEN_PATH = str(Path.cwd()) + '/.aud.token'


def move_file(src_path, dest_path):
    dest = Path(dest_path)
    src = Path(src_path)
    dest.write_bytes(src.read_bytes())
    Path.unlink(src)


def download_youtube_audio(url_list, download_dir=DOWNLOAD_DIR):
    print(f"Checking youtube download directory exists:\n[{download_dir}]")
    Path(download_dir).mkdir(exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    for url in url_list:
        print(f"Attempting to download audio from '{url}'")
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    mp3_path_list = []

    for mp3 in glob.glob('*.mp3'):
        mp3_path = str(Path.cwd()) + '/' + mp3
        formatted_mp3 = mp3.replace(' ', '_')
        dest = download_dir + '/' + formatted_mp3
        move_file(mp3_path, dest)
        mp3_path_list.append(dest)

    return mp3_path_list


def finger_print_with_aud(file_path):
    """Query the AUD API and return the song data"""
    print(f"Attempting to fingerprint audio file:\n[{file_path}]")
    with open(AUD_TOKEN_PATH, 'r') as f_in:
        token = f_in.read().strip()
    data = {'api_token': token, 'skip': '8', 'every': '1'}
    breakpoint()
    result = requests.post('https://api.audd.io/', data=data, files={'file': open(file_path, 'rb')})
    return json.loads(result.text)


def main():
    print('OK')
    parser = argparse.ArgumentParser(
        description="Download youtube audio from URL"
    )
    parser.add_argument("-u", "--url", dest="url_list", nargs='*', type=str, help="Specify the youtube URLs to download")
    args = parser.parse_args()
    print(args.url_list)
    mp3_list = download_youtube_audio(args.url_list)

    results = {}
    for mp3 in mp3_list:
        finger_print_results = finger_print_with_aud(mp3)
        results[mp3] = finger_print_results
        file_name = mp3.split('/')[-1]
        processed_file = PROCESSED_DIR + '/' + file_name
        move_file(mp3, processed_file)
        output_text = processed_file.replace('.mp3', '.output')
        with open(output_text) as f_out:
            f_out.write(json.dumps(finger_print_results))
            print(f"Results for [{processed_file}]:\n{output_text}")


if __name__ == "__main__":
    main()
