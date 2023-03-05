import subprocess
import whisper_timestamped as whisper

# TODO: Make this dynamic based on a local JSON file
default_swear_words = [
    "fuck",
    "bitch",
    "shit",
    "damn",
    "ass"
    # Companies I don't want to promote?
]


class AutoBleep:
    def __init__(
        self,
        input,
        output="./outputs/output.mka",
        language="en",
        swear_words=default_swear_words,
    ):
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

        ffmpeg_command = f"ffmpeg -hide_banner -i {input} -f lavfi -i \"sine=frequency=1000\" -filter_complex \"[0:a]volume=1,{','.join(base_filters)}[0x];[1:a]volume=1,{','.join(bleep_filters)}[1x];[0x][1x]amix=inputs=2:duration=first\" -c:a aac -q:a 4 -y {output}"

        print("\n ffmpeg command", ffmpeg_command, "\n \n")

        subprocess.run(ffmpeg_command, shell=True)
