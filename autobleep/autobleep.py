import subprocess
import whisper_timestamped as whisper
import numpy
from scipy.io.wavfile import write

from .sine import sine_tone


# TODO: Make this dynamic based on a local JSON file
swear_words = [
    "fuck",
    "bitch",
    "shit",
    "damn",
    "ass"
    # Companies I don't want to promote?
]


class AutoBleep:
    def __init__(self, input, output="./bleeped_output.mka", language="en"):
        audio = whisper.load_audio(input)

        model = whisper.load_model("tiny", device="cpu")

        result = whisper.transcribe(model, audio, language=language)

        generated_bleep_path = "./bleep.mka"

        length_command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input}"

        length_result = float(
            subprocess.run(length_command, shell=True, capture_output=True).stdout
        )

        # TODO: Generate bleep at bleep_path that is same length as input
        # volume = 1
        # sample_rate = 48000
        # frequency = 1000

        # samples = (
        #     numpy.sin(
        #         2
        #         * numpy.pi
        #         * numpy.arange(sample_rate * length_result)
        #         * frequency
        #         / sample_rate
        #     )
        # ).astype(numpy.float32)

        # write(generated_bleep_path, sample_rate, samples)

        bleep_command = f'ffmpeg -hide_banner -f lavfi -y -i "sine=frequency=1000:sample_rate=48000:duration={length_result}" -c:a aac -ac 2 bleep.mka'

        print("bleep_command", bleep_command)

        subprocess.run(
            bleep_command,
            shell=True,
        )

        filters = []

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
                        # filters.append(f"volume=enable='between(t,{start},{end})'")

                        base_filters.append(
                            f"volume=enable='between(t,{start},{end})':volume=0"
                        )
                        bleep_filters.append(
                            f"volume=enable='between(t,{previous_filter_end},{start})':volume=0"
                        )
                        previous_filter_end = end

        bleep_filters.append(
            f"volume=enable='between(t,{previous_filter_end},{length_result})':volume=0"
        )

        ffmpeg_command = f"ffmpeg -hide_banner -i {input} -i {generated_bleep_path} -filter_complex \"[0:a]volume=1,{','.join(base_filters)}[0x];[1:a]volume=1,{','.join(bleep_filters)}[1x];[0x][1x]amix=inputs=2:duration=first\" -c:a aac -q:a 4 -y {output}"

        print("\n ffmpeg command", ffmpeg_command, "\n \n")

        subprocess.run(ffmpeg_command, shell=True)
