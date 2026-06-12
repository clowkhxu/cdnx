import concurrent.futures
import re
import requests

# Cấu hình
FILE_PATH = "playlist.txt"  # Thay bằng tên file txt của bạn
MAX_THREADS = 4  # Số lượng link kiểm tra đồng thời
TIMEOUT = 5  # Thời gian chờ phản hồi tối đa cho mỗi link (giây)


def extract_urls(file_path):
    """Đọc file và trích xuất tất cả các link URL."""
    urls = []
    # Regex để tìm các link HTTP/HTTPS
    url_pattern = re.compile(r"https?://[^\s|]+")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                # Loại bỏ các dòng filter hoặc tag M3U nếu không chứa link media
                if line.startswith("#") and "URI=" not in line:
                    continue

                # Tìm tất cả url trong dòng (xử lý được cả trường hợp phân tách bằng dấu |)
                found_urls = url_pattern.findall(line)
                for url in found_urls:
                    # Nếu link nằm trong tag URI="...", tiến hành làm sạch
                    clean_url = url.strip(' "')
                    if clean_url:
                        urls.append(clean_url)
    except FileNotFoundError:
        print(f"❌ Không tìm thấy file: {file_path}")

    # Loại bỏ các link trùng lặp (nếu có)
    return list(set(urls))


def check_url_status(url):
    """Kiểm tra trạng thái của một URL bằng phương thức HEAD (nhanh hơn GET)."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        # Dùng HEAD request để chỉ lấy header về check, tiết kiệm băng thông và thời gian
        response = requests.head(
            url, headers=headers, timeout=TIMEOUT, allow_redirects=True
        )

        # Nếu HEAD bị chặn (405 hoặc 403), thử lại bằng GET nhưng chỉ lấy vài byte đầu
        if response.status_code in [403, 405]:
            response = requests.get(
                url, headers=headers, timeout=TIMEOUT, stream=True
            )

        if response.status_code == 200:
            return url, True, response.status_code
        else:
            return url, False, response.status_code
    except requests.RequestException:
        return url, False, "Timeout/Error"


def main():
    print("🔍 Đang trích xuất link từ file...")
    urls = extract_urls(FILE_PATH)
    total_urls = len(urls)
    print(f"📋 Tìm thấy tổng cộng {total_urls} link cần kiểm tra.\n")

    live_urls = []
    dead_urls = []

    print("🚀 Đang tiến hành kiểm tra trạng thái các link...")
    # Sử dụng ThreadPoolExecutor để tăng tốc độ kiểm tra bằng đa luồng
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=MAX_THREADS
    ) as executor:
        results = executor.map(check_url_status, urls)

        for url, is_live, status in results:
            if is_live:
                print(f"🟩 [LIVE] [{status}] -> {url}")
                live_urls.append(url)
            else:
                print(f"🟥 [DEAD] [{status}] -> {url}")
                dead_urls.append(url)

    # Thống kê kết quả
    print("\n" + "=" * 50)
    print("📊 KẾT QUẢ KIỂM TRA:")
    print(f"✅ Link còn sống: {len(live_urls)}/{total_urls}")
    print(f"❌ Link đã chết: {len(dead_urls)}/{total_urls}")
    print("=" * 50)

    # Tùy chọn: Lưu các link còn sống ra một file mới
    if live_urls:
        with open("live_urls.txt", "w", encoding="utf-8") as f:
            for url in live_urls:
                f.write(url + "\n")
        print("💾 Đã lưu danh sách link còn sống vào file 'live_urls.txt'")


if __name__ == "__main__":
    main()