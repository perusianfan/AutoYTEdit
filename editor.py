import cv2
import numpy as np
import os
import random
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, vfx
from config import INPUT_DIR, OUTPUT_DIR, TEMP_DIR, SPEED_VARIATIONS
from detector import PersonDetector
from effects import VideoEffects
from text_overlay import TextOverlay

class AutoVideoEditor:
    def __init__(self):
        self.detector = PersonDetector()
        self.effects = VideoEffects()
        self.text_overlay = TextOverlay()
        self.processed_frames = []

    def process_video(self, input_path, output_path):
        print(f"Processing: {input_path}")
        
        cap = cv2.VideoCapture(input_path)
        if not cap.isOpened():
            print(f"Error opening video: {input_path}")
            return False
        
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")
        
        temp_video = os.path.join(TEMP_DIR, "temp_processed.mp4")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
        
        frame_idx = 0
        detection_interval = 3
        last_detections = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_idx % detection_interval == 0:
                last_detections = self.detector.detect(frame)
            
            frame = self.effects.process_frame(frame, last_detections, frame_idx, total_frames)
            frame = self.text_overlay.process_frame(frame, last_detections, frame_idx, total_frames)
            
            out.write(frame)
            frame_idx += 1
            
            if frame_idx % 100 == 0:
                print(f"Processed {frame_idx}/{total_frames} frames ({100*frame_idx/total_frames:.1f}%)")
        
        cap.release()
        out.release()
        
        print("Adding audio and finalizing...")
        self._finalize_video(input_path, temp_video, output_path)
        
        if os.path.exists(temp_video):
            os.remove(temp_video)
        
        print(f"Done! Output saved to: {output_path}")
        return True


    def _finalize_video(self, original_path, processed_path, output_path):
        try:
            original = VideoFileClip(original_path)
            processed = VideoFileClip(processed_path)
            
            if original.audio is not None:
                final = processed.set_audio(original.audio)
            else:
                final = processed
            
            if random.random() < 0.3:
                speed = random.choice(SPEED_VARIATIONS)
                if speed != 1.0:
                    final = final.fx(vfx.speedx, speed)
            
            final.write_videofile(
                output_path,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=os.path.join(TEMP_DIR, 'temp_audio.m4a'),
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            original.close()
            processed.close()
            final.close()
            
        except Exception as e:
            print(f"Error finalizing video: {e}")
            import shutil
            shutil.copy(processed_path, output_path)

    def add_transitions(self, clips):
        if len(clips) < 2:
            return clips[0] if clips else None
        
        final_clips = []
        for i, clip in enumerate(clips):
            if i > 0 and random.random() < 0.5:
                clip = clip.crossfadein(0.5)
            final_clips.append(clip)
        
        return concatenate_videoclips(final_clips, method="compose")

    def apply_random_speed_ramps(self, clip):
        duration = clip.duration
        if duration < 3:
            return clip
        
        segments = []
        current_time = 0
        
        while current_time < duration:
            segment_duration = min(random.uniform(1, 3), duration - current_time)
            segment = clip.subclip(current_time, current_time + segment_duration)
            
            if random.random() < 0.2:
                speed = random.choice([0.5, 0.75, 1.25, 1.5])
                segment = segment.fx(vfx.speedx, speed)
            
            segments.append(segment)
            current_time += segment_duration
        
        return concatenate_videoclips(segments)

def process_all_videos():
    editor = AutoVideoEditor()
    
    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm')
    
    input_files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(video_extensions)]
    
    if not input_files:
        print(f"No video files found in {INPUT_DIR}/")
        print("Please add video files to the input folder and run again.")
        return
    
    print(f"Found {len(input_files)} video(s) to process")
    
    for filename in input_files:
        input_path = os.path.join(INPUT_DIR, filename)
        
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_edited{ext}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        
        editor.process_video(input_path, output_path)
        
        editor.effects = VideoEffects()
        editor.text_overlay = TextOverlay()

if __name__ == "__main__":
    process_all_videos()