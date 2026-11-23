ĐỒ ÁN THỐNG KÊ ỨNG DỤNG
Kiểm định Friedman và chi bình phương Pearson

Chạy demo từ tệp ZIP

  1. Giải nén ZIP. Giữ demo.py và nonparametric_tests.py trong cùng
     thư mục để demo có thể nạp các hàm kiểm định.
  2. Mở Terminal hoặc PowerShell và chuyển đến thư mục vừa giải nén.
     Thay đường dẫn minh họa bằng đường dẫn thật của bạn.

     cd "đường dẫn tới thư mục giải nén"

  3. Kiểm tra Python và chạy lệnh theo hệ điều hành. Cần Python 3.9
     trở lên. Demo chỉ dùng thư viện chuẩn của Python.

     Tác vụ              macOS / Linux                Windows
     Kiểm tra phiên bản  python3 --version            py -3 --version
     Chạy cả 6 ví dụ     python3 demo.py              py -3 demo.py
     Chạy một ví dụ      python3 demo.py F2           py -3 demo.py F2
     Chạy F2 rồi C2      python3 demo.py F2 C2        py -3 demo.py F2 C2
     Xem tùy chọn        python3 demo.py --help       py -3 demo.py --help

     Nếu Windows nhận lệnh python, có thể thay py -3 bằng python.
     Viết hoa mã ví dụ và cách nhau bằng dấu cách.

Nếu báo không tìm thấy demo.py, kiểm tra thư mục hiện tại bằng ls trên
macOS/Linux hoặc dir trên Windows. Nếu báo thiếu nonparametric_tests,
kiểm tra hai tệp Python đã được giải nén vào cùng thư mục.

Mã ví dụ

  F1  Thời gian chạy ba thuật toán trên cùng sáu bộ dữ liệu.
  F2  Điểm hài lòng của ba giao diện, có đồng hạng trong từng người.
  F3  Điểm cùng sinh viên sau khi dùng bốn kiểu ôn tập.
  C1  Độ phù hợp với phân phối xúc xắc công bằng.
  C2  Tính độc lập giữa phương pháp học và kết quả thi.
  C3  Tính đồng nhất của phân phối lựa chọn màu giữa ba chi nhánh.

Mỗi ví dụ dùng dữ liệu giả lập và α = 0,05. Demo in đầu vào,
hạng hoặc tần số kỳ vọng, thống kê, p-value và kết luận.

Đọc kết quả khi chạy F2 C2

  F2  Đọc bảng hạng theo từng khối và dòng tổng hạng. C = 0,8 là hệ
      số hiệu chỉnh đồng hạng. Q = 1,625 là thống kê Friedman.
      Demo quyết định theo p hoán vị = 0,580247; p xấp xỉ = 0,443747
      dùng để đối chiếu. Kết luận chưa đủ bằng chứng bác bỏ H₀.

  C2  Đối chiếu bảng quan sát O với bảng kỳ vọng E. Cộng bốn đóng góp
      (O − E)²/E để được χ² = 6. Với df = 1, p = 0,0143059.
      Vì p < 0,05, demo bác bỏ H₀ về tính độc lập.

Terminal dùng dấu chấm cho số thập phân. Chẳng hạn, 0.580247 trong
terminal là 0,580247 trong báo cáo.

Hàm trong nonparametric_tests.py

  friedman(rows, method="exact")
    Mỗi hàng là một khối độc lập và đầy đủ. Mỗi cột là một điều kiện.
    Chế độ exact liệt kê tối đa 500.000 hoán vị nhãn và cần nhãn có
    thể hoán đổi trong từng khối dưới H₀. Chế độ mặc định asymptotic
    dùng xấp xỉ χ² với k − 1 bậc tự do.

  chi_square_goodness_of_fit(observed, probabilities)
    Nhập tần số nguyên không âm và xác suất dương đã xác định trước.
    Tổng xác suất phải bằng 1.

  chi_square_contingency(table)
    Nhập bảng tần số nguyên không âm, ít nhất 2×2, với tổng các hàng
    và cột dương. Dùng cho tính độc lập hoặc tính đồng nhất.
    Tính thống kê Pearson nguyên bản, không hiệu chỉnh Yates.

Phiên bản PowerPoint có bảng sửa được và ghi chú thuyết trình. Slide
tham khảo tài liệu NIST, Penn State và R, có đường dẫn trong ghi chú.
Báo cáo PDF có mục hướng dẫn chạy demo và lời giải cho cả sáu ví dụ.

Chỉnh sửa báo cáo LaTeX

  Mở Bao_cao_Friedman_ChiSquare.tex trong trình soạn thảo và lưu
  bằng UTF-8. Văn bản, công thức, dữ liệu ví dụ và tài liệu tham khảo
  đều nằm trong tệp này.

  Biên dịch với XeLaTeX hai lượt để cập nhật mục lục và liên kết.

     xelatex Bao_cao_Friedman_ChiSquare.tex
     xelatex Bao_cao_Friedman_ChiSquare.tex

  Có thể biên dịch bằng Tectonic với một lệnh.

     tectonic Bao_cao_Friedman_ChiSquare.tex
