import os
import urllib.parse

# --- CẤU HÌNH ---
# Script tự tìm folder Season1 dựa trên vị trí file main.py
BASE_DIR = os.path.join(os.getcwd(), "Phim TQ", "Em Là Niềm Vui Đến Muộn - You Are My Fateful Love (2026)", "Season1")
GITHUB_BASE = "https://raw.githubusercontent.com/clowkhxu/cdnx/refs/heads/main/"
REPO_SUB_PATH = "Phim TQ/Em Là Niềm Vui Đến Muộn - You Are My Fateful Love (2026)/Season1/"

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

def update_playlist_files():
    if not os.path.exists(BASE_DIR):
        print(f"Lỗi: Không tìm thấy thư mục tại {BASE_DIR}")
        return

    # Lấy danh sách các thư mục Ep1, Ep2...
    subfolders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.lower().startswith('ep')])

    for ep_folder in subfolders:
        ep_path = os.path.join(BASE_DIR, ep_folder)
        vtt_files = sorted([f for f in os.listdir(ep_path) if f.endswith('.vtt')])
        
        if not vtt_files:
            continue
            
        target_files = ["index.m3u8", "index_sv2.m3u8"]
        for filename in target_files:
            file_path = os.path.join(ep_path, filename)
            if not os.path.exists(file_path):
                continue

            # Đọc nội dung hiện tại của file
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            lines = content.splitlines()
            new_media_lines = []

            for vtt in vtt_files:
                # Tạo URI để kiểm tra sự tồn tại
                full_repo_path = f"{REPO_SUB_PATH}{ep_folder}/{vtt}"
                encoded_uri = GITHUB_BASE + urllib.parse.quote(full_repo_path)
                
                # CHỈ THÊM NẾU URI CHƯA CÓ TRONG FILE
                if encoded_uri not in content:
                    parts = vtt.split('_')
                    if len(parts) < 2: continue
                    code = parts[1]
                    info = LANG_MAP.get(code, {"name": code.upper(), "lang": code, "default": "NO"})
                    
                    line = (f'#EXT-X-MEDIA:TYPE=SUBTITLES,GROUP-ID="subs",'
                            f'NAME="{info["name"]}",LANGUAGE="{info["lang"]}",'
                            f'DEFAULT={info["default"]},AUTOSELECT=YES,URI="{encoded_uri}"')
                    new_media_lines.append(line)

            # Nếu không có phụ đề mới thì bỏ qua file này
            if not new_media_lines:
                continue

            # Tìm vị trí chèn (sau dòng #EXT-X-VERSION hoặc #EXTM3U)
            insert_idx = 1
            for i, line in enumerate(lines):
                if line.startswith("#EXT-X-VERSION"):
                    insert_idx = i + 1
                    break
                elif line.startswith("#EXTM3U") and insert_idx == 1:
                    insert_idx = i + 1

            # Chèn các dòng mới vào list
            final_lines = lines[:insert_idx] + new_media_lines + lines[insert_idx:]

            # Ghi lại file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(final_lines) + "\n")
            
            print(f"--- Đã thêm {len(new_media_lines)} sub mới vào {ep_folder}/{filename}")

    print("Hoàn tất kiểm tra và cập nhật.")

if __name__ == "__main__":
    update_playlist_files()