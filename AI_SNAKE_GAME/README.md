# 🐍 AI SNAKE GAME – A* PATHFINDING + HAMILTONIAN CYCLE

> Dự án game Rắn săn mồi tự động bằng Trí tuệ Nhân tạo (AI), phát triển bằng **Python 3** và **Pygame**. Rắn hoàn toàn tự động tính toán đường đi, săn mồi, tránh chướng ngại vật, không bao giờ tự đâm vào thân và có khả năng phủ kín 100% bản đồ.

---

## 🌟 1. Giới thiệu & Điểm nổi bật
- **Tự động 100%**: Không cần người chơi điều khiển bằng bàn phím. Toàn bộ quyết định di chuyển được tính toán thời gian thực bởi AI.
- **Phối hợp 2 thuật toán đỉnh cao**:
  - **A\* Pathfinding**: Tìm đường đi ngắn nhất đến thức ăn với hàm heuristic khoảng cách Manhattan ($f = g + h$), tối ưu hóa tốc độ ăn mồi.
  - **Hamiltonian Cycle**: Xây dựng chu trình khép kín đi qua toàn bộ 400 ô trên lưới 20×20, bảo đảm tính an toàn tuyệt đối và khả năng lấp đầy 100% bản đồ mà không bao giờ tự kẹt.
  - **Hamiltonian Shortcutting**: Cho phép AI "đi tắt" khỏi chu trình để ăn mồi nhanh hơn khi và chỉ khi chứng minh được đường đi tắt không phá vỡ tính an toàn của thân rắn.
  - **Cơ chế phòng thủ (Flood Fill & Tail Reachability)**: Giả lập trạng thái sau khi ăn mồi để kiểm tra đầu mới có còn đường vươn tới đuôi hay không; nếu gặp thế bế tắc, AI tự động chọn không gian mở rộng nhất để sống sót chờ đuôi co lại.
- **Giao diện hiện đại & Trực quan hóa (Visualization)**:
  - Hiển thị trực quan các ô A\* đã duyệt (màu xanh dương).
  - Hiển thị đường đi A\* tối ưu (màu vàng rực rỡ).
  - Bật/tắt đường chu trình Hamiltonian (màu tím).
  - Bảng điều khiển thời gian thực với **8 thông số** chi tiết và các nút bấm tương tác mượt mà.

---

## 📁 2. Cấu trúc thư mục dự án

```text
AI_SNAKE_GAME/
│
├── main.py             # Điểm khởi chạy chương trình
├── settings.py         # Cấu hình bản đồ, kích thước, bảng màu và tốc độ
├── game.py             # Quản lý vòng lặp game, sự kiện và tương tác
├── snake.py            # Quản lý thân rắn, chuyển động và kiểm tra va chạm
├── food.py             # Quản lý thức ăn, sinh vị trí ngẫu nhiên không trùng thân
├── astar.py            # Cài đặt thuật toán A* Search & kiểm tra vươn tới đuôi
├── hamiltonian.py      # Xây dựng chu trình Hamiltonian & kiểm tra bước đi tắt an toàn
├── ai_controller.py    # Bộ não AI điều phối các chiến lược di chuyển
├── visualization.py    # Giao diện Pygame, Dashboard 8 chỉ số và nút bấm UI
├── test_ai.py          # Bộ kiểm thử tự động 7 kịch bản (Unit Tests)
├── requirements.txt    # Danh sách thư viện phụ thuộc
└── README.md           # Hướng dẫn chi tiết sử dụng
```

---

## ⚙️ 3. Yêu cầu hệ thống & Cài đặt

### Yêu cầu:
- Python 3.10 trở lên (hỗ trợ hoàn hảo từ Python 3.10 đến Python 3.14+).
- Visual Studio Code (hoặc bất kỳ IDE Python nào).

