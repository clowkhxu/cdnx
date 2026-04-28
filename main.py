import os
import shutil
import urllib.parse
import tkinter as tk
from tkinter import filedialog, simpledialog
import re

# --- CẤU HÌNH ---
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(CURRENT_DIR, "soucre")
GITHUB_BASE = "https://raw.githubusercontent.com/clowkhxu/cdnx/refs/heads/main/"

LANG_MAP = {
    "vie": {"name": "Vietnamese", "lang": "vi", "default": "YES"},
    "eng": {"name": "English", "lang": "en", "default": "NO"},
    "chi": {"name": "Chinese", "lang": "zh", "default": "NO"},
    "tha": {"name": "Thai", "lang": "th", "default": "NO"},
    "jpn": {"name": "Japanese", "lang": "ja", "default": "NO"},
    "kor": {"name": "Korean", "lang": "ko", "default": "NO"},
    "fil": {"name": "Filipino", "lang": "fil", "default": "NO"},
    "fre": {"name": "French", "lang": "fr", "default": "NO"},
    "ger": {"name": "German", "lang": "de", "default": "NO"},
    "ind": {"name": "Indonesian", "lang": "id", "default": "NO"},
    "ita": {"name": "Italian", "lang": "it", "default": "NO"},
    "may": {"name": "Malay", "lang": "ms", "default": "NO"},
    "por": {"name": "Portuguese", "lang": "pt", "default": "NO"},
    "rus": {"name": "Russian", "lang": "ru", "default": "NO"},
    "spa": {"name": "Spanish", "lang": "es", "default": "NO"},
    "swa": {"name": "Swahili", "lang": "sw", "default": "NO"},
    "ukr": {"name": "Ukrainian", "lang": "uk", "default": "NO"},
    "tur": {"name": "Turkish", "lang": "tr", "default": "NO"},
    "rum": {"name": "Romanian", "lang": "ro", "default": "NO"},
    "nob": {"name": "Norwegian", "lang": "no", "default": "NO"},
    "swe": {"name": "Swedish", "lang": "sv", "default": "NO"},
}

def get_user_inputs():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    folder_path = filedialog.askdirectory(initialdir=CURRENT_DIR, title="Chọn thư mục đích (Ví dụ: .../Movie)")
    if not folder_path:
        return None, None

    intro_end = simpledialog.askstring(
        "Cấu hình Skip Intro", 
        "Nhập thời gian KẾT THÚC intro (giây).\nVí dụ: 90\n(Để trống nếu muốn giữ nguyên cấu hình cũ hoặc không thêm)",
        parent=root
    )
    
    return folder_path, intro_end

def organize_files_from_source(base_dir):
    print(f"\n🚀 --- BẮT ĐẦU CHUYỂN FILE & ĐỔI TÊN ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ Không tìm thấy nguồn: {SOURCE_DIR} (Sẽ bỏ qua bước copy, chuyển sang cập nhật M3U8)")
        return

    for root_dir, dirs, files in os.walk(SOURCE_DIR):
        rel_dir = os.path.relpath(root_dir, SOURCE_DIR)
        
        dest_sub_dir = rel_dir
        if rel_dir != "." and rel_dir.lower().startswith("ep"):
            dest_sub_dir = "Ep" + rel_dir[2:]
        elif rel_dir == ".":
            dest_sub_dir = ""

        current_dest_dir = os.path.join(base_dir, dest_sub_dir)
        if not os.path.exists(current_dest_dir):
            os.makedirs(current_dest_dir)

        for filename in files:
            src_full_path = os.path.join(root_dir, filename)
            dest_name = filename
            f_lower = filename.lower()

            if f_lower.endswith(".m3u8"):
                if "_sv2" in f_lower:
                    dest_name = "index_sv2.m3u8"
                else:
                    dest_name = "index.m3u8"

            dest_full_path = os.path.join(current_dest_dir, dest_name)
            shutil.copy2(src_full_path, dest_full_path)
            print(f"✅ [Copy/Rename] {filename} -> {os.path.relpath(dest_full_path, base_dir)}")

