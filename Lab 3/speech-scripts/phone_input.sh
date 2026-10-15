#!/bin/bash

# Ask for a phone number
espeak "Hi! Please tell me your ten digit phone number."

# Give the user a moment to prepare
sleep 1

# Prompt the user to respond
espeak "Go ahead."

# Record the spoken response for 8 seconds
arecord -q -d 8 -f S16_LE -c 1 -r 16000 phone_answer.wav

# Transcribe the recorded response
echo "Here's what I heard:"
python transcribe.py phone_answer.wav --model tiny.en
