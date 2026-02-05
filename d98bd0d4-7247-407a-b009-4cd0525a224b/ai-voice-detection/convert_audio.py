
import base64
import os
import sys

def audio_to_base64(file_path):
    """Convert an audio file to a Base64 string."""
    try:
        with open(file_path, "rb") as audio_file:
            encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
        return encoded_string
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except Exception as e:
        print(f"Error converting file: {e}")
        return None

def base64_to_audio(base64_string, output_path):
    """Convert a Base64 string back to an audio file."""
    try:
        audio_data = base64.b64decode(base64_string)
        with open(output_path, "wb") as audio_file:
            audio_file.write(audio_data)
        print(f"Successfully saved to {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")

def generate_mock_base64():
    """Generates a dummy base64 string for testing purposes."""
    # A tiny valid mp3 header or just random bytes for mock testing
    dummy_content = b"ID3" + b"\x00" * 100
    return base64.b64encode(dummy_content).decode('utf-8')

if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "encode":
        b64 = audio_to_base64(sys.argv[2])
        if b64:
            print(b64[:100] + "...") # Print snippet
            
    elif len(sys.argv) == 2 and sys.argv[1] == "mock":
        print(generate_mock_base64())
        
    else:
        print("Usage:")
        print("  python convert_audio.py encode <file_path>")
        print("  python convert_audio.py mock")