def update_playlist_files(base_dir, repo_sub_path, intro_end):
    print(f"\n🛠️  --- CẬP NHẬT NỘI DUNG M3U8 ---")
    
    if not os.path.exists(base_dir):
        return

    for root_dir, dirs, files in os.walk(base_dir):
        vtt_files = sorted([f for f in files if f.endswith('.vtt')])
        rel_dir = os.path.relpath(root_dir, base_dir)
        current_repo_path = repo_sub_path if rel_dir == "." else f"{repo_sub_path}{rel_dir.replace(os.sep, '/')}/"

        # --- 1. Tạo danh sách sub mới từ file .vtt hiện có ---
        new_media_lines = []
        for vtt in vtt_files:
            code = "unknown"
            for key in LANG_MAP:
                if f"_{key}_" in f"_{vtt.lower()}_" or vtt.lower().startswith(f"{key}_"):
                    code = key
                    break
            
            info = LANG_MAP.get(code, {"name": code.upper(), "lang": code, "default": "NO"})
            full_repo_path = f"{current_repo_path}{vtt}".replace("//", "/")
            encoded_uri = GITHUB_BASE + urllib.parse.quote(full_repo_path)
            
            line = (f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",'
                    f'NAME="{info["name"]}",LANGUAGE="{info["lang"]}",'
                    f'DEFAULT={info["default"]},AUTOSELECT=YES,URI="{encoded_uri}"')
            new_media_lines.append(line)

        # --- 2. Kiểm tra và cập nhật file m3u8 ---
        for filename in ["index.m3u8", "index_sv2.m3u8"]:
            file_path = os.path.join(root_dir, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            target_duration = "10" 
            media_sequence = "0"  
            preserved_segments = []
            
            # Lưu trữ Sub và Intro cũ để không bị mất/trùng lặp
            existing_subs = {} 
            existing_intro = None

            for line in content:
                line = line.strip()
                if not line:
                    continue
                
                if "#EXT-X-TARGETDURATION" in line:
                    target_duration = line.split(":")[-1]
                elif "#EXT-X-MEDIA-SEQUENCE" in line:
                    media_sequence = line.split(":")[-1]
                elif line.startswith("#EXT-X-MEDIA:TYPE=SUBTITLES"):
                    # Tách lấy URI để làm key (kiểm tra trùng lặp)
                    uri_match = re.search(r'URI="([^"]+)"', line)
                    if uri_match:
                        existing_subs[uri_match.group(1)] = line
                    else:
                        existing_subs[line] = line # Fallback
                elif line.startswith("#EXT-X-INTRO"):
                    existing_intro = line
                elif line.startswith("#EXTINF") or (not line.startswith("#") and line) or line.startswith("#EXT-X-ENDLIST"):
                    preserved_segments.append(line)

            # --- 3. Gộp Sub mới vào Sub cũ (chống trùng lặp bằng URI) ---
            for new_line in new_media_lines:
                uri_match = re.search(r'URI="([^"]+)"', new_line)
                if uri_match:
                    existing_subs[uri_match.group(1)] = new_line # Thêm mới hoặc ghi đè nếu trùng URI
                else:
                    existing_subs[new_line] = new_line

            # --- 4. XÂY DỰNG LẠI HEADER ---
            header = [
                "#EXTM3U",
                "#EXT-X-VERSION:3",
                f"#EXT-X-TARGETDURATION:{target_duration}",
                f"#EXT-X-MEDIA-SEQUENCE:{media_sequence}"
            ]
            
            # Thêm danh sách Sub đã được lọc trùng lặp
            header.extend(list(existing_subs.values()))
            
            # Xử lý Skip Intro: Nếu có nhập số mới -> Dùng mới. Nếu bỏ trống -> Giữ lại intro cũ (nếu có)
            if intro_end and intro_end.strip().isdigit():
                header.append(f"#EXT-X-INTRO:START=0,END={intro_end.strip()}")
            elif existing_intro:
                header.append(existing_intro)
            
            header.append("#EXT-X-PLAYLIST-TYPE:VOD")

            # --- 5. Ghi lại file ---
            final_content = "\n".join(header + preserved_segments) + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            print(f"📝 [Update] {os.path.relpath(file_path, base_dir)} (Duration: {target_duration}, Seq: {media_sequence}, Subs: {len(existing_subs)})")

if __name__ == "__main__":
    print("--- Tool Xử Lý M3U8 & Subtitles ---")
    BASE_DIR, INTRO_END = get_user_inputs()
    
    if not BASE_DIR:
        print("⚠️ Bạn chưa chọn thư mục. Đã hủy!")
    else:
        try:
            rel_path = os.path.relpath(BASE_DIR, CURRENT_DIR)
            REPO_SUB_PATH = "" if rel_path == "." else rel_path.replace("\\", "/") + "/"
        except ValueError:
            REPO_SUB_PATH = "" 

        print(f"📁 Thư mục đích: {BASE_DIR}")
        
        organize_files_from_source(BASE_DIR)
        update_playlist_files(BASE_DIR, REPO_SUB_PATH, INTRO_END)
        print("\n✨ --- HOÀN TẤT ---")