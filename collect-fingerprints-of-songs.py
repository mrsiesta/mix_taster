#!/usr/bin/env python

import os
import sys
import libs
import libs.fingerprint as fingerprint

from termcolor import colored
from libs.reader_file import FileReader
from libs.db_sqlite import SqliteDatabase
from libs.config import get_config

if __name__ == '__main__':
  config = get_config()

  db = SqliteDatabase()
  path = "mp3/"

  # fingerprint all files in a directory

  for filename in os.listdir(path):
    if filename.endswith(".mp3"):
      reader = FileReader(path + filename)
      audio = reader.parse_audio()

      song = db.get_song_by_filehash(audio['file_hash'])
      song_id = db.add_song(filename, audio['file_hash'])

      msg = ' * {} {}: {}'.format(
        colored(f'id={song_id}', 'white', attrs=['dark']),
        colored(f'channels={len(audio["channels"])}', 'white', attrs=['dark']),
        colored(f'{filename}', 'white', attrs=['bold'])
      )
      print(msg)

      if song:
        hash_count = db.get_song_hashes_count(song_id)

        if hash_count > 0:
          msg = '   already exists (%d hashes), skip' % hash_count
          print(colored(msg, 'red'))

          continue

      print(colored('   new song, going to analyze..', 'green'))

      hashes = set()
      channel_amount = len(audio['channels'])

      for channeln, channel in enumerate(audio['channels']):
        msg = f'   fingerprinting channel {channeln+1}/{channel_amount}'
        print(colored(msg, attrs=['dark']))

        channel_hashes = fingerprint.fingerprint(channel, Fs=audio['Fs'], plots=config['fingerprint.show_plots'])
        channel_hashes = set(channel_hashes)

        msg = f'   finished channel {channeln+1}/{channel_amount}, got {len(channel_hashes)} hashes'
        print(colored(msg, attrs=['dark']))

        hashes |= channel_hashes

      msg = f'   finished fingerprinting, got {len(hashes)} unique hashes'

      values = []
      for hash, offset in hashes:
        values.append((song_id, hash, offset))

      msg = '   storing %d hashes in db' % len(values)
      print(colored(msg, 'green'))

      db.store_fingerprints(values)

  print('end')
