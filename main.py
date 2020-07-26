import os
import time
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

decoder = json.JSONDecoder()


def get_history_file():
    path = os.path.join(os.path.expanduser('~'), r'AppData\Local\Netease\CloudMusic\webdata\file')
    if os.path.exists(path):
        return path
    else:
        print('cloudmusic data folder not found')
        exit(1)


def get_playing(path):
    track_info = dict()
    with open(path, encoding='utf-8') as f:
        read_string = f.read(3200)
        for _ in range(4):
            try:
                read_string += f.read(500)
                decoded_json = decoder.raw_decode(read_string[1:])
                track_info.update(decoded_json[0])
                break
            except json.JSONDecodeError:
                pass

    if not track_info:
        return None

    track_name = track_info['track']['name']
    artist_list = [i['name'] for i in track_info['track']['artists']]

    return track_name, artist_list


class LoggingEventHandler(FileSystemEventHandler):
    def __init__(self):
        self.file_size = 0

    def on_modified(self, event):
        super(LoggingEventHandler, self).on_modified(event)
        path = event.src_path

        if path.endswith(r'webdata\file\history'):
            current_size = os.path.getsize(path)
            if current_size != self.file_size:
                self.file_size = current_size
                for _ in range(5):
                    try:
                        song, artists = get_playing(path)
                        with open('playing.txt', 'w', encoding='utf-8') as f:
                            playing = f'{song} - {" / ".join(artists)}'
                            print(playing)
                            f.write(playing)
                        break
                    except PermissionError:
                        time.sleep(1)


def main():
    path = get_history_file()
    event_handler = LoggingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
