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
    print(f"\n🚀 --- BẮT ĐẦU PHÂN LOẠI FILE TỪ: {SOURCE_DIR} ---")
    if not os.path.exists(SOURCE_DIR):
        print(f"⚠️  Bỏ qua: Không tìm thấy thư mục nguồn '{SOURCE_DIR}'")
        return

    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        print(f"📂 Đã tạo thư mục gốc: {BASE_DIR}")

    file_count = 0
    for root, dirs, files in os.walk(SOURCE_DIR):
        for filename in files:
            match = re.match(r'^(ep)(\d+)', filename, re.IGNORECASE)
            if not match:
                continue
            
            file_count += 1
            ep_num = match.group(2)
            ep_prefix = match.group(1).lower() + ep_num
            
            target_ep_folder = f"Ep{ep_num}"
            target_ep_path = os.path.join(BASE_DIR, target_ep_folder)

            # Log khi tạo folder Ep mới
            if not os.path.exists(target_ep_path):
                os.makedirs(target_ep_path)
                print(f"🆕 [Folder] Đã tạo thư mục mới: {target_ep_folder}")

            src_full_path = os.path.join(root, filename)
            dest_name = filename
            f_lower = filename.lower()

            if f_lower == f"{ep_prefix}.m3u8":
                dest_name = "index.m3u8"
            elif f_lower == f"{ep_prefix}_sv2.m3u8":
                dest_name = "index_sv2.m3u8"

            dest_full_path = os.path.join(target_ep_path, dest_name)

            if os.path.exists(dest_full_path):
                print(f"🔍 [Skip] Đã có sẵn: {target_ep_folder}/{dest_name} (Giữ nguyên)")
            else:
                shutil.copy2(src_full_path, dest_full_path)
                print(f"✅ [Copy] Thành công: {filename} -> {target_ep_folder}/{dest_name}")

    if file_count == 0:
        print("⚠️  Không tìm thấy file hợp lệ (ep*) để xử lý.")

def update_playlist_files():
    print(f"\n🛠️  --- CẬP NHẬT NỘI DUNG PLAYLIST TẠI: {BASE_DIR} ---")
    if not os.path.exists(BASE_DIR):
        return

    subfolders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.lower().startswith('ep')])
    
    if not subfolders:
        print("⚠️  Không thấy thư mục Ep nào để cập nhật nội dung.")
        return

    for ep_folder in subfolders:
        ep_path = os.path.join(BASE_DIR, ep_folder)
        vtt_files = sorted([f for f in os.listdir(ep_path) if f.endswith('.vtt')])
        
        if not vtt_files:
            print(f"ℹ️  [Info] {ep_folder}: Không có file phụ đề .vtt, bỏ qua cập nhật M3U8.")
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

        updated_any = False
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
            new_content_str = "\n".join(final_content) + "\n"

            # Kiểm tra xem nội dung có thực sự thay đổi không để log
            with open(file_path, "r", encoding="utf-8") as f:
                current_content = f.read()

            if new_content_str == current_content:
                print(f"🆗 [Steady] {ep_folder}/{filename}: Cấu trúc phụ đề đã chuẩn, không cần ghi đè.")
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content_str)
                updated_any = True

        if updated_any:
            print(f"📝 [Update] Đã làm mới link phụ đề cho: {ep_folder}")

if __name__ == "__main__":
    organize_files_from_source()
    update_playlist_files()
    print("\n✨ --- TẤT CẢ CÔNG VIỆC ĐÃ HOÀN TẤT ---")