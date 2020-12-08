import os
import glob
import eyed3

TITLE_FID          = b"TIT2"                                            # noqa
ARTIST_FID         = b"TPE1"                                            # noqa
ALBUM_FID          = b"TALB"                                            # noqa
TRACKNUM_FID       = b"TRCK"                                            # noqa
GENRE_FID          = b"TCON"                                            # noqa
YEAR_FID           = b"TDRC"                                            # noqa
ARTWORK_FID        = b"APIC"                                            # noqa

fields = [
    TITLE_FID,
    ARTIST_FID,
    ALBUM_FID,
    TRACKNUM_FID,
    GENRE_FID,
    YEAR_FID,
    ARTWORK_FID
]

start_directory = "/opt/storage/sd_card/damian/audiobooks"
# GENRE, ARTIST or ALBUM
start_level = "ALBUM"
file_pattern_recurse = "**/*.mp3"
file_pattern_no_recurse = "*.mp3"
dry_run = False

errors = []


def remove_non_required_tags(mp3_file):

    audio_file = eyed3.core.load(mp3_file)

    if dry_run:
        print(f"Audio file: {audio_file.path}")

    frames = []

    for frame_id in audio_file.tag.frame_set:
        if frame_id not in fields:
            frames.append(frame_id)

    for frame_id in frames:
        if dry_run:
            print(f"Removing frame: {frame_id}")

        try:
            if not dry_run:
                del audio_file.tag.frame_set[frame_id]
        except Exception:
            errors.append(f"Frame deletion error: {audio_file.path}")

    is_missing_tag = False

    # perform a sanity check
    if TITLE_FID not in audio_file.tag.frame_set:
        is_missing_tag = True
        errors.append(f"Missing title: {audio_file.path}")
    if ARTIST_FID not in audio_file.tag.frame_set:
        is_missing_tag = True
        errors.append(f"Missing artist: {audio_file.path}")
    if ALBUM_FID not in audio_file.tag.frame_set:
        is_missing_tag = True
        errors.append(f"Missing album: {audio_file.path}")
    if GENRE_FID not in audio_file.tag.frame_set:
        is_missing_tag = True
        errors.append(f"Missing genre: {audio_file.path}")
    if ARTWORK_FID not in audio_file.tag.frame_set:
        is_missing_tag = True
        errors.append(f"Missing artwork: {audio_file.path}")

    try:
        if not dry_run and not is_missing_tag:
            audio_file.tag.save()
    except Exception:
        errors.append(f"Tag save error: {audio_file.path}")


level_genre = []
if start_level == "GENRE":
    for genre in os.listdir(start_directory):
        if os.path.isdir(os.path.join(start_directory, genre)):
            level_genre.append(os.path.join(start_directory, genre))

if dry_run:
    print(f"level_genre: {level_genre}")

level_artist = []
if len(level_genre) > 0:
    if level_genre:
        for genre in level_genre:
            for artist in os.listdir(genre):
                if os.path.isdir(os.path.join(genre, artist)):
                    level_artist.append(os.path.join(genre, artist))
else:
    for artist in os.listdir(start_directory):
        if os.path.isdir(os.path.join(start_directory, artist)):
            level_artist.append(os.path.join(start_directory, artist))

if dry_run:
    print(f"level_artist: {level_artist}")

level_album = []
if len(level_artist) > 0:
    for artist in level_artist:
        for album in os.listdir(artist):
            if os.path.isdir(os.path.join(artist, album)):
                level_album.append(os.path.join(artist, album))
else:
    for album in os.listdir(start_directory):
        if os.path.isdir(os.path.join(start_directory, artist)):
            level_album.append(os.path.join(start_directory, artist))

if dry_run:
    print(f"level_album: {level_album}")

if len(level_album) > 0:
    for album in level_album:
        song_list = []

        song_list_recurse = glob.glob(os.path.join(album, file_pattern_recurse))
        if len(song_list_recurse) > 0:
            song_list.extend(song_list_recurse)

        song_list_no_recurse = glob.glob(os.path.join(album, file_pattern_no_recurse))
        if len(song_list_no_recurse) > 0:
            song_list.extend(song_list_no_recurse)

        # remove any duplicate songs
        song_list = list(dict.fromkeys(song_list))

        for song in song_list:
            if dry_run:
                print(song)

            remove_non_required_tags(song)

for error in errors:
    print(f">>> ERROR >>>: {error}")
