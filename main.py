#credit by nijar
import os
import time
from collections import defaultdict

import cv2
import mediapipe as mp

# audio libs
try:
    from gtts import gTTS
except Exception:
    gTTS = None
try:
    import pyttsx3
except Exception:
    pyttsx3 = None

import pygame

AUDIO_DIR = "audio"
PHRASES = {
    "open": ("Halo semuanya", "halo.mp3"),
    "thumb_only": ("Nama aku", "nama_aku.mp3"),
    "pinky_only": ("Nizar", "nizar.mp3"),
    "shaka": ("Salam kenal", "salam_kenal.mp3"),
}
# frames that gesture must be stable to trigger
DEBOUNCE_FRAMES = 6
# cooldown seconds after a trigger to avoid repeats
COOLDOWN = 2.0


def ensure_audio_dir():
    if not os.path.exists(AUDIO_DIR):
        os.makedirs(AUDIO_DIR)


def make_audio_gtts(text, filepath):
    """Try generate mp3 via gTTS (requires internet)."""
    if gTTS is None:
        raise RuntimeError("gTTS not installed / not available.")
    tts = gTTS(text=text, lang="id")
    tts.save(filepath)


def make_audio_pyttsx3(text, filepath_wav):
    """Fallback: generate wav via pyttsx3 (offline)."""
    if pyttsx3 is None:
        raise RuntimeError("pyttsx3 not installed / not available.")
    engine = pyttsx3.init()
    engine.save_to_file(text, filepath_wav)
    engine.runAndWait()


def ensure_audio_files():
    """Ensure each phrase has a playable file. Try gTTS->mp3, fallback pyttsx3->wav."""
    ensure_audio_dir()
    paths = {}
    for key, (text, fname) in PHRASES.items():
        mp3_path = os.path.join(AUDIO_DIR, fname)
        wav_path = os.path.join(AUDIO_DIR, fname.replace(".mp3", ".wav"))

        if os.path.exists(mp3_path) or os.path.exists(wav_path):
            paths[key] = mp3_path if os.path.exists(mp3_path) else wav_path
            continue

        # Try gTTS first
        try:
            print(f"[TTS] Generating (gTTS) -> {mp3_path}")
            make_audio_gtts(text, mp3_path)
            paths[key] = mp3_path
            continue
        except Exception as e:
            print(f"[TTS] gTTS failed for '{text}': {e}")

        # fallback pyttsx3
        try:
            print(f"[TTS] Generating (pyttsx3) -> {wav_path}")
            make_audio_pyttsx3(text, wav_path)
            paths[key] = wav_path
            continue
        except Exception as e:
            print(f"[TTS] pyttsx3 failed for '{text}': {e}")

        raise RuntimeError(f"Failed to generate audio for: {text}")

    return paths


def init_pygame():
    pygame.mixer.init()


def play_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
        sound.play()
    except Exception as e:
        print(f"[AUDIO] Failed to play {path}: {e}")


# ---------- Mediapipe helper ----------
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

FINGER_TIPS = [4, 8, 12, 16, 20]
FINGER_PIPS = [3, 6, 10, 14, 18]  


def fingers_state(hand_landmarks, handedness_label=None):
    """
    Return dict of finger states (True == finger extended).
    Very simple heuristic:
     - for index/middle/ring/pinky: tip.y < pip.y -> extended (image coords)
     - for thumb: compare x of tip and ip depending on handedness
    """
    lm = hand_landmarks.landmark
    fingers = {}
    names = ["thumb", "index", "middle", "ring", "pinky"]

    # index, middle, ring, pinky
    for tip_id, pip_id, name in zip(FINGER_TIPS[1:], FINGER_PIPS[1:], names[1:]):
        fingers[name] = lm[tip_id].y < lm[pip_id].y

    # thumb (x comparison)
    try:
        if handedness_label is None:
            fingers["thumb"] = lm[4].x < lm[3].x
        else:
            if handedness_label == "Right":
                fingers["thumb"] = lm[4].x < lm[3].x
            else:
                fingers["thumb"] = lm[4].x > lm[3].x
    except Exception:
        fingers["thumb"] = False

    return fingers


def identify_gesture(fingers: dict):
    """Return gesture key or None."""
    # all five fingers up -> open palm
    if all(fingers.get(f, False) for f in ["thumb", "index", "middle", "ring", "pinky"]):
        return "open"
    # thumb only (👍)
    if fingers.get("thumb", False) and not any(
        fingers.get(f, False) for f in ["index", "middle", "ring", "pinky"]
    ):
        return "thumb_only"
    # pinky only
    if fingers.get("pinky", False) and not any(
        fingers.get(f, False) for f in ["index", "middle", "ring", "thumb"]
    ):
        return "pinky_only"
    # shaka: thumb + pinky
    if fingers.get("thumb", False) and fingers.get("pinky", False) and not any(
        fingers.get(f, False) for f in ["index", "middle", "ring"]
    ):
        return "shaka"
    return None


def main():
    print("Starting gesture recognition...")
    paths = ensure_audio_files()
    print("Audio files ready:", paths)
    init_pygame()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Webcam tidak terbuka. Pastikan kamera terpasang.")
        return

    stable_counts = defaultdict(int)
    last_trigger_time = 0
    last_trigger_gesture = None

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.6,
        min_tracking_confidence=0.6,
    ) as hands:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: Tidak mendapat frame dari kamera.")
                break

            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = hands.process(img_rgb)

            detected_gesture = None
            gesture_text = ""

            if results.multi_hand_landmarks:
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    handedness_label = None
                    if results.multi_handedness and i < len(results.multi_handedness):
                        handedness_label = results.multi_handedness[i].classification[0].label

                    fingers = fingers_state(hand_landmarks, handedness_label)
                    gesture = identify_gesture(fingers)

                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    if gesture:
                        detected_gesture = gesture
                        gesture_text = PHRASES[gesture][0]
                        break

            # Debounce
            if detected_gesture:
                stable_counts[detected_gesture] += 1
                for k in list(stable_counts.keys()):
                    if k != detected_gesture:
                        stable_counts[k] = 0

                if (
                    stable_counts[detected_gesture] >= DEBOUNCE_FRAMES
                    and time.time() - last_trigger_time > COOLDOWN
                ):
                    audio_path = paths.get(detected_gesture)
                    if audio_path:
                        print(f"[TRIGGER] {detected_gesture} -> {gesture_text}")
                        play_sound(audio_path)
                    last_trigger_time = time.time()
                    last_trigger_gesture = detected_gesture
                    stable_counts[detected_gesture] = 0
            else:
                for k in list(stable_counts.keys()):
                    stable_counts[k] = 0

            display_text = ""
            if detected_gesture:
                display_text = gesture_text
            elif last_trigger_gesture and time.time() - last_trigger_time < 1.5:
                display_text = PHRASES[last_trigger_gesture][0]

            if display_text:
                cv2.putText(
                    frame,
                    display_text,
                    (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

            cv2.putText(
                frame,
                "Tekan 'q' untuk keluar",
                (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (200, 200, 200),
                1,
                cv2.LINE_AA,
            )

            cv2.imshow("Gesture -> Teks + Suara", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()
    try:
        pygame.mixer.quit()
    except Exception:
        pass
    print("Selesai.")


if __name__ == "__main__":
    main()
