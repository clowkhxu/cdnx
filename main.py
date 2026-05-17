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
        return None, None, None

    intro_end = simpledialog.askstring(
        "Cấu hình Skip Intro", 
        "Nhập thời gian KẾT THÚC intro (giây).\nVí dụ: 90\n(Để trống nếu muốn giữ nguyên cấu hình cũ hoặc không thêm)",
        parent=root
    )
    
    # --- TÙY CHỌN VIETSUB / THUYẾT MINH / LỒNG TIẾNG ---
    audio_choice = simpledialog.askstring(
        "Cấu hình M3U8",
        "Chọn chế độ file M3U8 chính:\n1: Vietsub (Tạo file index.m3u8)\n2: Thuyết Minh (Tạo file epX_tm.m3u8)\n3: Lồng Tiếng (Tạo file epX_lt.m3u8)",
        parent=root
    )
    
    audio_mode = "VS" # Mặc định là Vietsub
    if audio_choice == "2":
        audio_mode = "TM"
    elif audio_choice == "3":
        audio_mode = "LT"
        
    return folder_path, intro_end, audio_mode

def organize_files_from_source(base_dir, audio_mode):
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

        # Trích xuất tiền tố tập (vd: 'ep1', 'ep2'). Nếu là phim lẻ thư mục gốc thì dùng 'index'
        ep_prefix = "index"
        if dest_sub_dir.lower().startswith("ep"):
            ep_prefix = dest_sub_dir.lower()

        for filename in files:
            src_full_path = os.path.join(root_dir, filename)
            dest_name = filename
            f_lower = filename.lower()

            # --- LOGIC ĐỔI TÊN MỚI (KHÔNG GHI ĐÈ FILE CHÍNH NẾU KHÁC LOẠI) ---
            if f_lower.endswith(".m3u8"):
                if "_audio" in f_lower:
                    # Nếu là file audio rời
                    if audio_mode == "TM":
                        dest_name = f_lower.replace("_audio", "_tm_audio")
                    elif audio_mode == "LT":
                        dest_name = f_lower.replace("_audio", "_lt_audio")
                    else:
                        dest_name = filename
                else:
                    # Nếu là file video CHÍNH
                    if audio_mode == "TM":
                        if "_sv2" in f_lower:
                            dest_name = f"{ep_prefix}_tm_sv2.m3u8"
                        else:
                            dest_name = f"{ep_prefix}_tm.m3u8"
                    elif audio_mode == "LT":
                        if "_sv2" in f_lower:
                            dest_name = f"{ep_prefix}_lt_sv2.m3u8"
                        else:
                            dest_name = f"{ep_prefix}_lt.m3u8"
                    else:
                        # Chế độ Vietsub -> dùng index như cũ
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
        # Tìm file audio (có chứa chữ audio)
        audio_files = sorted([f for f in files if f.endswith('.m3u8') and '_audio' in f.lower()])
        
        # Tìm các file M3U8 là file chính (không chứa chữ audio)
        main_playlists = [f for f in files if f.endswith('.m3u8') and '_audio' not in f.lower()]
        
        rel_dir = os.path.relpath(root_dir, base_dir)
        current_repo_path = repo_sub_path if rel_dir == "." else f"{repo_sub_path}{rel_dir.replace(os.sep, '/')}/"

        # --- 1. Tạo danh sách thẻ EXT-X-MEDIA cho SUBTITLES (Dùng chung) ---
        sub_media_lines = []
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
            sub_media_lines.append(line)

        # --- 2. Lặp qua TẤT CẢ các file M3U8 chính (index, ep1_tm, ep1_lt...) ---
        for filename in main_playlists:
            file_path = os.path.join(root_dir, filename)
            if not os.path.exists(file_path):
                continue

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.readlines()

            target_duration = "10" 
            media_sequence = "0"  
            preserved_segments = []
            existing_media = {} 
            existing_intro = None

            for line in content:
                line = line.strip()
                if not line:
                    continue
                
                if "#EXT-X-TARGETDURATION" in line:
                    target_duration = line.split(":")[-1]
                elif "#EXT-X-MEDIA-SEQUENCE" in line:
                    media_sequence = line.split(":")[-1]
                elif line.startswith("#EXT-X-MEDIA:TYPE="):
                    uri_match = re.search(r'URI="([^"]+)"', line)
                    if uri_match:
                        existing_media[uri_match.group(1)] = line
                    else:
                        existing_media[line] = line
                elif line.startswith("#EXT-X-INTRO"):
                    existing_intro = line
                elif line.startswith("#EXTINF") or (not line.startswith("#") and line) or line.startswith("#EXT-X-ENDLIST"):
                    preserved_segments.append(line)

            # --- 3. Gắn thêm thẻ AUDIO (nếu có file audio rời) ---
            is_sv2_playlist = "_sv2" in filename.lower()
            current_new_media = list(sub_media_lines) # Gắn luôn sub cho file m3u8
            
            for aud in audio_files:
                is_sv2_audio = "_sv2" in aud.lower()
                
                # Cùng là sv1 hoặc cùng là sv2 thì mới gắn vào
                if is_sv2_playlist == is_sv2_audio:
                    full_repo_path = f"{current_repo_path}{aud}".replace("//", "/")
                    encoded_uri = GITHUB_BASE + urllib.parse.quote(full_repo_path)
                    
                    audio_name = "Thuyết Minh VN" 
                    if "_tm" in aud.lower() or "_tm" in filename.lower():
                        audio_name = "Thuyết Minh"
                    elif "_lt" in aud.lower() or "_lt" in filename.lower():
                        audio_name = "Lồng Tiếng"

                    group_id = 'audio-group-sv2' if is_sv2_playlist else 'audio-group'
                    line = (f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="{group_id}",'
                            f'NAME="{audio_name}",LANGUAGE="vi",'
                            f'DEFAULT=YES,AUTOSELECT=YES,URI="{encoded_uri}"')
                    current_new_media.append(line)

            # --- 4. Gộp Media mới vào Media cũ (chống trùng lặp bằng URI) ---
            for new_line in current_new_media:
                uri_match = re.search(r'URI="([^"]+)"', new_line)
                if uri_match:
                    existing_media[uri_match.group(1)] = new_line 
                else:
                    existing_media[new_line] = new_line

            # --- 5. XÂY DỰNG LẠI HEADER ---
            header = [
                "#EXTM3U",
                "#EXT-X-VERSION:3",
                f"#EXT-X-TARGETDURATION:{target_duration}",
                f"#EXT-X-MEDIA-SEQUENCE:{media_sequence}"
            ]
            
            header.extend(list(existing_media.values()))
            
            if intro_end and intro_end.strip().isdigit():
                header.append(f"#EXT-X-INTRO:START=0,END={intro_end.strip()}")
            elif existing_intro:
                header.append(existing_intro)
            
            header.append("#EXT-X-PLAYLIST-TYPE:VOD")

            # --- 6. Ghi lại file ---
            final_content = "\n".join(header + preserved_segments) + "\n"
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
                
            media_count = len(existing_media)
            print(f"📝 [Update] {os.path.relpath(file_path, base_dir)} (Nhúng thành công {media_count} tracks HLS)")

if __name__ == "__main__":
    print("--- Tool Xử Lý M3U8 (Subtitles & Audio) ---")
    BASE_DIR, INTRO_END, AUDIO_MODE = get_user_inputs()
    
    if not BASE_DIR:
        print("⚠️ Bạn chưa chọn thư mục. Đã hủy!")
    else:
        try:
            rel_path = os.path.relpath(BASE_DIR, CURRENT_DIR)
            REPO_SUB_PATH = "" if rel_path == "." else rel_path.replace("\\", "/") + "/"
        except ValueError:
            REPO_SUB_PATH = "" 

        print(f"📁 Thư mục đích: {BASE_DIR}")
        
        organize_files_from_source(BASE_DIR, AUDIO_MODE)
        update_playlist_files(BASE_DIR, REPO_SUB_PATH, INTRO_END)
        print("\n✨ --- HOÀN TẤT ---")