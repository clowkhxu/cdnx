import os
import urllib.parse

# --- CẤU HÌNH ---
# Script tự tìm folder Season1 dựa trên folder chứa phim hiện tại của bạn
BASE_DIR = os.path.join(os.getcwd(), "Phim TQ", "Tôi Ở Đại Học Tu Sửa Văn Vật - Glaze of Love (2026)", "Season1")

# URL gốc của Github
GITHUB_BASE = "https://raw.githubusercontent.com/clowkhxu/cdnx/refs/heads/main/"

# Đường dẫn tương đối trong Repo (Hãy sửa tên phim ở đây nếu bạn đổi sang phim khác)
REPO_SUB_PATH = "Phim TQ/Tôi Ở Đại Học Tu Sửa Văn Vật - Glaze of Love (2026)/Season1/"

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

    # Quét các thư mục Ep1, Ep2...
    subfolders = sorted([d for d in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, d)) and d.lower().startswith('ep')])

    for ep_folder in subfolders:
        ep_path = os.path.join(BASE_DIR, ep_folder)
        vtt_files = sorted([f for f in os.listdir(ep_path) if f.endswith('.vtt')])
        
        if not vtt_files:
            continue
            
        # 1. Tạo danh sách phụ đề MỚI từ các file thực tế trong folder
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

        # 2. Xử lý cập nhật file m3u8
        target_files = ["index.m3u8", "index_sv2.m3u8"]
        for filename in target_files:
            file_path = os.path.join(ep_path, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                old_lines = f.readlines()

            # Lọc bỏ hoàn toàn các dòng phụ đề cũ (Xóa hết để viết lại mới)
            clean_lines = [line.strip() for line in old_lines if "#EXT-X-MEDIA:TYPE=SUBTITLES" not in line]

            # Tìm vị trí để chèn phụ đề (ngay sau #EXT-X-VERSION hoặc #EXTM3U)
            insert_idx = 1
            for i, line in enumerate(clean_lines):
                if line.startswith("#EXT-X-VERSION"):
                    insert_idx = i + 1
                    break
                elif line.startswith("#EXTM3U") and insert_idx == 1:
                    insert_idx = i + 1

            # Ghép nội dung: [Phần đầu] + [Phụ đề mới] + [Phần nội dung video còn lại]
            final_content = clean_lines[:insert_idx] + new_media_lines + clean_lines[insert_idx:]

            # Ghi đè lại file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(final_content) + "\n")
            
        print(f"Đã làm mới phụ đề cho: {ep_folder}")

if __name__ == "__main__":
    update_playlist_files()