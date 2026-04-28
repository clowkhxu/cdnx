import tkinter as tk
from tkinter import filedialog
import os
import pysrt
import webvtt
import re

# ===== CONFIG =====
OLD_DURATION = 3851
NEW_DURATION = 3859
RATIO = NEW_DURATION / OLD_DURATION

# ===== GUI chọn folder =====
root = tk.Tk()
root.withdraw()

folder_path = filedialog.askdirectory(title="Chọn thư mục chứa subtitle")

if not folder_path:
    print("Không chọn folder!")
    exit()

print(f"Đang xử lý: {folder_path}")
print(f"Ratio: {RATIO:.6f}")

# ===== Hàm remove thẻ <i> =====
def clean_text(text):
    text = re.sub(r'</?i>', '', text)  # xóa <i> và </i>
    return text.strip()

# ===== Xử lý SRT =====
def fix_srt(file_path):
    subs = pysrt.open(file_path)

    for sub in subs:
        sub.start.ordinal = int(sub.start.ordinal * RATIO)
        sub.end.ordinal = int(sub.end.ordinal * RATIO)
        sub.text = clean_text(sub.text)

    output = file_path.replace(".srt", "_fixed.srt")
    subs.save(output, encoding='utf-8')
    print(f"✔ SRT: {os.path.basename(output)}")

# ===== Xử lý VTT =====
def fix_vtt(file_path):
    vtt = webvtt.read(file_path)
    output = file_path.replace(".vtt", "_fixed.vtt")

    with open(output, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")

        for caption in vtt:
            start = caption.start_in_seconds * RATIO
            end = caption.end_in_seconds * RATIO

            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = t % 60
                return f"{h:02}:{m:02}:{s:06.3f}"

            text = clean_text(caption.text)

            f.write(f"{fmt(start)} --> {fmt(end)}\n")
            f.write(text + "\n\n")

    print(f"✔ VTT: {os.path.basename(output)}")

# ===== Loop file =====
for file in os.listdir(folder_path):
    path = os.path.join(folder_path, file)

    if file.endswith(".srt"):
        fix_srt(path)

    elif file.endswith(".vtt"):
        fix_vtt(path)

print("\n✅ Hoàn tất!")