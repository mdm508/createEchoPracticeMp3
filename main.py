import os
from pydub import AudioSegment, silence

# Constants (These will be set dynamically based on user input)
MIN_SILENCE_LEN = 200  # Minimum length of silence to be used for a split (in milliseconds)
SILENCE_THRESH_OFFSET = -16  # Silence threshold offset in dBFS
KEEP_SILENCE = 0  # Amount of silence to leave at the beginning and end of each chunk (in milliseconds)
SILENCE_MULTIPLIER = 2  # Multiplier for the length of silence to add after each chunk


def load_audio(file_path):
    """Load an audio file and return an AudioSegment object."""
    try:
        audio = AudioSegment.from_file(file_path)
        return audio
    except Exception as e:
        print(f"Error loading audio file '{file_path}': {e}")
        raise


def calculate_silence_threshold(audio, offset_db):
    """Calculate the silence threshold based on the audio's dBFS and an offset."""
    return audio.dBFS + offset_db


def split_audio_on_silence(audio, min_silence_len, silence_thresh, keep_silence):
    """Split audio into chunks based on silence."""
    chunks = silence.split_on_silence(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
        keep_silence=keep_silence
    )
    return chunks


def process_chunk(chunk, silence_multiplier):
    """Process an individual audio chunk by normalizing and adding silence."""
    # Normalize the chunk volume (optional)
    chunk = chunk.normalize()

    # Calculate the duration of the chunk
    chunk_length = len(chunk)  # Duration in milliseconds

    # Create silence based on the multiplier
    silence_duration = chunk_length * silence_multiplier
    silence_chunk = AudioSegment.silent(duration=silence_duration)

    # Append the chunk and the silence
    processed_chunk = chunk + silence_chunk
    return processed_chunk


def process_chunks(chunks, silence_multiplier):
    """Process a list of audio chunks."""
    processed_chunks = []
    for i, chunk in enumerate(chunks):
        processed_chunk = process_chunk(chunk, silence_multiplier)
        processed_chunks.append(processed_chunk)
    return processed_chunks


def concatenate_chunks(chunks):
    """Concatenate a list of audio chunks into a single AudioSegment."""
    final_audio = AudioSegment.empty()
    for chunk in chunks:
        final_audio += chunk
    return final_audio


def export_audio(audio, file_path):
    """Export the final audio to a file."""
    try:
        audio.export(file_path, format="mp3")
        print(f"Exported processed audio to '{file_path}'.")
    except Exception as e:
        print(f"Error exporting audio to '{file_path}': {e}")
        raise


def process_audio(input_file, output_file):
    """Main function to process the audio file."""
    # Load the audio file
    audio = load_audio(input_file)

    # Calculate silence threshold
    silence_thresh = calculate_silence_threshold(audio, SILENCE_THRESH_OFFSET)

    # Split audio into chunks based on silence
    chunks = split_audio_on_silence(audio, MIN_SILENCE_LEN, silence_thresh, KEEP_SILENCE)

    if not chunks:
        print("No chunks were created. Check the silence detection parameters.")
        return

    # Process each chunk
    processed_chunks = process_chunks(chunks, SILENCE_MULTIPLIER)

    # Concatenate all processed chunks into one audio segment
    final_audio = concatenate_chunks(processed_chunks)

    # Export the final audio to a file
    export_audio(final_audio, output_file)

    print("Processing complete.")


if __name__ == "__main__":
    import sys

    # Prompt the user for input file and output file name
    in_file = input('Enter source MP3 file path:\n').strip()
    out_file_name = input("Enter name for output file (with .mp3 extension):\n").strip()

    # Ensure the input file exists
    if not os.path.isfile(in_file):
        print(f"Error: The file '{in_file}' does not exist.")
        sys.exit(1)

    # Define the output directory and ensure cross-platform compatibility
    output_dir = os.path.join(os.getcwd(), 'out')

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created output directory: '{output_dir}'")
        except Exception as e:
            print(f"Error creating output directory '{output_dir}': {e}")
            sys.exit(1)

    # Construct the full output file path
    out_file = os.path.join(output_dir, out_file_name)

    # Process the audio
    process_audio(in_file, out_file)
