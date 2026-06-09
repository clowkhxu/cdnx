import os
import re
import subprocess

def parse_prefix(user_input):
    """
    Hàm này dùng để tách phần chữ và phần số của tập phim.
    Ví dụ: 'ep1_vie_56' -> tiền tố là 'ep', số tập là 1, hậu tố là '_vie_56'
    """
    # Tìm số đầu tiên xuất hiện trong chuỗi nhập vào
    match = re.search(r'\d+', user_input)
    if not match:
        return user_input, None, ""
    
    start_idx, end_idx = match.span()
    prefix = user_input[:start_idx]
    current_num = int(match.group())
    suffix = user_input[end_idx:]
    
    # Lấy ra độ dài số để giữ lại định dạng (ví dụ ep01 thì sau đó là ep02)
    num_length = end_idx - start_idx
    
    return prefix, current_num, suffix, num_length

def main():
    link_file = "link.txt"
    
    # 1. Kiểm tra file link.txt
    if not os.path.exists(link_file):
        print(f"❌ Không tìm thấy file '{link_file}'. Vui lòng tạo file và thêm link vào.")
        return

    # Đọc danh sách link, bỏ dòng trống và khoảng trắng thừa
    with open(link_file, "r", encoding="utf-8") as f:
        links = [line.strip() for line in f if line.strip()]

    if not links:
        print("⚠️ File link.txt đang trống!")
        return

    print(status_msg := f"📋 Tìm thấy {len(links)} đường link cần xử lý.")
    print("-" * 40)

    # 2. Nhập tên file bắt đầu
    user_input = input("Nhập tên file bắt đầu (Ví dụ: ep1_vie_56): ").strip()
    if not user_input:
        print("❌ Tên file không được để trống!")
        return

    prefix, current_num, suffix, num_length = parse_prefix(user_input)

    # 3. Vòng lặp tải từng link
    for idx, link in enumerate(links):
        # Tính toán tên file output tiếp theo
        if current_num is not None:
            # Format lại số theo độ dài ban đầu (ví dụ: 1 -> 1, hoặc 01 -> 02)
            formatted_num = f"{current_num:0{num_length}d}"
            output_filename = f"{prefix}{formatted_num}{suffix}.vtt"
            current_num += 1 # Tăng số tập lên cho vòng lặp sau
        else:
            # Trường hợp người dùng nhập tên không có số (ví dụ: 'sub_vie')
            output_filename = f"{user_input}_{idx + 1}.vtt"

        print(f"\n🔄 [{idx + 1}/{len(links)}] Đang tải: {output_filename}")
        
        # Câu lệnh ffmpeg y hệt của bạn
        command = [
            "ffmpeg", "-i", link,
            "-map", "0:s:m:language:vie",
            output_filename
        ]
        
        try:
            # Chạy lệnh ffmpeg thông qua hệ thống
            # Thiết lập y để tự động ghi đè nếu file trùng tên
            subprocess.run(command, check=True)
            print(f"✅ Thành công: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Thất bại khi tải link thứ {idx + 1}. Lỗi: {e}")
        except FileNotFoundError:
            print("❌ Không tìm thấy lệnh 'ffmpeg'. Hãy chắc chắn rằng FFmpeg đã được cài đặt và thêm vào PATH hệ thống.")
            return

    print("\n🎉 Đã xử lý xong toàn bộ danh sách!")

if __name__ == "__main__":
    main()