import os
from pathlib import Path
import asyncio
from dotenv import load_dotenv
from yandex_music import Client, TrackShort

load_dotenv()
jukebox = Client.from_credentials(os.getenv('LOGIN'), os.getenv('PASS'))
Path('./YMcache/').mkdir(parents=True, exist_ok=True)


def search(rawtext: tuple):
    if rawtext[0][0] == '-':
        arg = rawtext[0][1::]
        text = ' '.join(rawtext[1::])
    else:
        arg = None
        text = ' '.join(rawtext)

    if arg is None:
        arg = 'all'
        text = text.split('/')
        if len(text) > 1:
            for word in text:
                if word == 'music.yandex.ru':
                    arg = 'link'
                    break
        text = '/'.join(text)

    try:
        if arg == 'link':
            int(text.split('/')[-1])
            parsed_id = text.split('/')[-1]
            try:
                int(text.split('/')[-3])
                parsed_id += ':' + text.split('/')[-3]

                tracks = jukebox.tracks(track_ids=[parsed_id])
            except Exception:
                setlist = jukebox.albums_with_tracks(parsed_id)
                tracks = []
                for volume in setlist.volumes:
                    tracks += volume

        elif arg == 'loves':
            tracks = jukebox.users_likes_tracks()

        elif arg == 'likes':
            tracks = jukebox.tracks(track_ids=['609676:14599232'])

        else:
            query = jukebox.search(text=text, type_=arg)
            if arg == 'track':
                setlist = query.tracks.results[0]
            elif arg == 'album':
                setlist = query.albums.results[0]
            elif arg == 'artist':
                setlist = query.artists.results[0]
            elif arg == 'playlist':
                setlist = query.playlists.results[0]
            else:
                setlist = query.best.result
                arg = query.best.type

            if arg == 'track':
                tracks = [setlist]
            elif arg == 'album':
                setlist = setlist.with_tracks()
                tracks = []
                for volume in setlist.volumes:
                    tracks += volume
            elif arg == 'artist':
                tracks = setlist.get_tracks()
            elif arg == 'playlist':
                tracks = setlist.fetch_tracks()

        return tracks

    except Exception as woopsie:
        return f"I don't get it ||{woopsie}||"
