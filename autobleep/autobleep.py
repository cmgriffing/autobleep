import json
import logging
import subprocess
import sys

from pathlib import Path

import whisper_timestamped as whisper

# set a simple logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


default_swear_words = [
    "fuck",
    "bitch",
    "shit",
    "damn",
    "ass"
    # Companies I don't want to promote?
]

def load_swear_words(path : str):
    try:
        with open(path, "r") as fp:
            swear_words = json.load(fp)

        swear_words = swear_words["words"]

    except Exception:
        logger.error("ERROR: Make sure your JSON file is correctly formatted.")
        sys.exit()

    return swear_words


class AutoBleep:
    def __init__(
        self,
        input,
        swear_words=None,
        output="./output/output.mka",
        language="en",
    ):

        if swear_words is None:
            swear_words = default_swear_words
        else:
            swear_words = load_swear_words(swear_words)


        audio = whisper.load_audio(input)

        model = whisper.load_model("tiny", device="cpu")

        result = whisper.transcribe(model, audio, language=language)

        base_filters = []
        bleep_filters = []

        previous_filter_end = 0

        for segment in result["segments"]:
            for word in segment["words"]:
                word_text = word["text"].lower()
                for swear_word in swear_words:
                    if swear_word in word_text:
                        start = word["start"]
                        end = word["end"]

                        base_filters.append(
                            f"volume=enable='between(t,{start},{end})':volume=0"
                        )
                        bleep_filters.append(
                            f"volume=enable='between(t,{previous_filter_end},{start})':volume=0"
                        )
                        previous_filter_end = end

        # Arbitrary value for a year in seconds
        length = 365 * 24 * 60 * 60

        bleep_filters.append(
            f"volume=enable='between(t,{previous_filter_end},{length})':volume=0"
        )

        Path(output).parent.mkdir(parents=True, exist_ok=True)

        ffmpeg_command = f"ffmpeg -hide_banner -i {input} -f lavfi -i \"sine=frequency=1000\" -filter_complex \"[0:a]volume=1,{','.join(base_filters)}[0x];[1:a]volume=1,{','.join(bleep_filters)}[1x];[0x][1x]amix=inputs=2:duration=first\" -c:a aac -q:a 4 -y {output}"

        print("\n ffmpeg command", ffmpeg_command, "\n \n")

        subprocess.run(ffmpeg_command, shell=True)
