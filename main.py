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
        "Nhập thời gian KẾT THÚC intro (giây).\nVí dụ: 90\n(Để trống nếu không muốn thêm thẻ này)",
        parent=root
    )
    
    return folder_path, intro_end

def organize_files_from_source(base_dir):
    print(f"\n🚀 --- BẮT ĐẦU CHUYỂN FILE & ĐỔI TÊN ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ Không tìm thấy nguồn: {SOURCE_DIR}")
        return

    for root_dir, dirs, files in os.walk(SOURCE_DIR):
        rel_dir = os.path.relpath(root_dir, SOURCE_DIR)
        
        # Xử lý tên thư mục đích (Ep1, Ep2...)
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

            # Logic đổi tên file m3u8: ep1.m3u8 -> index.m3u8, ep1_sv2.m3u8 -> index_sv2.m3u8
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
        # Lấy danh sách file vtt trong thư mục hiện tại
        vtt_files = sorted([f for f in files if f.endswith('.vtt')])
        
        rel_dir = os.path.relpath(root_dir, base_dir)
        # Đường dẫn tương đối phục vụ URL Github
        current_repo_path = repo_sub_path if rel_dir == "." else f"{repo_sub_path}{rel_dir.replace(os.sep, '/')}/"

        # 1. Tạo danh sách các dòng Subtitle
        new_media_lines = []
        for vtt in vtt_files:
            code = "unknown"
            for key in LANG_MAP:
                # Tìm mã ngôn ngữ trong tên file vtt (ví dụ: ep1_vie_4.vtt -> vie)
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

        # 2. Xử lý các file index.m3u8 và index_sv2.m3u8
        for filename in ["index.m3u8", "index_sv2.m3u8"]:
            file_path = os.path.join(root_dir, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            # Chỉ giữ lại các dòng chứa thông tin segment video (EXTINF và file .ts hoặc link video)
            # Loại bỏ toàn bộ Header cũ để ghi đè mới
            preserved_segments = []
            is_collecting = False
            for line in content:
                line = line.strip()
                if line.startswith("#EXTINF") or (not line.startswith("#") and line):
                    preserved_segments.append(line)
                elif line.startswith("#EXT-X-ENDLIST"):
                    preserved_segments.append(line)

            # 3. Xây dựng cấu trúc file mới
            header = [
                "#EXTM3U",
                "#EXT-X-VERSION:3"
            ]
            
            # Thêm các dòng subtitle
            header.extend(new_media_lines)
            
            # Thêm cấu hình Skip Intro nếu có
            if intro_end and intro_end.strip().isdigit():
                header.append(f"#EXT-X-INTRO:START=0,END={intro_end.strip()}")
            
            # Thêm dòng VOD type
            header.append("#EXT-X-PLAYLIST-TYPE:VOD")

            # Kết hợp Header và Segments
            final_content = "\n".join(header + preserved_segments) + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            print(f"📝 [Update] {os.path.relpath(file_path, base_dir)} ({len(new_media_lines)} subs added)")

if __name__ == "__main__":
    print("--- Tool Xử Lý M3U8 & Subtitles ---")
    BASE_DIR, INTRO_END = get_user_inputs()
    
    if not BASE_DIR:
        print("⚠️ Bạn chưa chọn thư mục. Đã hủy!")
    else:
        try:
            # Tính toán path tương đối so với file script để làm path trên Github
            # Giả định folder chứa script là root của repo (hoặc tương đương)
            # Nếu script nằm ngoài repo, bạn có thể cần chỉnh lại logic REPO_SUB_PATH
            rel_path = os.path.relpath(BASE_DIR, CURRENT_DIR)
            if rel_path == ".":
                REPO_SUB_PATH = ""
            else:
                REPO_SUB_PATH = rel_path.replace("\\", "/") + "/"
        except ValueError:
            REPO_SUB_PATH = "" 

        print(f"📁 Thư mục đích: {BASE_DIR}")
        print(f"🔗 Base Path: {REPO_SUB_PATH}")
        
        organize_files_from_source(BASE_DIR)
        update_playlist_files(BASE_DIR, REPO_SUB_PATH, INTRO_END)
        print("\n✨ --- HOÀN TẤT ---")