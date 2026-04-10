import os
import shutil
import urllib.parse
import tkinter as tk
from tkinter import filedialog

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

def select_directory():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(initialdir=CURRENT_DIR, title="Chọn thư mục đích (Ví dụ: .../Movie)")
    return folder_path

def organize_files_from_source(base_dir):
    print(f"\n🚀 --- BẮT ĐẦU CHUYỂN FILE ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ Không tìm thấy nguồn: {SOURCE_DIR}")
        return

    for root_dir, dirs, files in os.walk(SOURCE_DIR):
        # Lấy tên thư mục con hiện tại (ví dụ: 'ep6')
        rel_dir = os.path.relpath(root_dir, SOURCE_DIR)
        
        # Đổi 'ep6' thành 'Ep6', nếu là thư mục gốc thì bỏ qua
        dest_sub_dir = rel_dir
        if rel_dir != "." and rel_dir.lower().startswith("ep"):
            dest_sub_dir = "Ep" + rel_dir[2:]
        elif rel_dir == ".":
            dest_sub_dir = ""

        # Tạo thư mục con ở đích
        current_dest_dir = os.path.join(base_dir, dest_sub_dir)
        if not os.path.exists(current_dest_dir):
            os.makedirs(current_dest_dir)

        for filename in files:
            src_full_path = os.path.join(root_dir, filename)
            dest_name = filename
            f_lower = filename.lower()

            # Đổi tên file m3u8
            if f_lower.endswith(".m3u8"):
                dest_name = "index_sv2.m3u8" if "sv2" in f_lower else "index.m3u8"

            dest_full_path = os.path.join(current_dest_dir, dest_name)

            if not os.path.exists(dest_full_path):
                shutil.copy2(src_full_path, dest_full_path)
                print(f"✅ [Copy] {filename} -> {os.path.relpath(dest_full_path, base_dir)}")

def update_playlist_files(base_dir, repo_sub_path):
    print(f"\n🛠️  --- CẬP NHẬT M3U8 ---")
    
    if not os.path.exists(base_dir):
        return

    # Quét qua từng thư mục con trong base_dir
    for root_dir, dirs, files in os.walk(base_dir):
        vtt_files = sorted([f for f in files if f.endswith('.vtt')])
        if not vtt_files:
            continue

        # Tính đường dẫn của thư mục con trên Github
        rel_dir = os.path.relpath(root_dir, base_dir)
        current_repo_path = repo_sub_path if rel_dir == "." else f"{repo_sub_path}{rel_dir.replace(os.sep, '/')}/"

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

        for filename in ["index.m3u8", "index_sv2.m3u8"]:
            file_path = os.path.join(root_dir, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            clean_lines = [l.strip() for l in content if "#EXT-X-MEDIA:TYPE=SUBTITLES" not in l]
            insert_idx = 1
            for i, line in enumerate(clean_lines):
                if line.startswith(("#EXT-X-VERSION", "#EXTM3U")):
                    insert_idx = i + 1

            final_str = "\n".join(clean_lines[:insert_idx] + new_media_lines + clean_lines[insert_idx:]) + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_str)
            print(f"📝 [Update] {os.path.relpath(file_path, base_dir)}")

if __name__ == "__main__":
    print("Đang mở hộp thoại chọn thư mục...")
    BASE_DIR = select_directory()
    
    if not BASE_DIR:
        print("⚠️ Bạn chưa chọn thư mục. Đã hủy!")
    else:
        try:
            rel_path = os.path.relpath(BASE_DIR, CURRENT_DIR)
            REPO_SUB_PATH = rel_path.replace("\\", "/") + "/"
        except ValueError:
            REPO_SUB_PATH = "" 

        print(f"📁 Thư mục đích: {BASE_DIR}")
        print(f"🔗 Path gốc trên Github: {REPO_SUB_PATH}")
        
        organize_files_from_source(BASE_DIR)
        update_playlist_files(BASE_DIR, REPO_SUB_PATH)
        print("\n✨ --- HOÀN TẤT ---")