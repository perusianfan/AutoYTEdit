import cv2
import numpy as np
import random
from config import ZOOM_INTENSITY, SHAKE_INTENSITY, get_random_color

class VideoEffects:
    def __init__(self):
        self.shake_offset_x = 0
        self.shake_offset_y = 0
        self.zoom_factor = 1.0
        self.target_zoom = 1.0
        self.current_effect = None
        self.effect_duration = 0
        self.effect_frame = 0

    def apply_zoom(self, frame, factor):
        h, w = frame.shape[:2]
        new_h, new_w = int(h / factor), int(w / factor)
        y1 = (h - new_h) // 2
        x1 = (w - new_w) // 2
        cropped = frame[y1:y1+new_h, x1:x1+new_w]
        return cv2.resize(cropped, (w, h), interpolation=cv2.INTER_LINEAR)

    def apply_shake(self, frame, intensity):
        h, w = frame.shape[:2]
        dx = random.randint(-intensity, intensity)
        dy = random.randint(-intensity, intensity)
        M = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(frame, M, (w, h), borderMode=cv2.BORDER_REFLECT)

    def apply_flash(self, frame, intensity=0.5):
        flash = np.ones_like(frame) * 255
        return cv2.addWeighted(frame, 1 - intensity, flash, intensity, 0)

    def apply_vignette(self, frame, strength=0.5):
        h, w = frame.shape[:2]
        x = np.arange(w)
        y = np.arange(h)
        X, Y = np.meshgrid(x, y)
        cx, cy = w // 2, h // 2
        mask = np.sqrt((X - cx)**2 + (Y - cy)**2)
        mask = mask / mask.max()
        mask = 1 - mask * strength
        mask = np.dstack([mask] * 3)
        return (frame * mask).astype(np.uint8)


    def apply_color_grade(self, frame, style="cinematic"):
        if style == "cinematic":
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            l = clahe.apply(l)
            lab = cv2.merge([l, a, b])
            frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
            frame = cv2.addWeighted(frame, 1.1, np.zeros_like(frame), 0, 10)
        elif style == "warm":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame[:, :, 0] = np.clip(frame[:, :, 0] * 1.1, 0, 255)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        elif style == "cold":
            frame[:, :, 0] = np.clip(frame[:, :, 0] * 1.1, 0, 255)
        elif style == "vintage":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = np.clip(frame * [1.0, 0.9, 0.8], 0, 255).astype(np.uint8)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        return frame

    def apply_blur_background(self, frame, mask):
        blurred = cv2.GaussianBlur(frame, (21, 21), 0)
        mask_3ch = np.dstack([mask] * 3)
        return np.where(mask_3ch > 0, frame, blurred)

    def apply_glow(self, frame, intensity=0.3):
        blurred = cv2.GaussianBlur(frame, (0, 0), 30)
        return cv2.addWeighted(frame, 1, blurred, intensity, 0)

    def apply_chromatic_aberration(self, frame, offset=3):
        b, g, r = cv2.split(frame)
        h, w = frame.shape[:2]
        M_left = np.float32([[1, 0, -offset], [0, 1, 0]])
        M_right = np.float32([[1, 0, offset], [0, 1, 0]])
        r = cv2.warpAffine(r, M_right, (w, h))
        b = cv2.warpAffine(b, M_left, (w, h))
        return cv2.merge([b, g, r])

    def apply_speed_ramp(self, speed_factor):
        return max(0.25, min(2.0, speed_factor))

    def get_random_effect(self):
        effects = ["zoom", "shake", "flash", "glow", "chromatic"]
        return random.choice(effects)

    def process_frame(self, frame, detections=None, frame_idx=0, total_frames=1):
        if random.random() < 0.02:
            self.current_effect = self.get_random_effect()
            self.effect_duration = random.randint(5, 20)
            self.effect_frame = 0

        if self.current_effect and self.effect_frame < self.effect_duration:
            if self.current_effect == "zoom":
                factor = 1.0 + (ZOOM_INTENSITY[1] - 1.0) * (self.effect_frame / self.effect_duration)
                frame = self.apply_zoom(frame, min(factor, ZOOM_INTENSITY[1]))
            elif self.current_effect == "shake":
                intensity = int(SHAKE_INTENSITY[0] + (SHAKE_INTENSITY[1] - SHAKE_INTENSITY[0]) * random.random())
                frame = self.apply_shake(frame, intensity)
            elif self.current_effect == "flash":
                intensity = max(0, 0.5 - (self.effect_frame / self.effect_duration) * 0.5)
                frame = self.apply_flash(frame, intensity)
            elif self.current_effect == "glow":
                frame = self.apply_glow(frame, 0.4)
            elif self.current_effect == "chromatic":
                frame = self.apply_chromatic_aberration(frame, 5)
            self.effect_frame += 1
        else:
            self.current_effect = None

        if detections is not None and len(detections) > 0:
            if random.random() < 0.3:
                frame = self.apply_zoom(frame, random.uniform(1.05, 1.15))

        frame = self.apply_vignette(frame, 0.3)
        
        styles = ["cinematic", "warm", "cold", "vintage"]
        frame = self.apply_color_grade(frame, random.choice(styles) if random.random() < 0.1 else "cinematic")

        return frame