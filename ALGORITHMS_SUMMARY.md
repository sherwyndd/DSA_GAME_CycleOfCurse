# TÀI LIỆU TỔNG HỢP GIẢI THUẬT & CẤU TRÚC DỮ LIỆU (DSA) - DỰ ÁN CYCLE OF CURSE

Tài liệu này trình bày sự kết hợp giữa nền tảng lý thuyết (từ thư mục `TaiLieu`) và các triển khai thực tế trong mã nguồn của trò chơi.

---

## 1. ĐỐI CHIẾU LÝ THUYẾT (TÀI LIỆU HỌC THUẬT)

Dưới đây là sự tương quan giữa các tệp tài liệu PDF và các tính năng trong game:

*   **LinkedList full.pdf**: Triển khai cấu trúc `GhostNode` (Danh sách liên kết đơn) để quản lý bộ nhớ và hiển thị hiệu ứng bóng ma di chuyển.
*   **Searching full.pdf**: Triển khai thuật toán **BFS (Breadth-First Search)** để xử lý trí tuệ nhân tạo (AI) giúp quái vật tìm đường tránh vật cản.
*   **Sorting full.pdf**: Triển khai thuật toán **Sắp xếp (Sorting)** trong `YSortCameraGroup` để xử lý thứ tự vẽ các lớp đồ họa theo chiều sâu.
*   **Tree full.pdf**: Triển khai cấu trúc **Đồ thị có hướng không chu trình (DAG)** cho hệ thống Cây kỹ năng (Skill Tree).
*   **LinearDynamicStructures.pdf**: Sử dụng cấu trúc dữ liệu **Hàng đợi (Queue)** (`collections.deque`) làm nền tảng cho việc duyệt các ô trong thuật toán BFS.

---

## 2. CHI TIẾT CÁC GIẢI THUẬT TRONG MÃ NGUỒN

### 2.1 Nhóm Tìm Đường & AI
#### ● Breadth-First Search (BFS)
*   **Vị trí:** `enemy.py` (`get_bfs_direction`), `summon.py`
*   **Mô tả:** Sử dụng một hàng đợi để loang từ vị trí quái vật ra các ô xung quanh trên lưới Grid.
*   **Mục đích:** Tìm đường đi ngắn nhất đến mục tiêu và tự động tránh các Tile vật cản (vách núi, tường).

#### ● Separation Algorithm (Thuật toán Tách biệt)
*   **Vị trí:** `summon.py` (`separation_logic`)
*   **Mô tả:** Sử dụng vector đẩy ngược chiều dựa trên khoảng cách vật lý giữa các thực thể.
*   **Mục đích:** Ngăn chặn các Thức thần đứng chồng lên nhau, giúp đội hình di chuyển tự nhiên hơn.

### 2.2 Nhóm Đồ Họa & Hiển Thị
#### ● Y-Sorting (Sắp xếp theo trục Y)
*   **Vị trí:** `level.py` (`YSortCameraGroup`)
*   **Mô tả:** Sắp xếp danh sách Sprite dựa trên tọa độ Y (`centery`) của hitbox trước khi vẽ.
*   **Mục đích:** Mô phỏng chiều sâu Z-axis. Vật ở dưới (Y lớn) sẽ che vật ở trên (Y nhỏ).

#### ● Flood Fill (Giải thuật Loang màu)
*   **Vị trí:** `support.py` (`remove_background_floodfill`)
*   **Mô tả:** Loang từ 4 góc ảnh để nhận diện màu nền và chuyển Alpha về 0.
*   **Mục đích:** Tách nền thông minh cho nhân vật mà vẫn giữ được màu trắng bên trong mắt hoặc trang phục.

#### ● Linear Interpolation (Nội suy tuyến tính - Lerp)
*   **Vị trí:** `ui.py` (`show_bar`)
*   **Mô tả:** Tính toán giá trị trung gian giữa máu hiện tại và máu mục tiêu qua từng khung hình.
*   **Mục đích:** Tạo hiệu ứng thanh máu co dãn mượt mà thay vì thay đổi đột ngột.

### 2.3 Nhóm Cấu Trúc Dữ Liệu
#### ● Singly Linked List (Danh sách liên kết đơn)
*   **Vị trí:** `player.py` (`GhostNode`), `magic.py` (`SukunaSlash`)
*   **Mô tả:** Mỗi khung hình di chuyển tạo ra một Node liên kết với nhau.
*   **Mục đích:** Quản lý hiệu ứng bóng ma. Chèn Node vào đầu (Head) và xóa Node ở cuối (Tail) với độ phức tạp O(1).

#### ● Directed Acyclic Graph (DAG - Đồ thị có hướng không chu trình)
*   **Vị trí:** `player.py` (`skill_tree_nodes`)
*   **Mô tả:** Các nút kỹ năng liên kết với nhau thông qua danh sách `prereq`.
*   **Mục đích:** Quản lý logic nâng cấp kỹ năng theo cấp bậc (LV1 -> LV2).

#### ● Finite State Machine (FSM - Máy trạng thái hữu hạn)
*   **Vị trí:** `player.py`, `enemy.py`
*   **Mô tả:** Chia hành vi thực thể thành các trạng thái cố định (Idle, Move, Attack).
*   **Mục đích:** Tránh xung đột logic và giúp code AI dễ quản lý hơn.

---

## 3. TỔNG KẾT THÔNG SỐ KỸ THUẬT
- **Độ phức tạp BFS:** O(V + E) với V là số ô lưới trên màn hình.
- **Độ phức tạp Sorting:** O(N log N) sử dụng thuật toán Timsort của Python.
- **Lưu trữ dữ liệu:** Sử dụng định dạng **JSON** để lưu trữ bảng xếp hạng (`leaderboard.json`).
