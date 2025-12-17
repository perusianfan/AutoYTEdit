import sys
import os
from editor import AutoVideoEditor, process_all_videos
from config import INPUT_DIR, OUTPUT_DIR

def main():
    print("=" * 50)
    print("AUTO VIDEO EDITOR")
    print("=" * 50)
    print(f"Input folder: {INPUT_DIR}/")
    print(f"Output folder: {OUTPUT_DIR}/")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
        if os.path.isfile(input_path):
            editor = AutoVideoEditor()
            filename = os.path.basename(input_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(OUTPUT_DIR, f"{name}_edited{ext}")
            editor.process_video(input_path, output_path)
        else:
            print(f"File not found: {input_path}")
    else:
        process_all_videos()

if __name__ == "__main__":
    main()