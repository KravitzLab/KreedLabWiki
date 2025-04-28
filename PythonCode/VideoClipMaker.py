#%% ROI Setup
import cv2

# === CONFIGURATION ===
video_path = "C:/Users/barrett.m/Desktop/event_clips/0424.mp4"
output_image_path = "C:/Users/barrett.m/Desktop/event_clips/roi_preview.jpg"
sample_time_sec = 10 # change to the timestamp you want to sample from

# Example ROI — edit this to test new ones
roi = (800, 100, 50, 50)  # (x, y, w, h)

# === Load video and seek to frame ===
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
frame_number = int(fps * sample_time_sec)
cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

ret, frame = cap.read()
if not ret:
    print("❌ Could not read frame.")
else:
    # Draw red rectangle on ROI
    x, y, w, h = roi
    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
    
    # Save to disk
    cv2.imwrite(output_image_path, frame)
    print(f"✅ ROI preview saved at: {output_image_path}")

cap.release()
#%% Clip maker
import cv2
import os
import subprocess
from tqdm import tqdm

# === CONFIGURATION ===
video_path = "C:/Users/barrett.m/Desktop/M1_FR1_2/M1Vid_4FR12025-04-23T16_21_36.avi"
output_dir = "C:/Users/barrett.m/Desktop/M1_FR1_2"
final_output_path = os.path.join(output_dir, "combined_FR1_2.avi")

roi = (640, 120, 50, 50)  # (x, y, w, h)
threshold = 80          # blue brightness threshold
sample_rate = 30          # frames per second to check
max_duration_sec = 100000000000  # max duration to analyze (e.g. 3 hours)

pre_sec = 5
post_sec = 5
combine_within = 10  # seconds to merge nearby pulses

