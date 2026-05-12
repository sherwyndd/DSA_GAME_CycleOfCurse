PHỤ LỤC: TÀI LIỆU CẤU TRÚC CHI TIẾT TOÀN DIỆN MÃ NGUỒN DỰ ÁN CYCLE OF CURSE
========================================================================================

Tài liệu này trình bày chi tiết từng Module trong hệ thống, bao gồm Tổng quan, Các lớp, Biến số, Phương thức và Chức năng hoạt động.

---

========================================================
1. MODULE: MAIN (main.py)
========================================================
● TỔNG QUÁT: Điểm khởi đầu của ứng dụng, quản lý vòng đời và các trạng thái lớn của game.
● LỚP: Game
  - BIẾN SỐ:
    * self.screen: Bề mặt hiển thị Pygame.
    * self.clock: Đồng hồ điều phối FPS.
    * self.state: Trạng thái hiện tại ('MENU', 'GAME', v.v.).
  - PHƯƠNG THỨC:
    * __init__(): Thiết lập cửa sổ và nạp các module Menu, Settings.
    * run(): Vòng lặp vô hạn xử lý sự kiện và vẽ màn hình theo trạng thái.
● CHỨC NĂNG: Đảm bảo game chạy mượt mà ở 60 FPS và điều hướng chính xác giữa các màn hình chức năng.

========================================================
2. MODULE: ENTITY (entity.py)
========================================================
● TỔNG QUÁT: Chứa các logic vật lý và hoạt ảnh cơ sở cho mọi thực thể di động.
● LỚP: Entity
  - BIẾN SỐ:
    * self.direction: Vector2 hướng di chuyển.
    * self.hitbox: Vùng va chạm vật lý thu nhỏ.
  - PHƯƠNG THỨC:
    * move(speed): Cập nhật vị trí và gọi xử lý va chạm.
    * collision(direction): Kiểm tra và ngăn thực thể đi xuyên vật cản.
● CHỨC NĂNG: Cung cấp nền tảng vật lý thống nhất cho Player, Enemy và Summon.

========================================================
3. MODULE: PLAYER (player.py)
========================================================
● TỔNG QUÁT: Module phức tạp nhất, quản lý nhân vật chính và tiến trình người chơi.
● LỚP: Player (Kế thừa Entity), GhostNode
  - BIẾN SỐ:
    * self.health/self.target_health: Quản lý máu và hiệu ứng mượt thanh HP.
    * self.stats: Dictionary chỉ số (Health, Armor, Attack, Magic, Speed).
    * self.ghost_head: Đầu danh sách liên kết cho hiệu ứng bóng ma di chuyển.
    * self.sai_dogs_data: Trạng thái máu/sống của các chú chó triệu hồi.
  - PHƯƠNG THỨC:
    * input(): Bắt phím điều khiển từ Settings.
    * ghost_logic(): Cập nhật Linked List để tạo vệt bóng ma.
    * update(): Cập nhật cooldown, trạng thái và thực hiện di chuyển.
● CHỨC NĂNG: Cho phép người chơi tương tác với thế giới, thăng tiến sức mạnh qua cây kỹ năng và thực hiện các kỹ thuật chiến đấu.

========================================================
4. MODULE: ENEMY (enemy.py)
========================================================
● TỔNG QUÁT: Quản lý kẻ địch và các giải thuật trí tuệ nhân tạo (AI).
● LỚP: Enemy
  - BIẾN SỐ:
    * self.status: Trạng thái AI ('move', 'attack', 'idle').
    * self.mana: Dùng cho Boss để quản lý thời gian triệu hồi.
  - PHƯƠNG THỨC:
    * get_bfs_direction(): Tìm đường ngắn nhất trên lưới Tile tránh vật cản.
    * actions(): Quyết định tấn công hay đuổi theo dựa trên khoảng cách mục tiêu.
● CHỨC NĂNG: Tạo ra thử thách cho người chơi thông qua các hành vi quái vật thông minh.

========================================================
5. MODULE: SUMMON (summon.py)
========================================================
● TỔNG QUÁT: Hệ thống Thức thần hỗ trợ (Shikigami).
● LỚP: DivineDog, Frog, Bull, Totality
  - BIẾN SỐ:
    * self.orbit_angle: Góc quay quanh chủ nhân.
    * self.is_player_owned: Phân biệt đồng minh và kẻ thù.
  - PHƯƠNG THỨC:
    * separation_logic(): Giải thuật đẩy các thực thể gần nhau để không đè hình.
