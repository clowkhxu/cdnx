import tkinter as tk
from tkinter import filedialog
import re
import os

# ===== Xóa HTML tag =====
def remove_html_tags(text):
    return re.sub(r'<.*?>', '', text)

# ===== Convert time SRT -> VTT =====
def convert_time_format(srt_time):
    # SRT: 00:00:01,000 --> 00:00:02,000
    return srt_time.replace(',', '.')

# ===== Convert SRT -> VTT =====
def srt_to_vtt(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("WEBVTT\n\n")

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Bỏ dòng index (1,2,3...)
            if line.isdigit():
                i += 1
                continue

            # Dòng time
            if '-->' in line:
                time_line = convert_time_format(line)
                f.write(time_line + '\n')
                i += 1

                # Nội dung subtitle
                while i < len(lines) and lines[i].strip() != "":
                    text = remove_html_tags(lines[i].strip())
                    f.write(text + '\n')
                    i += 1

                f.write('\n')
            else:
                i += 1

# ===== GUI chọn file =====
root = tk.Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Chọn file SRT",
    filetypes=[("SRT files", "*.srt")]
)

if not file_path:
    print("❌ Không chọn file!")
    exit()

# ===== Output file =====
output_path = os.path.splitext(file_path)[0] + ".vtt"

# ===== Convert =====
try:
    srt_to_vtt(file_path, output_path)
    print(f"✅ Convert thành công: {output_path}")
except Exception as e:
    print(f"❌ Lỗi: {e}")