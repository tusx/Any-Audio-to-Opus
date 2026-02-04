import os
import subprocess

def convert_audiobooks(root_dir):
    # Added common audiobook and audio formats
    input_extensions = (".mp3", ".m4a", ".m4b", ".wav", ".aac", ".flac", ".aax")
    output_ext = ".opus"
    total_saved_bytes = 0

    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            # Check if file ends with any of our supported extensions
            if filename.lower().endswith(input_extensions):

                input_path = os.path.join(dirpath, filename)
                base_name = os.path.splitext(filename)[0]
                output_path = os.path.join(dirpath, base_name + output_ext)

                # Skip if the .opus version already exists (prevents accidental overwrites)
                if os.path.exists(output_path):
                    print(f"--> Skipping {filename}, Opus version already exists.")
                    continue

                orig_size_bytes = os.path.getsize(input_path)
                orig_size_mb = orig_size_bytes / (1024 * 1024)

                print(f"\n--- Processing: {filename} ---")
                print(f"Original Size: {orig_size_mb:.2f} MB")

                # FFmpeg command: -map_metadata 0 keeps tags/covers
                cmd = [
                    'ffmpeg', '-y', '-i', input_path,
                    '-map_metadata', '0', '-c:a', 'libopus',
                    '-b:a', '24k', '-ac', '1', '-vbr', 'on',
                    output_path
                ]

                try:
                    print("Running ffmpeg conversion...")
                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

                    if os.path.exists(output_path):
                        new_size_bytes = os.path.getsize(output_path)
                        new_size_mb = new_size_bytes / (1024 * 1024)

                        saved_mb = orig_size_mb - new_size_mb
                        total_saved_bytes += (orig_size_bytes - new_size_bytes)

                        print(f"New Size:      {new_size_mb:.2f} MB")
                        print(f"Space Saved:   {saved_mb:.2f} MB ({(saved_mb/orig_size_mb)*100:.1f}%)")

                        # Delete original
                        os.remove(input_path)
                        print("Original file deleted successfully.")

                except subprocess.CalledProcessError:
                    print(f"!! Error converting {filename}. Skipping deletion. !!")

    total_saved_gb = total_saved_bytes / (1024**3)
    print("\n" + "="*30)
    print(f"COMPLETED! Total disk space reclaimed: {total_saved_gb:.2f} GB")
    print("="*30)

if __name__ == "__main__":
    target_folder = "."
    print("\n Note: Make sure you have setup the app.py file correctly and it is in right location. \n")
    confirm = input(f"Convert all Audio Files in '{os.path.abspath(target_folder)}' to Opus and DELETE originals? (y/n): ")
    if confirm.lower() == 'y':
        convert_audiobooks(target_folder)
    else:
        print("Aborted.")