### Cài đặt thư viện:
Mở Terminal trong thư mục dự án và chạy lệnh:
```bash
pip install -r requirements.txt
```
*(Thư viện `pygame-ce` được sử dụng nhằm đảm bảo tương thích 100% với `import pygame` và tối ưu hiệu năng cao nhất trên Windows).*

---

## 🚀 4. Hướng dẫn chạy dự án trong Visual Studio Code

1. Mở thư mục `AI_SNAKE_GAME` trong **Visual Studio Code**.
2. Mở file `main.py`.
3. Nhấn **F5** (Run with Debugging) hoặc nút **Play** ở góc trên bên phải để chạy.
4. Hoặc chạy trực tiếp từ Terminal:
   ```bash
   python main.py
   ```

---

## 🎮 5. Phím tắt & Bảng điều khiển (Controls)

Bạn có thể click trực tiếp bằng chuột lên các nút trên giao diện bên phải, hoặc dùng các phím tắt nhanh sau:

| Phím tắt | Chức năng |
| :--- | :--- |
| `Space` | **Tạm dừng / Tiếp tục** (Pause / Resume) |
| `R` | **Khởi động lại ván chơi** (Restart) |
| `↑` hoặc `→` | **Tăng tốc độ** (Tăng FPS) |
| `↓` hoặc `←` | **Giảm tốc độ** (Giảm FPS) |
| `P` | **Bật / Tắt hiển thị đường đi A\*** (Show/Hide Path) |
| `S` | **Bật / Tắt hiển thị các ô A\* đã duyệt** (Show/Hide Search Nodes) |
| `H` | **Bật / Tắt hiển thị Chu trình Hamiltonian** (Show/Hide Cycle) |
| `M` | **Chuyển đổi chế độ AI**: Smart Hybrid $\leftrightarrow$ Pure Hamiltonian $\leftrightarrow$ Pure A\* |

---

## 📊 6. Bảng thông số thời gian thực (8 Chỉ số)

Bảng Dashboard hiển thị đầy đủ 8 thông số theo dõi hiệu năng của AI:
1. **Score**: Điểm số hiện tại (+10 điểm cho mỗi lần ăn mồi).
2. **Snake Length**: Chiều dài hiện tại của rắn / Tổng số ô bản đồ (tối đa 400).
3. **A\* Nodes**: Số lượng nút trạng thái mà thuật toán A\* đã duyệt qua trong lượt tính toán.
4. **Path Length**: Độ dài đường đi ngắn nhất vừa được tính toán.
5. **Map Coverage**: Tỷ lệ phần trăm diện tích bản đồ đang bị rắn chiếm giữ (có kèm thanh Progress Bar trực quan).
6. **AI Status**: Mô tả trạng thái quyết định hiện tại của AI.
7. **Algorithm**: Tên chiến lược đang được kích hoạt (`A* Tối ưu`, `Đi tắt Hamiltonian`, `Chu trình Hamiltonian`, `Sinh tồn Flood Fill`).
8. **Runtime**: Tổng thời gian chạy ván đấu (định dạng `MM:SS`).

---

## 🧪 7. Kiểm thử tự động (Unit Tests)

Dự án đi kèm bộ kiểm thử tự động tại `test_ai.py` kiểm tra toàn bộ 7 kịch bản quan trọng:
- [x] Tính đúng đắn toán học của Chu trình Hamiltonian 20x20 (khép kín, 400 ô, không cắt chéo).
- [x] Săn mồi ở vị trí gần.
- [x] Săn mồi ở khoảng cách xa (góc đối diện).
- [x] Tìm đường vòng qua nhiều chướng ngại vật phức tạp.
- [x] Thức ăn tự động sinh ở vị trí mới hợp lệ sau khi ăn.
- [x] Xử lý an toàn khi rắn có chiều dài lớn (> 70% bản đồ).
- [x] Kích hoạt cơ chế sinh tồn Flood Fill khi gặp ngõ cụt.

Để chạy bộ kiểm thử:
```bash
python test_ai.py
```
Kết quả mong đợi: `Ran 7 tests in ... OK`.
