import os
import shutil
import re
import urllib.parse

# --- CẤU HÌNH ---
SOURCE_DIR = os.path.join(os.getcwd(), "soucre")
BASE_DIR = os.path.join(os.getcwd(), "Phim TQ", "Bạch Nhật Đề Đăng - Love Beyond The Grave (2026)", "Season1")
GITHUB_BASE = "https://raw.githubusercontent.com/clowkhxu/cdnx/refs/heads/main/"
REPO_SUB_PATH = "Phim TQ/Bạch Nhật Đề Đăng - Love Beyond The Grave (2026)/Season1/"

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
}

def organize_files_from_source():
    print(f"\n--- BẮT ĐẦU PHÂN LOẠI FILE TỪ: {SOURCE_DIR} ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"[!] Bỏ qua: Không tìm thấy thư mục {SOURCE_DIR}")
        return

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)

    file_count = 0
    # os.walk quét đệ quy toàn bộ thư mục và thư mục con
    for root, dirs, files in os.walk(SOURCE_DIR):
        for filename in files:
            # Chỉ lấy các file bắt đầu bằng ep + số (vd: ep1.m3u8, ep3_vie_1.vtt)
            match = re.match(r'^(ep)(\d+)', filename, re.IGNORECASE)
            if not match:
                continue
            
            file_count += 1
            ep_prefix = match.group(0).lower() # chữ "ep1"
            ep_num = match.group(2) # số "1"
            
            # Tạo folder đích: Ep1, Ep2...
            target_ep_folder = f"Ep{ep_num}"
            target_ep_path = os.path.join(BASE_DIR, target_ep_folder)

            if not os.path.exists(target_ep_path):
                os.makedirs(target_ep_path)

            src_full_path = os.path.join(root, filename)
            dest_name = filename
            f_lower = filename.lower()

            # Đổi tên file m3u8
            if f_lower == f"{ep_prefix}.m3u8":
                dest_name = "index.m3u8"
            elif f_lower == f"{ep_prefix}_sv2.m3u8":
                dest_name = "index_sv2.m3u8"

            dest_full_path = os.path.join(target_ep_path, dest_name)

            if os.path.exists(dest_full_path):
                print(f"[~] Đã tồn tại: {target_ep_folder}/{dest_name}")
            else:
                shutil.copy2(src_full_path, dest_full_path) # Dùng copy thay vì move
                print(f"[+] Đã copy: {filename} -> {target_ep_folder}/{dest_name}")

    if file_count == 0:
        print("[!] Không tìm thấy bất kỳ file nào có tên bắt đầu bằng 'ep' bên trong soucre.")

def update_playlist_files():
    print(f"\n--- BẮT ĐẦU CẬP NHẬT M3U8 TẠI: {BASE_DIR} ---")
    if not os.path.exists(BASE_DIR):
        return

    subfolders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.lower().startswith('ep')])
    
    if not subfolders:
        print("[!] Không tìm thấy thư mục Ep nào để cập nhật.")
        return

    for ep_folder in subfolders:
        ep_path = os.path.join(BASE_DIR, ep_folder)
        vtt_files = sorted([f for f in os.listdir(ep_path) if f.endswith('.vtt')])
        
        if not vtt_files:
            continue
            
        new_media_lines = []
        for vtt in vtt_files:
            parts = vtt.split('_')
            if len(parts) < 2: continue
            code = parts[1]
            info = LANG_MAP.get(code, {"name": code.upper(), "lang": code, "default": "NO"})
            
            full_repo_path = f"{REPO_SUB_PATH}{ep_folder}/{vtt}"
            encoded_uri = GITHUB_BASE + urllib.parse.quote(full_repo_path)
            
            line = (f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",'
                    f'NAME="{info["name"]}",LANGUAGE="{info["lang"]}",'
                    f'DEFAULT={info["default"]},AUTOSELECT=YES,URI="{encoded_uri}"')
            new_media_lines.append(line)

        for filename in ["index.m3u8", "index_sv2.m3u8"]:
            file_path = os.path.join(ep_path, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                old_lines = f.readlines()

            clean_lines = [line.strip() for line in old_lines if "#EXT-X-MEDIA:TYPE=SUBTITLES" not in line]
            insert_idx = 1
            for i, line in enumerate(clean_lines):
                if line.startswith("#EXT-X-VERSION"):
                    insert_idx = i + 1
                    break
                elif line.startswith("#EXTM3U") and insert_idx == 1:
                    insert_idx = i + 1

            final_content = clean_lines[:insert_idx] + new_media_lines + clean_lines[insert_idx:]
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(final_content) + "\n")
            
        print(f"[+] Đã làm mới phụ đề cho: {ep_folder}")

if __name__ == "__main__":
    organize_files_from_source()
    update_playlist_files()
    print("\n--- HOÀN TẤT ---")