● CHỨC NĂNG: Tạo ra các đơn vị chiến đấu hỗ trợ, tăng chiều sâu chiến thuật cho game.

========================================================
6. MODULE: LEVEL (level.py)
========================================================
● TỔNG QUÁT: Điều phối toàn bộ dữ liệu màn chơi, va chạm và camera.
● LỚP: Level, YSortCameraGroup
  - BIẾN SỐ:
    * self.visible_sprites: Nhóm vẽ Sprite tích hợp Camera.
    * self.bg_cache: Bộ nhớ đệm ảnh nền tăng hiệu suất.
  - PHƯƠNG THỨC:
    * create_map(): Nạp CSV và khởi tạo thế giới.
    * run(): Nhịp đập chính của Level, xử lý va chạm và UI.
● CHỨC NĂNG: Kết nối tất cả các thực thể lại thành một thế giới game hoàn chỉnh.

========================================================
7. MODULE: UI (ui.py)
========================================================
● TỔNG QUÁT: Hiển thị các thông tin trạng thái và giao diện người dùng.
● LỚP: UI
  - BIẾN SỐ:
    * self.health_bar_rect: Vị trí vẽ thanh máu.
    * self.skill_tree_scroll: Quản lý cuộn bảng kỹ năng.
  - PHƯƠNG THỨC:
    * show_bar(): Vẽ thanh máu/giáp.
    * draw_skill_tree(): Vẽ cây nâng cấp kỹ năng.
● CHỨC NĂNG: Cung cấp phản hồi trực quan về trạng thái nhân vật và tiến trình game.

========================================================
8. MODULE: MAGIC (magic.py)
========================================================
● TỔNG QUÁT: Quản lý các kỹ năng phép thuật và đạn đạo.
● LỚP: SukunaSlash, MagicPlayer
  - BIẾN SỐ:
    * self.ghost_head: Quản lý vệt đạn kéo dài bằng Linked List.
● CHỨC NĂNG: Cung cấp các đòn tấn công tầm xa và khả năng hồi phục đặc biệt.

========================================================
9. MODULE: PARTICLES (particles.py)
========================================================
● TỔNG QUÁT: Hệ thống hiệu ứng hạt và hoạt ảnh ngắn.
● LỚP: AnimationPlayer, ParticleEffect
  - PHƯƠNG THỨC:
    * tint_frames(): Nhuộm màu ảnh hoạt ảnh cho các hiệu ứng nguyên tố.
● CHỨC NĂNG: Tăng cường trải nghiệm thị giác qua các hiệu ứng cháy nổ, va chạm.

========================================================
10. MODULE: MENU (menu.py)
========================================================
● TỔNG QUÁT: Quản lý các màn hình Menu chính, Cài đặt và Bảng xếp hạng.
● CHỨC NĂNG: Điều hướng người chơi trước khi vào trận và lưu trữ kỷ lục.

========================================================
11. MODULE: SUPPORT (support.py)
========================================================
● TỔNG QUÁT: Các hàm tiện ích hỗ trợ nạp dữ liệu.
● HÀM QUAN TRỌNG:
  * remove_background_floodfill(): Giải thuật Flood Fill xử lý độ trong suốt ảnh.

========================================================
12. MODULE: SETTINGS (settings.py)
========================================================
● TỔNG QUÁT: Lưu trữ hằng số cấu hình toàn dự án.
● CHỨC NĂNG: Cân bằng game (sát thương, máu) và cấu hình phím điều khiển.

========================================================
13. MODULE: TILE (tile.py)
========================================================
● TỔNG QUÁT: Đơn vị cơ bản cấu thành địa hình bản đồ.
● CHỨC NĂNG: Định nghĩa vùng va chạm cho tường và các vật thể tĩnh.

========================================================
14. MODULE: WEAPON (weapon.py)
========================================================
● TỔNG QUÁT: Quản lý hình ảnh và vùng va chạm của vũ khí cận chiến.
● CHỨC NĂNG: Đồng bộ vị trí vũ khí theo chuyển động của người chơi.
