import http.server
import socketserver
import requests
import re
from urllib.parse import urljoin, urlparse

PORT = 8080
SECRET_KEY = b"AntiScanKey2026"
ENCRYPT_SIZE = 2048

def get_ts_offset(data):
    # Tìm kiếm ký tự IEND để xác định offset giống như trong Worker JS
    max_search = min(len(data), 300)
    for i in range(max_search - 3):
        if data[i] == 0x49 and data[i+1] == 0x45 and data[i+2] == 0x4e and data[i+3] == 0x44:
            return i + 8
    return 70

def decrypt_ts_data(chunk):
    offset = get_ts_offset(chunk)
    if len(chunk) <= offset:
        return chunk
    
    ts_part = chunk[offset:]
    if len(ts_part) <= 4:
        return ts_part

    # Lấy kích thước dữ liệu thực tế (4 byte đầu)
    data_size = int.from_bytes(ts_part[0:4], byteorder='big')
    
    # Cắt lấy phần data bị mã hóa
    encrypted_data = bytearray(ts_part[4:4+data_size])
    key_len = len(SECRET_KEY)

    # Chế độ Fast Mode kiểm tra ký tự 0x47 (Sync byte của liên kết TS)
    is_fast_mode = False
    if data_size > 2256:
        if encrypted_data[2068] == 0x47 and encrypted_data[2256] == 0x47:
            is_fast_mode = True

    if is_fast_mode:
        # Chỉ giải mã phần đầu ENCRYPT_SIZE
        limit = min(data_size, ENCRYPT_SIZE)
        for i in range(limit):
            encrypted_data[i] ^= SECRET_KEY[i % key_len]
    else:
        # Giải mã toàn bộ
        for i in range(data_size):
            encrypted_data[i] ^= SECRET_KEY[i % key_len]

    return bytes(encrypted_data)

class DecryptProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Trích xuất link m3u8 thật từ tham số truyền vào proxy
        # Định dạng: http://127.0.0.1:8080/?url=LInK_M3U8_CUA_BAN
        path_url = self.path
        if "?url=" not in path_url:
            self.send_error(400, "Thừa hoặc thiếu tham số ?url=")
            return
            
        target_url = path_url.split("?url=")[1]
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        # Trường hợp 1: VLC yêu cầu file Playlist (.m3u8)
        if ".m3u8" in target_url.split('?')[0].lower():
            res = requests.get(target_url, headers=headers)
            if res.status_code != 200:
                self.send_error(res.status_code)
                return

            text = res.text
            lines = text.splitlines()
            new_lines = []
            parts = []

            # Xử lý gộp dòng #EXT-X-PART giống hệt như logic CustomPlaylistLoader của bạn
            for line in lines:
                line_str = line.strip()
                if line_str.startswith('#EXT-X-PART:'):
                    parts.append(line_str[12:])
                elif (line_str.startswith('http') or '.ts' in line_str.lower()) and len(parts) > 0:
                    # Tạo đường dẫn tuyệt đối cho ts/part nếu nó là đường dẫn tương đối
                    full_ts_url = urljoin(target_url, line_str) if not line_str.startswith('http') else line_str
                    # Biến đổi link ts này đi qua proxy tiếp
                    new_lines.append(f"http://127.0.0.1:{PORT}/?url={full_ts_url}")
                    parts = []
                elif line_str != '':
                    # Nếu dòng đó là link segment thông thường (không có part)
                    if line_str.startswith('http'):
                        new_lines.append(f"http://127.0.0.1:{PORT}/?url={line_str}")
                    elif '.ts' in line_str.lower() or '.mp4' in line_str.lower():
                        full_url = urljoin(target_url, line_str)
                        new_lines.append(f"http://127.0.0.1:{PORT}/?url={full_url}")
                    else:
                        new_lines.append(line_str)

            response_data = "\n".join(new_lines).encode('utf-8')
            
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response_data)

        # Trường hợp 2: VLC yêu cầu tải các phân đoạn Video (.ts hoặc chuỗi | từ gộp part)
        else:
            # Nếu chuỗi url chứa dấu "|" (do gộp part), proxy cần tải lần lượt và nối lại
            urls = [u.strip() for u in target_url.split("|") if u.strip()]
            combined_raw = bytearray()

            try:
                for u in urls:
                    r = requests.get(u, headers=headers, timeout=10)
                    if r.status_code == 200:
                        combined_raw.extend(r.content)
                
                # Tiến hành giải mã luồng TS vừa gộp xong
                decrypted_data = decrypt_ts_data(combined_raw)
                
                self.send_response(200)
                self.send_header("Content-Type", "video/mp2t")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(decrypted_data)
            except Exception as e:
                self.send_error(500, f"Proxy Error: {str(e)}")

# Chạy Server Proxy
with socketserver.TCPServer(("127.0.0.1", PORT), DecryptProxyHandler) as httpd:
    print(f"=== KHỞI CHẠY PROXY GIẢI MÃ VIDEO TẠI PORT {PORT} ===")
    print(f"Để xem phim trên VLC, hãy copy và mở đường dẫn sau:")
    print(f"http://127.0.0.1:{PORT}/?url=NHAP_LINK_M3U8_GOC_VAO_DAY")
    print("=====================================================")
    httpd.serve_forever()