
import time
import sys
import textwrap
import subprocess
import threading
import queue
from pathlib import Path
from datetime import datetime

import board
import digitalio
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
AUDIO_FILE = SCRIPT_DIR / "ideadrop_test.wav"

# PiTFT setup
dc = digitalio.DigitalInOut(board.D25)
display = st7789.ST7789(
    board.SPI(),
    cs=None,
    dc=dc,
    rst=None,
    baudrate=64000000,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output(value=True)

button_a = digitalio.DigitalInOut(board.D23)
button_a.switch_to_input(pull=digitalio.Pull.UP)

button_b = digitalio.DigitalInOut(board.D24)
button_b.switch_to_input(pull=digitalio.Pull.UP)

font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 22
)
small_font = ImageFont.truetype(
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12
)
last_displayed_title = None

# Display one interaction state
def show_screen(title, subtitle="", transcript=None,
                bg="#FFE1EC", fg="#A72D68", dot="#A72D68",
                scroll_offset=0):
    global last_displayed_title
    image = Image.new("RGB", (240, 135), bg)
    draw = ImageDraw.Draw(image)

    # On-screen status indicator
    draw.ellipse((216, 8, 230, 22), fill=dot)

    draw.text(
        (120, 27), title,
        font=font, fill=fg, anchor="mm"
    )

    if transcript is not None:
        lines = textwrap.wrap(transcript, width=28)
        visible_lines = lines[scroll_offset:scroll_offset + 4]

        for i, line in enumerate(visible_lines):
            draw.text(
                (120, 49 + i * 16), line,
                font=small_font, fill=fg, anchor="mm"
            )

        draw.text(
            (120, 122), "A: Save    B: Redo",
            font=small_font, fill=fg, anchor="mm"
        )
    else:
        draw.text(
            (120, 78), subtitle,
            font=small_font, fill=fg, anchor="mm"
        )

    display.image(image, 90)

    if title != last_displayed_title:
        print("Screen:", title)
        last_displayed_title = title


def show_home():
    show_screen(
        "IdeaDrop", "Press A to begin",
        bg="#FFE1EC", fg="#A72D68"
    )


def show_result(text, scroll_offset=0):
    if text:
        show_screen(
            "Save idea?", transcript=text,
            bg="#FFF0CC", fg="#916212",
            dot="#E0A12B",
            scroll_offset=scroll_offset
        )
    else:
        show_screen(
            "Try again",
            transcript="I couldn't catch that.",
            bg="#FFF0CC", fg="#916212"
        )


# Record and transcribe speech
def record_idea():
    show_screen(
        "Listening...", "Tell me your idea!",
        bg="#E1EFFF", fg="#285EA1",
        dot="#2AA66A"
    )

    print("\nRecording for 10 seconds. Speak now!")

    try:
        subprocess.run([
            "arecord", "-q", "-d", "10",
            "-f", "S16_LE",
            "-c", "1",
            "-r", "16000",
            str(AUDIO_FILE)
        ], check=True)

        show_screen(
            "Thinking...", "Transcribing speech",
            bg="#EAE2FF", fg="#6442A5",
            dot="#E0A12B"
        )

        print("Transcribing...")

        result = subprocess.run([
            sys.executable,
            str(SCRIPT_DIR / "transcribe.py"),
            str(AUDIO_FILE),
            "--model", "tiny.en"
        ], check=True, capture_output=True, text=True)

        print(result.stdout)

        lines = [
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        ]

        transcript = lines[0] if lines else ""

        # Empty transcriptions start with model statistics
        if transcript.startswith("model "):
            transcript = ""

        print("Captured idea:", transcript)
        show_result(transcript)
        return transcript

    except subprocess.CalledProcessError as error:
        print("Recording/transcription error:", error)
        show_result("")
        return ""

def save_idea(text):
    if not text.strip():
        print("Nothing to save.")
        return

    save_file = SCRIPT_DIR / "saved_ideas.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(save_file, "a", encoding="utf-8") as file:
        file.write(f"[{timestamp}] {text}\n")

    print("Idea saved to:", save_file)

    show_screen(
        "Idea saved!",
        "Press A to go home",
        bg="#DEF4E6",
        fg="#23764D",
        dot="#23764D"
    )

# Wizard-of-Oz controller
commands = queue.Queue()

def wizard_controller():
    while True:
        try:
            command = input().strip()
            commands.put(command)
        except EOFError:
            break

threading.Thread(
    target=wizard_controller, daemon=True
).start()

print("\nIDEADROP WIZARD CONTROLLER")
print("s = Start recording")
print("a = Save / Home")
print("r = Redo")
print("h = Home")
print("t Your corrected words = Correct transcript")
print("q = Quit\n")

state = "home"
transcript = ""
last_a = True
last_b = True

scroll_offset = 0
last_scroll = time.monotonic()
scroll_text = None

show_home()

try:
    while True:
        a = button_a.value
        b = button_b.value

        a_pressed = not a and last_a
        b_pressed = not b and last_b

        try:
            command = commands.get_nowait()
        except queue.Empty:
            command = ""

        if command.lower() == "q":
            break

        elif command.lower().startswith("t ") and state == "result":
            transcript = command[2:].strip()
            show_result(transcript)
            print("Wizard corrected transcript:", transcript)

        elif state == "result" and (
            command.lower() == "a" or a_pressed
        ):
            if transcript.strip():
                save_idea(transcript)
                state = "saved"
            else:
                print("No transcript to save. Please redo.")

        elif state == "saved" and (
            command.lower() in ("a", "h") or a_pressed
        ):
            state = "home"
            show_home()

        elif command.lower() == "h":
            state = "home"
            show_home()

        elif state == "result" and (
            command.lower() == "r" or b_pressed
        ):
            transcript = record_idea()
            state = "result"

        elif state == "home" and (
            command.lower() == "s" or a_pressed
        ):
            transcript = record_idea()
            state = "result"

        # Automatically scroll long transcriptions
        if state == "result" and transcript:
            if scroll_text != transcript:
                scroll_text = transcript
                scroll_offset = 0
                last_scroll = time.monotonic()

            lines = textwrap.wrap(transcript, width=28)

            if len(lines) > 4:
                if time.monotonic() - last_scroll >= 2.5:
                    scroll_offset = (
                        scroll_offset + 1
                    ) % (len(lines) - 3)

                    show_result(transcript, scroll_offset)
                    last_scroll = time.monotonic()

        elif state != "result":
            scroll_text = None
            
        last_a = a
        last_b = b
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopping IdeaDrop.")

finally:
    button_a.deinit()
    button_b.deinit()
    backlight.deinit()
    dc.deinit()