# === STEP 1: DETECT LIGHT PULSES FROM VIDEO ===
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(min(cap.get(cv2.CAP_PROP_FRAME_COUNT), max_duration_sec * fps))
sample_every = max(1, int(fps // sample_rate))

timestamps = []
with tqdm(total=total_frames, desc="Scanning video for pulses") as pbar:
    frame_idx = 0
    while frame_idx < total_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every == 0:
            x, y, w, h = roi
            roi_frame = frame[y:y+h, x:x+w]
            blue_avg = roi_frame[:, :, 0].mean()
            time_sec = frame_idx / fps

            if blue_avg > threshold:
                if len(timestamps) == 0 or time_sec - timestamps[-1] > 1:
                    timestamps.append(time_sec)
                    print(f"🔵 Detected pulse at {time_sec:.2f} sec", end='\r')


        frame_idx += 1
        pbar.update(1)

cap.release()
print(f"✅ Detected {len(timestamps)} pulses. First few: {timestamps[:10]}")

# === STEP 2: MERGE CLOSE TIMESTAMPS INTO CLIP BOUTS ===
merged = []
if timestamps:
    start = timestamps[0] - pre_sec
    end = timestamps[0] + post_sec

    for t in timestamps[1:]:
        if t - end <= combine_within:
            end = t + post_sec
        else:
            merged.append((max(start, 0), end - max(start, 0)))
            start = t - pre_sec
            end = t + post_sec
    merged.append((max(start, 0), end - max(start, 0)))

# === STEP 3: CUT CLIPS BASED ON MERGED TIMESTAMPS ===
os.makedirs(output_dir, exist_ok=True)
clip_paths = []

for i, (start, duration) in enumerate(merged):
    start_clean = f"{start:.2f}".replace('.', 'p')
    clip_path = os.path.join(output_dir, f"clip_{i:03d}_{start_clean}s.avi")

    print(f"✂️  Cutting clip {i:03d} at {start:.2f}s → {start+duration:.2f}s", end='\r')
    cmd = [
        "ffmpeg", "-ss", str(start), "-i", video_path,
        "-t", str(duration), "-c:v", "copy", "-c:a", "copy", "-y", clip_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    print(f"✅ Saved {os.path.basename(clip_path)}".ljust(80))
    clip_paths.append(f"file '{clip_path}'")

# === STEP 4: CONCATENATE ALL CLIPS INTO FINAL VIDEO ===
concat_list_path = os.path.join(output_dir, "clip_list.txt")
with open(concat_list_path, "w") as f:
    for path in clip_paths:
        f.write(path + "\n")

concat_cmd = [
    "ffmpeg",
    "-f", "concat",
    "-safe", "0",
    "-i", concat_list_path,
    "-c", "copy",
    final_output_path
]
subprocess.run(concat_cmd)
print(f"🎬 Final video saved at: {final_output_path}")


#%% Blue light timestamp getter
import cv2
import pandas as pd
from tqdm import tqdm

# === CONFIGURATION ===
video_path = "C:/Users/barrett.m/Desktop/event_clips/0424.mp4"
roi = (800, 100, 50, 50)  # (x, y, w, h)

threshold = 120
sample_rate = 30  # frames per second to check

# === STEP 1: Open video and setup ===
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise ValueError("❌ Could not open video.")

fps = cap.get(cv2.CAP_PROP_FPS) or 30
frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = frame_count / fps
sample_every = max(1, int(fps // sample_rate))

timestamps = []
frame_idx = 0

# === STEP 2: Scan for pulses ===
print("🔍 Scanning for blue light pulses...")
with tqdm(total=frame_count) as pbar:
    while frame_idx < frame_count:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_every == 0:
            x, y, w, h = roi
            roi_frame = frame[y:y+h, x:x+w]
            blue_avg = roi_frame[:, :, 0].mean()
            time_sec = frame_idx / fps

            if blue_avg > threshold:
                if len(timestamps) == 0 or time_sec - timestamps[-1] > 1:
                    timestamps.append(time_sec)

        frame_idx += 1
        pbar.update(1)

cap.release()

# === STEP 3: Save to DataFrame ===
touch_df = pd.DataFrame({"Touch_Timestamp_sec": timestamps})
print(f"✅ Detected {len(timestamps)} pulses.")
#%% Graph based on blue light timestamps
import cv2
import pandas as pd
import numpy as np
from moviepy import VideoFileClip, CompositeVideoClip, VideoClip

# === CONFIGURATION ===
video_path = "C:/Users/barrett.m/Desktop/event_clips/Grazing_Clip.mp4"
output_path = "C:/Users/barrett.m/Desktop/event_clips/Grazing_Clip_Annotated.mp4"

combine_within = 60       # seconds to group pulses into bouts
feed_filter = 5           # minimum bout duration to be considered a meal

# === STEP 1: Load timestamps from touch_df ===
timestamps = touch_df["Touch_Timestamp_sec"].tolist()

# === STEP 2: Classify Meals from touch timestamps ===
pulse_df = pd.DataFrame({
    "Timestamp": pd.to_datetime(pd.Series(timestamps), unit='s'),
    "LeftFeedDur": 1
})

def classify_bouts(touch_times, combine_within=60, min_apart=5):
    if not touch_times:
        print("⚠️ No touches found.")
        return []

    summary = []
    bout = [touch_times[0]]
    print(f"📌 Starting new bout at {touch_times[0]:.2f}s")

    for t in touch_times[1:]:
        if t - bout[-1] <= combine_within:
            bout.append(t)
            print(f"   ➕ Adding {t:.2f}s to current bout (Δ={t - bout[-2]:.2f}s)")
        else:
            print(f"🚪 Bout closed at {bout[-1]:.2f}s (Δ={t - bout[-1]:.2f}s to next)")
            if qualifies_as_meal(bout, min_apart):
                print(f"✅ Meal accepted: {bout[0]:.2f}s → {bout[-1]:.2f}s")
                summary.append((bout[0], bout[-1]))
            else:
                print(f"❌ Bout rejected (no touches ≥ {min_apart}s apart)")
            bout = [t]
            print(f"📌 Starting new bout at {t:.2f}s")

    # Final bout
    print(f"🚪 Final bout closed at {bout[-1]:.2f}s")
    if qualifies_as_meal(bout, min_apart):
        print(f"✅ Meal accepted: {bout[0]:.2f}s → {bout[-1]:.2f}s")
        summary.append((bout[0], bout[-1]))
    else:
        print(f"❌ Final bout rejected (no touches ≥ {min_apart}s apart)")

    print(f"\n🍽️ Total meals detected: {len(summary)}")
    return summary

def qualifies_as_meal(bout, min_apart):
    for i in range(len(bout)):
        for j in range(i+1, len(bout)):
            if bout[j] - bout[i] >= min_apart:
                return True
    return False

meals = classify_bouts(timestamps, combine_within=60, min_apart=5)

def make_overlay(get_frame, t):
    frame = get_frame(t)
    img = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)

    graph_height = 400
    padded = np.zeros((img.shape[0] + graph_height, img.shape[1], 3), dtype=np.uint8)
    padded[graph_height:, :, :] = img

    width = img.shape[1]
    window_size = 30
    start_time = t - window_size / 2
    end_time = t + window_size / 2

    font = cv2.FONT_HERSHEY_SIMPLEX

    # === 1. Touch tick marks (white, taller)
    for ts in timestamps:
        if start_time <= ts <= end_time:
            x = int(((ts - start_time) / window_size) * width)
            if 0 <= x < width:
                cv2.line(padded, (x, 50), (x, 140), (255, 255, 255), 6)

    # === 2. Meal bars (green, taller)
    for start, end in meals:
        if end < 0 or start > end_time:
            continue
        overlap_start = max(start, start_time, 0)
        overlap_end = min(end, end_time)
        x1 = int(((overlap_start - start_time) / window_size) * width)
        x2 = int(((overlap_end - start_time) / window_size) * width)
        if x1 < width and x2 > 0:
            cv2.rectangle(padded, (x1, 160), (x2, 240), (144, 238, 144), -1)

    # === 3. Scrolling timestamp bar
    tick_interval = 5
    first_tick_time = t - window_size / 2
    tick_offset = first_tick_time % tick_interval

    for i in range(int(window_size // tick_interval) + 2):
        tick_time = first_tick_time - tick_offset + i * tick_interval
        x = int(((tick_time - first_tick_time) / window_size) * width)
        if 0 <= x < width:
            cv2.line(padded, (x, 300), (x, 320), (180, 180, 180), 3)
            cv2.putText(padded, f"{tick_time:.0f}s", (x - 30, 390), font, 2.0, (200, 200, 200), 4, cv2.LINE_AA)

    # === 4. Center red time marker
    center_x = width // 2
    cv2.line(padded, (center_x, 0), (center_x, graph_height), (0, 0, 255), 4)

    # === 5. Labels (repositioned)
    cv2.putText(padded, "Touches", (10, 95), font, 2.8, (255, 255, 255), 5, cv2.LINE_AA)
    cv2.putText(padded, "Meals", (10, 205), font, 2.8, (255, 255, 255), 5, cv2.LINE_AA)

    return cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)


# === STEP 4: Build and save final video ===
print("🎞️ Rendering video from touch_df timestamps...")
clip = VideoFileClip(video_path)
new_height = clip.h + 100

annotated = VideoClip(lambda t: make_overlay(clip.get_frame, t), duration=clip.duration)
final = CompositeVideoClip([annotated], size=(clip.w, new_height))
final.write_videofile(output_path, fps=clip.fps)
print(f"✅ Annotated video saved to: {output_path}")