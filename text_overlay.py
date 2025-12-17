import cv2
import numpy as np
import random
from PIL import Image, ImageDraw, ImageFont
from config import get_random_caption, get_random_intro, get_random_color, COLORS, SHADOW_COLORS

class TextOverlay:
    def __init__(self):
        self.current_text = None
        self.text_duration = 0
        self.text_frame = 0
        self.text_position = None
        self.text_style = None
        self.font_size = 40

    def get_font(self, size):
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            try:
                return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
            except:
                return ImageFont.load_default()

    def add_text_pil(self, frame, text, position, font_size=40, color=(255, 255, 255), shadow=True):
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        font = self.get_font(font_size)
        
        x, y = position
        
        if shadow:
            shadow_color = random.choice(SHADOW_COLORS)
            for offset in [(2, 2), (3, 3)]:
                draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
        
        draw.text((x, y), text, font=font, fill=color)
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def add_outlined_text(self, frame, text, position, font_size=40, color=(255, 255, 255), outline_color=(0, 0, 0)):
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)
        font = self.get_font(font_size)
        
        x, y = position
        outline_width = 3
        
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
        
        draw.text((x, y), text, font=font, fill=color)
        
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


    def add_animated_text(self, frame, text, position, frame_idx, font_size=40, color=(255, 255, 255)):
        scale = 1.0 + 0.1 * np.sin(frame_idx * 0.2)
        adjusted_size = int(font_size * scale)
        return self.add_outlined_text(frame, text, position, adjusted_size, color)

    def add_glitch_text(self, frame, text, position, font_size=40, color=(255, 255, 255)):
        if random.random() < 0.3:
            offset = random.randint(-5, 5)
            position = (position[0] + offset, position[1])
        
        frame = self.add_outlined_text(frame, text, position, font_size, color)
        
        if random.random() < 0.2:
            r_offset = random.randint(-3, 3)
            frame_copy = frame.copy()
            frame[:, :, 2] = np.roll(frame_copy[:, :, 2], r_offset, axis=1)
        
        return frame

    def add_person_label(self, frame, bbox, label="PERSON", confidence=0.0):
        x1, y1, x2, y2 = map(int, bbox)
        
        labels = ["MAIN CHARACTER", "NPC", "LEGEND", "GOAT", "REAL ONE", "VIBE CHECK", "W", "ICONIC"]
        label = random.choice(labels) if random.random() < 0.5 else f"CONF: {confidence:.0%}"
        
        color = random.choice(COLORS)
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(frame, (x1, y1 - 25), (x1 + label_size[0] + 10, y1), color, -1)
        cv2.putText(frame, label, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        return frame

    def add_tracking_lines(self, frame, bbox, color=None):
        if color is None:
            color = random.choice(COLORS)
        
        x1, y1, x2, y2 = map(int, bbox)
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        h, w = frame.shape[:2]
        
        cv2.line(frame, (0, cy), (x1, cy), color, 1)
        cv2.line(frame, (x2, cy), (w, cy), color, 1)
        cv2.line(frame, (cx, 0), (cx, y1), color, 1)
        cv2.line(frame, (cx, y2), (cx, h), color, 1)
        
        corner_len = 20
        cv2.line(frame, (x1, y1), (x1 + corner_len, y1), color, 3)
        cv2.line(frame, (x1, y1), (x1, y1 + corner_len), color, 3)
        cv2.line(frame, (x2, y1), (x2 - corner_len, y1), color, 3)
        cv2.line(frame, (x2, y1), (x2, y1 + corner_len), color, 3)
        cv2.line(frame, (x1, y2), (x1 + corner_len, y2), color, 3)
        cv2.line(frame, (x1, y2), (x1, y2 - corner_len), color, 3)
        cv2.line(frame, (x2, y2), (x2 - corner_len, y2), color, 3)
        cv2.line(frame, (x2, y2), (x2, y2 - corner_len), color, 3)
        
        return frame

    def process_frame(self, frame, detections=None, frame_idx=0, total_frames=1):
        h, w = frame.shape[:2]
        
        if frame_idx < 60:
            intro = get_random_intro() if frame_idx == 0 or self.current_text is None else self.current_text
            if frame_idx == 0:
                self.current_text = intro
            alpha = min(1.0, frame_idx / 20)
            if alpha > 0:
                frame = self.add_animated_text(frame, intro, (50, 50), frame_idx, 50, (255, 255, 0))
        
        if random.random() < 0.01 and self.text_duration == 0:
            self.current_text = get_random_caption()
            self.text_duration = random.randint(30, 90)
            self.text_position = (random.randint(50, w - 300), random.randint(h // 2, h - 100))
            self.text_style = random.choice(["normal", "glitch", "animated"])
        
        if self.text_duration > 0:
            if self.text_style == "glitch":
                frame = self.add_glitch_text(frame, self.current_text, self.text_position, 45, get_random_color())
            elif self.text_style == "animated":
                frame = self.add_animated_text(frame, self.current_text, self.text_position, frame_idx, 45, get_random_color())
            else:
                frame = self.add_outlined_text(frame, self.current_text, self.text_position, 45, get_random_color())
            self.text_duration -= 1
        
        if detections is not None:
            for det in detections:
                bbox = det[:4]
                conf = det[4] if len(det) > 4 else 0.0
                
                if random.random() < 0.7:
                    frame = self.add_tracking_lines(frame, bbox)
                
                if random.random() < 0.5:
                    frame = self.add_person_label(frame, bbox, confidence=conf)
        
        return frame