# Cycle of Curse - DSA Game Project

## Giới thiệu
**Cycle of Curse** là một trò chơi nhập vai hành động (Action RPG) được xây dựng bằng Python và Pygame. Dự án không chỉ là một trò chơi giải trí mà còn là minh chứng cho việc ứng dụng các **Cấu trúc dữ liệu và Giải thuật (DSA)** vào phát triển thực tế.

## Các khái niệm DSA đã áp dụng
- **BFS (Breadth-First Search)**: Thuật toán tìm đường cho quái vật và Thức thần.
- **Singly Linked List**: Quản lý hiệu ứng bóng ma (afterimage) khi nhân vật lướt (dash).
- **DAG (Directed Acyclic Graph)**: Quản lý logic điều kiện nâng cấp trong Cây kỹ năng (Skill Tree).
- **Y-Sorting**: Giải thuật sắp xếp theo trục Y để xử lý chiều sâu đồ họa (Depth Rendering).
- **Finite State Machine (FSM)**: Quản lý các trạng thái hành động của thực thể (Idle, Run, Attack).
- **Flood Fill**: Xử lý tách nền đồ họa tự động.

## Tính năng nổi bật
- **Hệ thống nhân vật**: 3 nhân vật với chỉ số riêng (Monkey, Megumi, Sukuna).
- **Cơ chế triệu hồi (Shikigami)**: Sử dụng vũ khí Sai để triệu hồi các Thức thần chiến đấu cùng người chơi.
- **Boss Fight**: Hệ thống Boss thông minh (Megumi Summoner, Sukuna) với các cơ chế chiến đấu riêng biệt.
- **Cây kỹ năng**: Nâng cấp Máu, Giáp, Tốc độ và Sát thương vũ khí.

## Cài đặt và Khởi chạy

### Yêu cầu
- Python 3.x
- Thư viện Pygame

### Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Chạy game
```bash
python code/main.py
```

## Điều khiển
- **Di chuyển**: W, A, S, D
- **Tấn công**: SPACE
- **Sử dụng Phép/Bình máu**: Z
- **Đổi vũ khí**: Q
- **Lướt (Dash)**: N
- **Mở Cây kỹ năng**: ESC (khi đang chơi)
