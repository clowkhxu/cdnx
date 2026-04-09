import os
import shutil
import urllib.parse

# --- CẤU HÌNH ---
SOURCE_DIR = os.path.join(os.getcwd(), "soucre")
BASE_DIR = os.path.join(os.getcwd(), "Phim ÂM", "Bóng ma Anh Quốc - Peaky Blinders", "Movie")
GITHUB_BASE = "https://raw.githubusercontent.com/clowkhxu/cdnx/refs/heads/main/"
REPO_SUB_PATH = "Phim ÂM/Bóng ma Anh Quốc - Peaky Blinders/Movie/"

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

def organize_files_from_source():
    print(f"\n🚀 --- BẮT ĐẦU CHUYỂN FILE ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️ Không tìm thấy nguồn: {SOURCE_DIR}")
        return

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    for root, dirs, files in os.walk(SOURCE_DIR):
        for filename in files:
            src_full_path = os.path.join(root, filename)
            dest_name = filename
            f_lower = filename.lower()

            # Đổi tên m3u8
            if f_lower.endswith(".m3u8"):
                dest_name = "index_sv2.m3u8" if "sv2" in f_lower else "index.m3u8"

            dest_full_path = os.path.join(BASE_DIR, dest_name)

            if not os.path.exists(dest_full_path):
                shutil.copy2(src_full_path, dest_full_path)
                print(f"✅ [Copy] {filename} -> {os.path.basename(BASE_DIR)}/{dest_name}")

def update_playlist_files():
    print(f"\n🛠️  --- CẬP NHẬT M3U8 ---")
    
    if not os.path.exists(BASE_DIR):
        return

    vtt_files = sorted([f for f in os.listdir(BASE_DIR) if f.endswith('.vtt')])
    if not vtt_files:
        print("⚠️ Không có file .vtt nào để cập nhật.")
        return

    new_media_lines = []
    for vtt in vtt_files:
        code = "unknown"
        for key in LANG_MAP:
            if f"_{key}_" in f"_{vtt.lower()}_" or vtt.lower().startswith(f"{key}_"):
                code = key
                break
        
        info = LANG_MAP.get(code, {"name": code.upper(), "lang": code, "default": "NO"})
        
        # Tạo link trực tiếp tới repo
        full_repo_path = f"{REPO_SUB_PATH}{vtt}".replace("//", "/")
        encoded_uri = GITHUB_BASE + urllib.parse.quote(full_repo_path)
        
        line = (f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",'
                f'NAME="{info["name"]}",LANGUAGE="{info["lang"]}",'
                f'DEFAULT={info["default"]},AUTOSELECT=YES,URI="{encoded_uri}"')
        new_media_lines.append(line)

    # Chèn vào các file index.m3u8
    for filename in ["index.m3u8", "index_sv2.m3u8"]:
        file_path = os.path.join(BASE_DIR, filename)
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
        print(f"📝 [Update] {os.path.basename(BASE_DIR)}/{filename}")

if __name__ == "__main__":
    organize_files_from_source()
    update_playlist_files()
    print("\n✨ --- HOÀN TẤT ---")