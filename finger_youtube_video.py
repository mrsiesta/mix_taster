import argparse
import glob
from pathlib import Path

from youtube_dl import YoutubeDL

DOWNLOAD_DIR = str(Path.resolve(__file__)) + '/youtube_downloads'


def move_file(src_path, dest_path):
    dest = Path(dest_path)
    src = Path(src_path)
    dest.write_bytes(src.read_bytes())
    Path.unlink(src_path)


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
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)

    mp3_list = glob.glob('*.mp3')
    for mp3 in mp3_list:
        mp3_path = str(Path.cwd()) + '/' + mp3
        formatted_mp3 = mp3.replace(' ', '_')
        dest = download_dir + '/' + formatted_mp3
        move_file(mp3_path, dest)


def main():
    parser = argparse.ArgumentParser(
        description="Download youtube audio from URL"
    )
    parser.add_argument("-u", "--url", dest="url_list", nargs='*', help="Specify the youtube URLs to download")
    args = parser.parse_args()
    download_youtube_audio(args.url_list)
