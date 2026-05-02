import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pysrt
import webvtt
import re

# ===== Parse time =====
def parse_time(time_str):
    parts = time_str.strip().split(":")

    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + float(s)
    elif len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + float(s)
    else:
        raise ValueError

# ===== Clean text =====
def clean_text(text):
    text = re.sub(r'</?i>', '', text)
    text = re.sub(r'</?b>', '', text)
    return text.strip()

# ===== Get duration =====
def get_srt_duration(path):
    subs = pysrt.open(path)
    return subs[-1].end.ordinal / 1000 if subs else 0

def get_vtt_duration(path):
    vtt = list(webvtt.read(path))
    return vtt[-1].end_in_seconds if vtt else 0

# ===== Fix SRT =====
def fix_srt(path, new_duration, log):
    subs = pysrt.open(path)
    old = get_srt_duration(path)

    if old == 0:
        log(f"⚠ Bỏ qua (rỗng): {os.path.basename(path)}")
        return

    ratio = new_duration / old
    log(f"{os.path.basename(path)} | Old: {old:.2f}s | Ratio: {ratio:.6f}")

    for sub in subs:
        sub.start.ordinal = int(sub.start.ordinal * ratio)
        sub.end.ordinal = int(sub.end.ordinal * ratio)
        sub.text = clean_text(sub.text)

    out = path.replace(".srt", "_fixed.srt")
    subs.save(out, encoding='utf-8')
    log(f"✔ SRT: {os.path.basename(out)}")

# ===== Fix VTT =====
def fix_vtt(path, new_duration, log):
    vtt = list(webvtt.read(path))
    old = get_vtt_duration(path)

    if old == 0:
        log(f"⚠ Bỏ qua (rỗng): {os.path.basename(path)}")
        return

    ratio = new_duration / old
    log(f"{os.path.basename(path)} | Old: {old:.2f}s | Ratio: {ratio:.6f}")

    out = path.replace(".vtt", "_fixed.vtt")

    with open(out, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")

        for cap in vtt:
            start = cap.start_in_seconds * ratio
            end = cap.end_in_seconds * ratio

            def fmt(t):
                h = int(t // 3600)
                m = int((t % 3600) // 60)
                s = t % 60
                return f"{h:02}:{m:02}:{s:06.3f}"

            text = clean_text(cap.text)

            f.write(f"{fmt(start)} --> {fmt(end)}\n{text}\n\n")

    log(f"✔ VTT: {os.path.basename(out)}")

# ===== GUI =====
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitle Time Fix Tool")
        self.files = []

        # Select files button
        tk.Button(root, text="Chọn file (.srt / .vtt)", command=self.select_files).pack(pady=5)

        # Listbox
        self.listbox = tk.Listbox(root, width=60, height=8)
        self.listbox.pack()

        # Time input
        tk.Label(root, text="Thời lượng video (MM:SS hoặc HH:MM:SS):").pack(pady=5)
        self.time_entry = tk.Entry(root, width=20)
        self.time_entry.pack()

        # Start button
        tk.Button(root, text="Start", command=self.start).pack(pady=10)

        # Log box
        self.log_box = tk.Text(root, height=10, width=70)
        self.log_box.pack()

    def log(self, text):
        self.log_box.insert(tk.END, text + "\n")
        self.log_box.see(tk.END)

    def select_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[("Subtitle", "*.srt *.vtt")]
        )
        if files:
            self.files = files
            self.listbox.delete(0, tk.END)
            for f in files:
                self.listbox.insert(tk.END, os.path.basename(f))

    def start(self):
        if not self.files:
            messagebox.showerror("Lỗi", "Chưa chọn file!")
            return

        time_str = self.time_entry.get()
        try:
            new_duration = parse_time(time_str)
        except:
            messagebox.showerror("Lỗi", "Sai định dạng thời gian!")
            return

        self.log(f"▶ Bắt đầu | Duration: {new_duration:.2f}s\n")

        for path in self.files:
            if path.lower().endswith(".srt"):
                fix_srt(path, new_duration, self.log)
            elif path.lower().endswith(".vtt"):
                fix_vtt(path, new_duration, self.log)

        self.log("\n✅ Hoàn tất!")

# ===== Run =====
root = tk.Tk()
app = App(root)
root.mainloop()