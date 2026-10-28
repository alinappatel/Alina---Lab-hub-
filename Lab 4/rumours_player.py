
import subprocess
import time

SONGS = {
    "SONGBIRD": "Songbird",
    "NEVER_GOING_BACK_AGAIN": "Never Going Back Again",
    "SILVER_SPRINGS": "Silver Springs",
}

positions = {song: 0.0 for song in SONGS}
active = None
loaded = None
held = []


def music(script):
    result = subprocess.run(
        ["osascript", "-e", f'tell application "Music"\n{script}\nend tell'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def pause():
    global active

    if active is None:
        return

    try:
        music("pause")
        positions[active] = float(music("player position"))
        print(f"PAUSED: {SONGS[active]} at {positions[active]:.1f}s")
    except Exception as e:
        print("Pause error:", e)

    active = None


def play(song):
    global active, loaded

    if active == song:
        return

    pause()

    try:
        if loaded == song:
            music("play")
        else:
            name = SONGS[song]

            music(
                f'set matches to (every track of library playlist 1 '
                f'whose name is "{name}" and artist is "Fleetwood Mac")\n'
                'if (count of matches) is 0 then '
                'error "Song not found"\n'
                'play (item 1 of matches)'
            )

            loaded = song
            time.sleep(0.3)
            music(f"set player position to {positions[song]}")

        active = song
        print(f"PLAYING: {SONGS[song]}")

    except Exception as e:
        print("Playback error:", e)


def main():
    print("Connecting to Raspberry Pi...", flush=True)

    connection = subprocess.Popen(
        [
            "ssh", "-T", "pi@10.56.130.48",
            "cd '/home/pi/Alina---Lab-hub-/Lab 4' && "
            "exec .venv/bin/python -u rumours_touch.py"
        ],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    try:
        for line in connection.stdout:
            parts = line.strip().split(maxsplit=1)

            if len(parts) != 2:
                if line.strip() == "READY":
                    print("RUMOURS READY! Touch the artwork.")
                continue

            action, song = parts

            if song not in SONGS:
                continue

            if action == "DOWN":
                if song in held:
                    held.remove(song)
                held.append(song)
                play(song)

            elif action == "UP":
                if song in held:
                    held.remove(song)

                if active == song:
                    pause()

                    if held:
                        play(held[-1])

    except KeyboardInterrupt:
        print("\nStopping controller.")

    finally:
        pause()
        connection.terminate()
        try:
            connection.wait(timeout=3)
        except subprocess.TimeoutExpired:
            connection.kill()
            connection.wait()


if __name__ == "__main__":
    main()

