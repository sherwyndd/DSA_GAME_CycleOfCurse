# Tài liệu Dự án: Cycle of Curse (DSA Game Project)

Đây là tài liệu tổng hợp cấu trúc và cách vận hành của dự án Game Pygame "Cycle of Curse". Tài liệu này tập trung vào các file code chính và mối quan hệ giữa chúng khi chạy ứng dụng từ file `main.py`.

## 1. Cấu trúc thư mục dự án

```text
DSA-Game-Project/
├── code/                   # Chứa toàn bộ mã nguồn logic
│   ├── main.py             # File khởi chạy chính (Entry Point)
│   ├── settings.py         # Cấu hình game, thông số nhân vật/vũ khí, bản đồ
│   ├── level.py            # Quản lý màn chơi, Camera và sắp xếp Sprite
│   ├── player.py           # Logic nhân vật (di chuyển, hoạt ảnh, đầu vào)
│   ├── weapon.py           # Logic vũ khí (hiển thị, vị trí khi tấn công)
│   └── tile.py             # Lớp cơ bản cho các vật thể tĩnh trên bản đồ
├── graphics/               # Chứa các tài nguyên đồ họa mới
│   └── weapons/            # Hình ảnh các loại vũ khí (Sword, Axe, Lance...)
├── image/                  # Chứa hình ảnh nhân vật và bối cảnh
│   ├── monkey.png          # Sprite nhân vật chính
│   └── background4.png     # Hình ảnh nền bản đồ
└── audio/                  # (Nếu có) Chứa âm thanh game
```

## 2. Chi tiết các file Code chính

### 🚀 `main.py`
- **Vai trò**: Trái tim của game.
- **Chức năng**: Khởi tạo cửa sổ Pygame, thiết lập vòng lặp game (Game Loop), xử lý sự kiện thoát và gọi hàm cập nhật của lớp `Level`.

### ⚙️ `settings.py`
- **Vai trò**: Nơi lưu trữ tất cả các "con số".
- **Thông số quan trọng**:
    - `WIDTH`, `HEIGHT`: Kích thước màn hình (900x700).
    - `PLAYER_INDEX`: ID nhân vật đang chọn (Monkey, Megumi, Sukuna).
    - `WEAPON_INDEX`: ID vũ khí khởi đầu.
    - `weapon_data`: Từ điển chứa sát thương và thời gian hồi của từng loại vũ khí.
    - `WORLD_MAP`: Mảng 2 chiều định nghĩa bố cục bản đồ.

### 🗺️ `level.py`
- **Vai trò**: Quản lý sự tương tác giữa các Sprite.
- **Chức năng**: 
    - Đọc `WORLD_MAP` để tạo các ô gạch (`Tile`) và người chơi (`Player`).
    - Lớp `YSortCameraGroup`: Xử lý Camera đi theo người chơi và kỹ thuật **Y-Sorting** (vật thể ở dưới sẽ che vật thể ở trên để tạo độ sâu 2.5D).
    - Quản lý vòng đời của đòn tấn công thông qua `create_attack` và `destroy_attack`.

### 🤺 `player.py`
- **Vai trò**: Điều khiển hành vi của người chơi.
- **Logic quan trọng**:
    - `input()`: Nhận phím điều hướng (WASD), tấn công (SPACE), lướt (L-CTRL) và đổi vũ khí (Q).
    - `get_status()`: Xác định trạng thái hiện tại (đứng yên, chạy, tấn công) để chọn hoạt ảnh phù hợp.
    - `animate()`: Xử lý việc chuyển đổi các khung hình của nhân vật.
    - **Ràng buộc**: Nhân vật không được tấn công khi đang di chuyển (đã cập nhật theo yêu cầu).

### ⚔️ `weapon.py`
- **Vai trò**: Hiển thị vũ khí khi tấn công.
- **Chức năng**: Nạp hình ảnh vũ khí dựa trên trạng thái `weapon` của Player và hướng nhìn để đặt vị trí vũ khí chính xác vào tay nhân vật.

## 3. Luồng hoạt động của Game

1. **Khởi chạy**: `main.py` -> `Level()` -> `create_map()`.
2. **Cập nhật liên tục**: 
   - `Player.input()` kiểm tra phím nhấn.
   - Nếu nhấn SPACE và đang đứng yên: `Player` gọi `create_attack()` (trong `level.py`).
   - `level.py` tạo một instance của `Weapon`.
   - Sau `action_duration` (thời gian ra đòn), `Player` gọi `destroy_attack()` để xóa vũ khí.
3. **Hiển thị**: `YSortCameraGroup` sắp xếp tất cả Sprite theo tọa độ Y và vẽ lên màn hình.
