import subprocess
import re
import os

# ===== DANH SÁCH LINK (dán vào đây) =====
urls = """
http://download803.fshare.vn/dl/DoeqYVGMOQczxEw7IpJvNfoFIK2X15bmaM+YNQ11r+Oj++kENzb23Wp8eUO8MgDlTSvshiEFpRSNrmqV/Reverse.S01E01.ViE.1080p.WEB-DL.AAC2.0.H.264.mkv
http://download802.fshare.vn/dl/MYViQLl-cCQccyBskC563MB3G2jH32WIskCkUFSDzGiv9WCZnE+WpY3oiB30o-mTVX8JGYpCZarzLSzu/Reverse.S01E02.ViE.1080p.WEB-DL.AAC2.0.H.264.mkv
http://download802.fshare.vn/dl/gw+kXrikie-pAP3R0Nmcyp5poicIbOHJVNbyTmzdx5-FaYYycmUTmTV9q6ywUQqO76HlKDjqLFi99TcX/Reverse.S01E03.ViE.1080p.WEB-DL.AAC2.0.H.264%20%28FIX%29.mkv
""".strip().splitlines()

# ===== HÀM XÓA TAG HTML =====
def clean_vtt(file):
    if not os.path.exists(file):
        print(f"❌ Không tìm thấy file: {file}")
        return

    with open(file, "r", encoding="utf-8") as f:
        content = f.read()

    # xóa toàn bộ tag <...>
    content = re.sub(r'<[^>]+>', '', content)

    with open(file, "w", encoding="utf-8") as f:
        f.write(content)

# ===== LOOP XỬ LÝ =====
for i, url in enumerate(urls, start=1):
    output = f"ep{i}_vie.vtt"

    print(f"\n🎬 Đang xử lý: {output}")

    cmd = [
        "ffmpeg",
        "-y",                      # overwrite nếu có file cũ
        "-ss", "01:00:00",         # tăng tốc (có thể bỏ nếu không cần)
        "-i", url,
        "-map", "0:s:m:language:vie?",
        "-c:s", "webvtt",
        output
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✔ Extract xong, đang clean tag...")
        clean_vtt(output)
        print(f"✅ Hoàn tất: {output}")
    else:
        print(f"❌ Lỗi khi xử lý: {url}")

print("\n🚀 Xong toàn bộ!")