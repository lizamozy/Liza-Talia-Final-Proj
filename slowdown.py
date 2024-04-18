from pydub import AudioSegment
from pydub.playback import play

def slow_down_wav(input_file, output_file, speed_factor):
    # Load the audio file
    audio = AudioSegment.from_file(input_file, format="wav")

    # Slow down the audio
    slowed_down = audio._spawn(audio.raw_data, overrides={
        "frame_rate": int(audio.frame_rate / speed_factor)
    })

    # Export the modified audio
    slowed_down.export(output_file, format="wav")

if __name__ == "__main__":
    input_file = "test.wav"  # Path to the input .wav file
    output_file = "slower.wav"  # Path to the output .wav file
    speed_factor = 1.5  # Slow down factor (1.0 means no change)

    slow_down_wav(input_file, output_file, speed_factor)

    print(f"Audio slowed down and saved to {output_file}")



