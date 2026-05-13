"""
Summon Module
-------------
Defines shikigami (summons) used by both the Player and Boss Megumi.

DSA Highlights:
- Separation Algorithm: A proximity-based push algorithm to prevent 
  multiple summons from overlapping (stacking).
- BFS Pathfinding: Inherited from DivineDog to allow summons to 
  navigate complex map layouts avoiding obstacles.
- State-Based AI: Manages complex life cycles (Spawn -> Orbit -> Chase -> Despawn).
"""
import pygame
import math
from entity import Entity

class DivineDog(Entity):
    """
    Thức thần Khuyển Thần (Divine Dog) — Lớp cơ sở cho các loại triệu hồi.

    DSA Highlights:
    - Separation Logic: Giải thuật tách biệt để các thực thể không chồng lên nhau.
    - BFS Pathfinding: Tìm đường đến mục tiêu tránh vật cản.
    - Orbit/Chase States: Quản lý hành vi bay quanh chủ hoặc đuổi mục tiêu.
    """


    SPAWN_DURATION  = 600   # ms - time for spawn reveal animation
    DESPAWN_DURATION = 500  # ms - time for despawn hide animation

    def __init__(self, variant, owner, player, groups, obstacle_sprites, damage_player, animation_player, is_player_owned = False, attackable_sprites = None):
        """
        Khởi tạo Thức thần:
        - Xử lý hiệu ứng spawn (loang điểm ảnh).
        - Thiết lập thuộc tính phe phái (đồng minh/kẻ thù).
        - Nạp các thông số AI (orbit angle, speed).
        """

        super().__init__(groups)
        self.animation_player = animation_player
        self.visible_sprites = groups[0] if isinstance(groups, list) else groups
        self.sprite_type  = 'enemy' if not is_player_owned else 'player_summon'
        self.variant      = variant  # 'black' or 'white'
        self.owner        = owner    # Megumi boss OR Player
        self.player       = player
        self.damage_player = damage_player
        self.obstacle_sprites = obstacle_sprites
        self.is_player_owned = is_player_owned
        self.attackable_sprites = attackable_sprites
        if variant in ('black', 'white'):
            self.monster_name = f'divine_dog_{variant}'
        else:
            self.monster_name = variant

        # ── Graphics ─────────────────────────────────────────────────────────
        if variant == 'totality':
            path = f'../graphics/summons/totality-dog.png'
            self.scale = 0.0975 # 1/2 of previous 0.195
        elif variant == 'frog':
            path = f'../graphics/summons/frog.png'
            self.scale = 0.3 # 2x larger
        elif variant == 'bull':
            path = f'../graphics/summons/bull.png'
            self.scale = 0.3
        else:
            path = f'../graphics/summons/divine-dog-{variant}.png'
            self.scale = 0.13

        raw  = pygame.image.load(path).convert_alpha()
        self.base_image  = pygame.transform.scale_by(raw, self.scale)
        self.flipped_image = pygame.transform.flip(self.base_image, True, False)
        
        # ── Animations ────────────────────────────────────────────────────────
        self.status = 'idle'
        self.animations = {'idle': [], 'move': []}
        self._init_animations()
        
        self.image = self.animations['idle'][0]
        self.rect  = self.image.get_rect()

        # ── Stats ─────────────────────────────────────────────────────────────
        from settings import monster_data
        self.monster_info = monster_data.get(self.monster_name, {'health': 100, 'damage': 8, 'exp': 15})
        self.max_health = self.monster_info.get('health', 100)
        self.speed      = self.monster_info.get('speed', 3.1)
        self.attack_damage = self.monster_info.get('damage', 8)
        self.armor      = 0 # Default base armor

        # ── Scaling for Player-owned Summons ──────────────────────────────────
        if is_player_owned:
            # 1. Health: +10% of player health
            self.max_health += int(player.stats['health'] * 0.1)
            # 2. Speed: +10% of player speed
            self.speed += player.stats['speed'] * 0.1
            # 3. Damage: Hard set to 15 as requested
            self.attack_damage = 15
            # 4. Armor: +20% of player armor
            self.armor = player.armor * 0.2
        
        self.attack_radius = self.monster_info.get('attack_radius', 80)
        self.exp_reward = self.monster_info.get('exp', 0) if not is_player_owned else 0

        self.health     = self.max_health
        self.attack_cooldown = 700   # ms
        self.last_attack_time = 0
        self.attack_feedback_duration = 200
        self.attack_feedback_time = 0

        self.vulnerable = True
        self.hit_time   = 0
        self.invincibility_duration = 400

        self.resistance = 0 # No knockback

        # ── Frozen effect ─────────────────────────────────────────────────────
        self.frozen = False
        self.freeze_time = 0
        self.freeze_duration = 500 # 0.5s freeze as requested

        # ── Orbit ─────────────────────────────────────────────────────────────
        self.orbit_angle  = 0.0 if variant == 'white' else math.pi
        self.orbit_radius = 144
        self.orbit_speed  = 1.2  # rad/s

        # ── Find clear spot near owner ────────────────────────────────────────
        # Search in expanding circles to find a spot with no obstacles, no player, and no Megumi
        import random
        spawn_found = False
        search_radius_min = 60
        search_radius_max = 100
        
        for attempt in range(40): # More attempts
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(search_radius_min, search_radius_max)
            # Gradually expand search if no spot found
            if attempt > 20: search_radius_max += 2
            
            ox = owner.rect.centerx + math.cos(angle) * dist
            oy = owner.rect.centery + math.sin(angle) * dist
            
            # Map clamping
            ox = max(40, min(1224 - 40, ox))
            oy = max(40, min(711 - 40, oy))
            
            temp_hitbox = self.base_image.get_rect(center=(int(ox), int(oy))).inflate(-4, -4)
            
            # COLLISION CHECKS:
            # 1. Megumi (owner)
            if temp_hitbox.colliderect(owner.hitbox): continue
            # 2. Player
            if temp_hitbox.colliderect(player.hitbox): continue
            # 3. Obstacles (walls)
            collision_wall = False
            for sprite in obstacle_sprites:
                if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(temp_hitbox):
                    collision_wall = True
                    break
            if collision_wall: continue
            # 4. Other Summons/Enemies
            collision_enemy = False
            for sprite in self.visible_sprites:
                if hasattr(sprite, 'hitbox') and sprite != self and sprite != owner and sprite != player:
                    if sprite.hitbox.colliderect(temp_hitbox):
                        collision_enemy = True
                        break
            if collision_enemy: continue
            
            # If we reach here, spot is CLEAR!
            self.hitbox = temp_hitbox
            self.rect = self.base_image.get_rect(center=self.hitbox.center)
            spawn_found = True
            break
            
        if not spawn_found:
            # Fallback to owner but offset to avoid exact overlap
            self.hitbox = self.base_image.get_rect(center=owner.rect.center).inflate(-4, -4)
            self.hitbox.x += 32
            self.rect.center = self.hitbox.center

        # ── State machine ─────────────────────────────────────────────────────
        self.state       = 'spawning'
        self.state_timer = pygame.time.get_ticks()

        # ── Spawn / despawn pixel animation ───────────────────────────────────
        self._init_pixel_anim()

        self.facing_left = False

    def _init_animations(self):
        """Create procedurally generated bobbing/stretching frames."""
        def make_frames(base_surf):
            frames = []
            for i in range(6):
                t = i / 6.0
                # Squash/Stretch bobbing
                stretch = 1.0 + math.sin(t * math.pi * 2) * 0.05
                squash = 1.0 - math.sin(t * math.pi * 2) * 0.05
                frame = pygame.transform.scale_by(base_surf, (stretch, squash))
                frames.append(frame)
            return frames

        self.animations['idle'] = [self.base_image]
        self.animations['move'] = make_frames(self.base_image)

    def animate(self):
        animation = self.animations['move'] if self.state in ('orbiting', 'chasing') else self.animations['idle']
        
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        
        # Apply red tint when attacking
        now = pygame.time.get_ticks()
        if now - self.attack_feedback_time < self.attack_feedback_duration:
            tint_surf = pygame.Surface(image.get_size()).convert_alpha()
            tint_surf.fill((255, 0, 0, 100)) # Semi-transparent red
            image = image.copy()
            image.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        # Apply ice tint when frozen
        if self.frozen:
            ice_surf = pygame.Surface(image.get_size()).convert_alpha()
            ice_surf.fill((100, 200, 255, 120)) # Light blue
            image = image.copy()
            image.blit(ice_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        if self.facing_left:
            self.image = pygame.transform.flip(image, True, False)
        else:
            self.image = image

    def draw_health_bar(self, surface, offset):
        """Draw a small health bar above the dog."""
        if self.state in ('spawning', 'despawning'): return
        
        bar_width = 30
        bar_height = 4
        
        hp_bg = pygame.Rect(0, 0, bar_width, bar_height)
        hp_bg.midbottom = (self.rect.midtop[0], self.rect.midtop[1] - 2)
        hp_bg.topleft -= offset
        
        ratio = max(0, self.health / self.max_health)
        hp_rect = pygame.Rect(hp_bg.left, hp_bg.top, bar_width * ratio, bar_height)
        
        pygame.draw.rect(surface, 'red', hp_bg)
        pygame.draw.rect(surface, '#00ff00', hp_rect)
        pygame.draw.rect(surface, 'black', hp_bg, 1)

    # ── BFS Pathfinding ───────────────────────────────────────────────────────
    def get_bfs_direction(self, target_pos):
        from collections import deque
        from settings import T_WIDTH, T_HEIGHT, ROWS, COLS
        
        start_c = int(self.hitbox.centerx // T_WIDTH)
        start_r = int(self.hitbox.centery // T_HEIGHT)
        target_c = int(target_pos[0] // T_WIDTH)
        target_r = int(target_pos[1] // T_HEIGHT)

        # BFS radius limit
        dist_to_target = math.hypot(target_pos[0] - self.hitbox.centerx, target_pos[1] - self.hitbox.centery)
        if dist_to_target > 400:
            target_vec = pygame.math.Vector2(target_pos)
            enemy_vec = pygame.math.Vector2(self.hitbox.center)
            return (target_vec - enemy_vec).normalize() if (target_vec - enemy_vec).magnitude() > 0 else pygame.math.Vector2()

        grid = [[0 for _ in range(COLS)] for _ in range(ROWS)]
        for sprite in self.obstacle_sprites:
            if sprite is self or sprite is self.player or sprite is self.owner:
                continue
            left_c = int(sprite.hitbox.left // T_WIDTH)
            right_c = int((sprite.hitbox.right - 1) // T_WIDTH)
            top_r = int(sprite.hitbox.top // T_HEIGHT)
            bottom_r = int((sprite.hitbox.bottom - 1) // T_HEIGHT)
            for r in range(top_r, bottom_r + 1):
                for c in range(left_c, right_c + 1):
                    if 0 <= r < ROWS and 0 <= c < COLS:
                        grid[r][c] = 1

        if 0 <= start_c < COLS and 0 <= start_r < ROWS: grid[start_r][start_c] = 0
        if 0 <= target_c < COLS and 0 <= target_r < ROWS: grid[target_r][target_c] = 0

        queue = deque([(start_c, start_r)])
        visited = {(start_c, start_r): None}
        found = False

        while queue:
            curr_c, curr_r = queue.popleft()
            if curr_c == target_c and curr_r == target_r:
                found = True
                break
            for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nc, nr = curr_c + dc, curr_r + dr
                if 0 <= nc < COLS and 0 <= nr < ROWS:
                    if grid[nr][nc] == 0 and (nc, nr) not in visited:
                        # Prevent corner cutting through walls
                        if dc != 0 and dr != 0:
                            if grid[curr_r][nc] == 1 or grid[nr][curr_c] == 1:
                                continue
                        visited[(nc, nr)] = (curr_c, curr_r)
                        queue.append((nc, nr))

        if found:
            curr = (target_c, target_r)
            path = []
            while curr != (start_c, start_r):
                path.append(curr)
                curr = visited[curr]
            path.reverse()
            if path:
                next_c, next_r = path[0]
                target_pixel = pygame.math.Vector2((next_c + 0.5) * T_WIDTH, (next_r + 0.5) * T_HEIGHT)
                direction = target_pixel - pygame.math.Vector2(self.hitbox.center)
                if direction.magnitude() > 0:
                    return direction.normalize()
        
        target_vec = pygame.math.Vector2(target_pos)
        enemy_vec = pygame.math.Vector2(self.hitbox.center)
        return (target_vec - enemy_vec).normalize() if (target_vec - enemy_vec).magnitude() > 0 else pygame.math.Vector2()

    # ── AI Helpers ───────────────────────────────────────────────────────────
    def _get_target_pos(self):
        if not self.is_player_owned:
            return self.player.rect.center
        
        # Player-owned dogs target nearest enemy
        nearest_enemy = None
        min_dist = 9999
        for sprite in self.attackable_sprites:
            if sprite != self and sprite != self.owner and hasattr(sprite, 'health') and sprite.health > 0:
                # ── Fix: Don't target fellow friendly summons ──
                if self.is_player_owned and getattr(sprite, 'sprite_type', '') == 'player_summon':
                    continue
                
                dist = math.hypot(sprite.rect.centerx - self.hitbox.centerx, sprite.rect.centery - self.hitbox.centery)
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy = sprite
        
        if nearest_enemy:
            return nearest_enemy.rect.center
        return self.player.rect.center # Orbit player if no enemies

    def _chase_target(self):
        if self.state == 'despawning' or not self.owner.alive():
            return
        target_pos = self._get_target_pos()
        
        # Steering leashing: Adjust target if too far from owner
        dist_to_owner = math.hypot(target_pos[0] - self.owner.rect.centerx,
                                 target_pos[1] - self.owner.rect.centery)
        max_leash = self.orbit_radius + (400 if self.is_player_owned else 40) # Larger leash for player dogs
        
        if dist_to_owner > max_leash:
            owner_vec = pygame.math.Vector2(self.owner.rect.center)
            target_vec = pygame.math.Vector2(target_pos)
            target_pos = owner_vec + (target_vec - owner_vec).normalize() * max_leash

        self.direction = self.get_bfs_direction(target_pos)
        self.move(self.speed)
        self.facing_left = self.direction.x < 0

    def _orbit_owner(self, dt):
        if self.state == 'despawning': return
        # 1. Target Position in the orbit
        self.orbit_angle += self.orbit_speed * dt
        tx = self.owner.rect.centerx + math.cos(self.orbit_angle) * self.orbit_radius
        ty = self.owner.rect.centery + math.sin(self.orbit_angle) * self.orbit_radius
        
        # 2. Check if target is within notice zone
        target_pos = self._get_target_pos()
        dist_to_target = math.hypot(target_pos[0] - self.owner.rect.centerx,
                                   target_pos[1] - self.owner.rect.centery)
        
        notice_radius = 400 if self.is_player_owned else self.owner.notice_radius

        if dist_to_target < notice_radius:
            speed = self.speed
        else:
            target_pos = (tx, ty)
            speed = self.speed * 0.8

        self.direction = self.get_bfs_direction(target_pos)
        self.move(speed)
        self.facing_left = self.direction.x < 0

    def _try_attack(self):
        now = pygame.time.get_ticks()
        target_pos = self._get_target_pos()
        dog_vec = pygame.math.Vector2(self.hitbox.center)
        dist = math.hypot(target_pos[0] - dog_vec.x, target_pos[1] - dog_vec.y)
        
        # ── Fix: Stop attacking if owner is dead or despawning ──
        if self.state == 'despawning' or not self.owner.alive():
            return

        if dist < self.attack_radius and now - self.last_attack_time > self.attack_cooldown:
            self.last_attack_time = now
            self.attack_feedback_time = now
            
            if self.is_player_owned:
                # Damage enemies in radius
                for sprite in self.attackable_sprites:
                    if sprite != self and sprite != self.owner and hasattr(sprite, 'health'):
                        # 1. Don't attack fellow friendly summons (dogs/frogs/etc)
                        if getattr(sprite, 'sprite_type', '') == 'player_summon':
                            continue
                        
                        # 2. Don't attack the player (owner)
                        if sprite == self.player or sprite == self.owner:
                            continue
                        
                        # 3. Double check: don't attack self or owner's other dogs
                        if self.is_player_owned and getattr(sprite, 'sprite_type', '') == 'player_summon':
                            continue
                            
                        s_dist = math.hypot(sprite.rect.centerx - self.hitbox.centerx, sprite.rect.centery - self.hitbox.centery)
                        if s_dist < self.attack_radius:
                            if hasattr(sprite, 'get_damage'):
                                sprite.get_damage(self.player, 'weapon')
            else:
                self.damage_player(self.attack_damage, 'none')
            
            # Spawn slash particle on target
            if self.animation_player:
                self.animation_player.create_particles('slash', target_pos, [self.visible_sprites])

    # ── Reveal/Hide Pixel Animation ─────────────────────────────────────────
    def _init_pixel_anim(self):
        w = self.base_image.get_width()
        h = self.base_image.get_height()
        self._rows = []
        for y in range(h):
            row_pixels = []
            for x in range(w):
                if self.base_image.get_at((x, y))[3] > 10:
                    row_pixels.append(x)
            if row_pixels:
                self._rows.append((y, row_pixels))
        self._rows_spawn   = list(reversed(self._rows))
        self._rows_despawn = list(self._rows)

    def _build_spawn_frame(self, progress):
        w, h = self.base_image.get_size()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        total = len(self._rows_spawn)
        half = 0.5
        if progress <= half:
            black_revealed = int((progress / half) * total)
            for i, (y, xs) in enumerate(self._rows_spawn):
                if i < black_revealed:
                    for x in xs: surf.set_at((x, y), (0, 0, 0, 255))
        else:
            colour_revealed = int(((progress - half) / half) * total)
            for i, (y, xs) in enumerate(self._rows_spawn):
                for x in xs:
                    if i < colour_revealed: surf.set_at((x, y), self.base_image.get_at((x, y)))
                    else: surf.set_at((x, y), (0, 0, 0, 255))
        return surf

    def _build_despawn_frame(self, progress):
        w, h = self.base_image.get_size()
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        total = len(self._rows_despawn)
        half = 0.5
        if progress <= half:
            black_count = int((progress / half) * total)
            for i, (y, xs) in enumerate(self._rows_despawn):
                for x in xs:
                    if i < black_count: surf.set_at((x, y), (0, 0, 0, 255))
                    else: surf.set_at((x, y), self.base_image.get_at((x, y)))
        else:
            erase_count = int(((progress - half) / half) * total)
            for i, (y, xs) in enumerate(self._rows_despawn):
                if i >= erase_count:
                    for x in xs: surf.set_at((x, y), (0, 0, 0, 255))
        return surf

    def begin_despawn(self):
        if self.state != 'despawning':
            self.state = 'despawning'
            self.state_timer = pygame.time.get_ticks()

    def get_damage(self, attacker, attack_type):
        if self.vulnerable and self.state not in ('spawning', 'despawning'):
            # Determine damage based on attacker type
            if getattr(attacker, 'sprite_type', '') == 'enemy':
                damage = attacker.attack_damage if hasattr(attacker, 'attack_damage') else 10
            elif hasattr(attacker, 'get_full_weapon_damage'):
                damage = attacker.get_full_weapon_damage()
            elif hasattr(attacker, 'damage'):
                damage = attacker.damage
            else:
                damage = 10
            
            # Apply summon's own armor reduction
            damage -= self.armor
            if damage < 1: damage = 1
                
            self.health -= damage
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False
            self.direction = pygame.math.Vector2() 
            if self.health <= 0:
                self.begin_despawn()
                if self.is_player_owned:
                    self.player.sai_dogs_data[self.variant]['alive'] = False
            
            # Axe freeze effect only from player
            if hasattr(attacker, 'weapon') and attacker.weapon == 'axe':
                import random
                if random.random() < 0.2:
                    self.freeze()
                    if self.animation_player:
                        frozen_pos = (self.rect.midbottom[0], self.rect.midbottom[1] + 20)
                        self.animation_player.create_particles('frozen', frozen_pos, [self.visible_sprites], pos_type='midbottom')

            if not self.is_player_owned and hasattr(self.owner, 'summon_aggro'):
                self.owner.summon_aggro()

    def freeze(self):
        self.frozen = True
        self.freeze_time = pygame.time.get_ticks()
        self.direction = pygame.math.Vector2()

    def hit_reaction(self):
        """Divine Dogs should not be pushed by player attacks."""
        pass

    def enemy_update(self, player):
        pass

    def update(self):
        now = pygame.time.get_ticks()
        dt = 1/60
        elapsed = now - self.state_timer

        if not self.vulnerable:
            if now - self.hit_time >= self.invincibility_duration:
                self.vulnerable = True

        if self.state == 'spawning':
            self.direction = pygame.math.Vector2()
            progress = min(elapsed / self.SPAWN_DURATION, 1.0)
            self.image = self._build_spawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0:
                self.state = 'orbiting'
                self.state_timer = now

        elif self.state == 'despawning':
            self.direction = pygame.math.Vector2()
            progress = min(elapsed / self.DESPAWN_DURATION, 1.0)
            self.image = self._build_despawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0: self.kill()

        # Handle freeze timer
        if self.frozen:
            if now - self.freeze_time >= self.freeze_duration:
                self.frozen = False
            else:
                self.direction = pygame.math.Vector2() # Force no movement

        if self.state == 'orbiting' and not self.frozen:
            self._orbit_owner(dt)
            self._try_attack() 
            # Megumi dogs chase if owner attacks or is aggroed. Player dogs chase if an enemy is found.
            should_chase = False
            if self.is_player_owned:
                if self._get_target_pos() != self.player.rect.center:
                    should_chase = True
            else:
                if getattr(self.owner, 'attacking', False) or getattr(self.owner, '_summon_aggro_flag', False):
                    should_chase = True
            
            if should_chase:
                self.state = 'chasing'
                self.state_timer = now

        elif self.state == 'chasing' and not self.frozen:
            self._chase_target()
            self._try_attack()
            
            # Stop chasing if target is too far or lost
            target_pos = self._get_target_pos()
            owner_vec = pygame.math.Vector2(self.owner.rect.center)
            dist_to_owner = math.hypot(target_pos[0] - owner_vec.x, target_pos[1] - owner_vec.y)
            
            notice_radius = 450 if self.is_player_owned else self.owner.notice_radius
            if dist_to_owner > notice_radius + 50:
                self.state = 'orbiting'
                self.state_timer = now

            if not self.owner.alive():
                self.begin_despawn()

        if self.state not in ('spawning', 'despawning'):
            self.animate()
            
            # ── Separation Logic: Push away from other summons/enemies to avoid overlapping ──
            push_vec = pygame.math.Vector2()
            for sprite in self.visible_sprites:
                if sprite != self and hasattr(sprite, 'hitbox'):
                    # Only push against other summons or enemies
                    if getattr(sprite, 'sprite_type', '') in ('player_summon', 'enemy'):
                        dist_vec = pygame.math.Vector2(self.hitbox.center) - pygame.math.Vector2(sprite.hitbox.center)
                        dist = dist_vec.magnitude()
                        # If overlapping or too close
                        if 0 < dist < 32:
                            push_vec += dist_vec.normalize() * (32 - dist) * 0.1
            
            if push_vec.magnitude() > 0:
                self.hitbox.x += push_vec.x
                self.collision('horizontal')
                self.hitbox.y += push_vec.y
                self.collision('vertical')

        # Update rect from hitbox
        self.rect.center = self.hitbox.center
        if not self.vulnerable:
            self.image.set_alpha(255 if (now // 80) % 2 == 0 else 80)
        else:
            self.image.set_alpha(255)

        # Healing logic: Heal owner 1 HP per second if alive and not anti-healed
        if self.state in ('orbiting', 'chasing') and self.owner.alive():
            if self.is_player_owned:
                self.player.sai_dogs_data[self.variant]['health'] = self.health

            if not hasattr(self, '_last_heal_tick'): self._last_heal_tick = now
            if now - self._last_heal_tick >= 1000:
                self._last_heal_tick = now
                # Only heal if owner is not under anti-heal effect
                is_anti_healed = now - getattr(self.owner, 'anti_heal_time', 0) < getattr(self.owner, 'anti_heal_duration', 3000)
                if not is_anti_healed:
                    heal_amount = 2 if self.variant == 'totality' else 1
                    max_hp = self.owner.max_health # Player now has max_health attribute
                    self.owner.health = min(max_hp, self.owner.health + heal_amount)
                    if self.is_player_owned:
                        self.player.target_health = self.player.health

            # ── Dog's own regeneration when active ──
            if not hasattr(self, '_last_self_regen_tick'): self._last_self_regen_tick = now
            if now - self._last_self_regen_tick >= 1000:
                self._last_self_regen_tick = now
                # Active dogs regen slowly (1 HP per second)
                self.health = min(self.max_health, self.health + 1)

class Frog(DivineDog):
    SPAWN_DURATION = 1000 # Slower spawn effect (1 second)
    DESPAWN_DURATION = 500

    def __init__(self, owner, player, groups, obstacle_sprites, damage_player, animation_player):
        # Frog needs to be in [visible, attackable, obstacle] to be hit and block player
        super().__init__('frog', owner, player, groups, obstacle_sprites, damage_player, animation_player)
        self.monster_name = 'frog'
        self.speed = 1.0
        self.attack_damage = 2
        self.attack_radius = 80
        self.image = pygame.transform.scale_by(pygame.image.load('../graphics/summons/frog.png').convert_alpha(), 0.3)
        self.base_image = self.image
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(-10, -10)
        
        # Start near Megumi (owner) - Find a clear spot
        import random
        spawn_found = False
        search_min = 30
        search_max = 60
        for attempt in range(30):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(search_min, search_max)
            if attempt > 15: search_max += 5
            
            ox = owner.rect.centerx + math.cos(angle) * dist
            oy = owner.rect.centery + math.sin(angle) * dist
            
            # Map clamping
            ox = max(40, min(1224 - 40, ox))
            oy = max(40, min(711 - 40, oy))
            
            temp_hitbox = self.image.get_rect(center=(int(ox), int(oy))).inflate(-10, -10)
            
            # Collisions
            if temp_hitbox.colliderect(owner.hitbox): continue
            if temp_hitbox.colliderect(player.hitbox): continue
            
            collision = False
            for sprite in obstacle_sprites:
                if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(temp_hitbox):
                    collision = True
                    break
            if collision: continue
            
            collision_enemy = False
            for sprite in self.visible_sprites:
                if hasattr(sprite, 'hitbox') and sprite != self and sprite != owner and sprite != player:
                    if sprite.hitbox.colliderect(temp_hitbox):
                        collision_enemy = True
                        break
            if collision_enemy: continue
            
            # Spot is clear!
            self.hitbox = temp_hitbox
            self.rect = self.image.get_rect(center=self.hitbox.center)
            spawn_found = True
            break
        
        if not spawn_found:
            self.hitbox.center = owner.rect.center
            self.rect.center = self.hitbox.center

        self.state = 'spawning'
        self.state_timer = pygame.time.get_ticks()
        self._init_pixel_anim()
        
        self.animations = {'idle': [], 'move': []}
        self._init_animations()

    def _try_attack(self):
        now = pygame.time.get_ticks()
        dist = (pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.hitbox.center)).magnitude()
        if dist < self.attack_radius and now - self.last_attack_time > 1000:
            self.last_attack_time = now

            # Slow on every successful hit (refresh duration)
            self.player.is_slowed = True
            self.player.slow_start_time = now

            if not hasattr(self, 'last_effect_time'): self.last_effect_time = 0
            if now - self.last_effect_time > 3000:
                self.last_effect_time = now
                self.damage_player(self.attack_damage, 'none')
                if self.animation_player:
                    self.animation_player.create_particles('frog_hit', self.player.rect.center, [self.visible_sprites])
            else:
                self.damage_player(self.attack_damage, 'none')

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        # ── Spawn / Despawn Pixel Animation ───────────────────────────────────
        if self.state == 'spawning':
            progress = min(elapsed / self.SPAWN_DURATION, 1.0)
            self.image = self._build_spawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0:
                self.state = 'chasing'
                self.state_timer = now
            return
            
        if self.state == 'despawning':
            progress = min(elapsed / self.DESPAWN_DURATION, 1.0)
            self.image = self._build_despawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0: self.kill()
            return

        # 1. Base update (handles vulnerability, blinking, rect update)
        super().update()

        # 2. Movement Logic (BFS)
        self.direction = self.get_bfs_direction(self.player.rect.center)
        if self.direction.x != 0: self.facing_left = self.direction.x < 0
        
        # 3. Apply movement
        self.move(self.speed)
        self.animate() # Bobbing animation
        
        # 4. Attack
        self._try_attack()
        
        # 5. Healing owner
        if not hasattr(self, '_last_heal_tick'): self._last_heal_tick = now
        if now - self._last_heal_tick >= 1000:
            self._last_heal_tick = now
            is_anti_healed = now - getattr(self.owner, 'anti_heal_time', 0) < getattr(self.owner, 'anti_heal_duration', 3000)
            if not is_anti_healed:
                self.owner.health = min(self.owner.max_health, self.owner.health + 1)

class Bull(DivineDog):
    def __init__(self, owner, player, groups, obstacle_sprites, damage_player, animation_player):
        super().__init__('bull', owner, player, groups, obstacle_sprites, damage_player, animation_player)
        self.monster_name = 'bull'
        self.max_health = 150
        self.health = 150
        self.speed = 1.5 # Slower speed
        self.attack_damage = 15 # Reduced from 25
        self.attack_radius = 80
        
        # Override image
        path = '../graphics/summons/bull.png'
        raw = pygame.image.load(path).convert_alpha()
        self.base_image = pygame.transform.scale_by(raw, 0.3)
        self.flipped_image = pygame.transform.flip(self.base_image, True, False)
        self.image = self.base_image
        self.rect = self.image.get_rect()
        self.hitbox = self.rect.inflate(-20, -20)
        
        # Standard clear-spot spawn logic
        import random
        spawn_found = False
        search_min, search_max = 40, 80
        for attempt in range(30):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(search_min, search_max)
            if attempt > 15: search_max += 5
            ox = owner.rect.centerx + math.cos(angle) * dist
            oy = owner.rect.centery + math.sin(angle) * dist
            ox = max(40, min(1224 - 40, ox))
            oy = max(40, min(711 - 40, oy))
            temp_hitbox = self.image.get_rect(center=(int(ox), int(oy))).inflate(-20, -20)
            if temp_hitbox.colliderect(owner.hitbox): continue
            if temp_hitbox.colliderect(player.hitbox): continue
            
            collision_wall = False
            for sprite in obstacle_sprites:
                if hasattr(sprite, 'hitbox') and sprite.hitbox.colliderect(temp_hitbox):
                    collision_wall = True
                    break
            if collision_wall: continue
            
            collision_enemy = False
            for sprite in self.visible_sprites:
                if hasattr(sprite, 'hitbox') and sprite != self and sprite != owner and sprite != player:
                    if sprite.hitbox.colliderect(temp_hitbox):
                        collision_enemy = True
                        break
            if collision_enemy: continue

            self.hitbox = temp_hitbox
            self.rect = self.image.get_rect(center=self.hitbox.center)
            spawn_found = True
            break
        
        if not spawn_found:
            self.hitbox.center = owner.rect.center
            self.rect.center = self.hitbox.center

        self.state = 'spawning'
        self.state_timer = pygame.time.get_ticks()
        self._init_pixel_anim()
        
        self.animations = {'idle': [], 'move': []}
        self._init_animations()

    def _try_attack(self):
        now = pygame.time.get_ticks()
        dist = (pygame.math.Vector2(self.player.rect.center) - pygame.math.Vector2(self.hitbox.center)).magnitude()
        if dist < self.attack_radius and now - self.last_attack_time > 1000: # Fast regular damage
            self.last_attack_time = now
            
            # Effects (Knockback) only every 3s
            if not hasattr(self, 'last_effect_time'): self.last_effect_time = 0
            if now - self.last_effect_time > 3000:
                self.last_effect_time = now
                self.damage_player(self.attack_damage, 'bull') # 'bull' triggers knockback in level.py
            else:
                self.damage_player(self.attack_damage, 'none') # Damage only

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.state_timer

        if self.state == 'spawning':
            progress = min(elapsed / self.SPAWN_DURATION, 1.0)
            self.image = self._build_spawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0:
                self.state = 'chasing'
                self.state_timer = now
            return
            
        if self.state == 'despawning':
            progress = min(elapsed / self.DESPAWN_DURATION, 1.0)
            self.image = self._build_despawn_frame(progress)
            if self.facing_left: self.image = pygame.transform.flip(self.image, True, False)
            if progress >= 1.0: self.kill()
            return

        super().update()
        
        if self.state == 'chasing':
            self.direction = self.get_bfs_direction(self.player.rect.center)
            if self.direction.x != 0: self.facing_left = self.direction.x < 0
            self.move(self.speed)
            self.animate()
            self._try_attack()
            
            if not self.owner.alive(): self.begin_despawn()
        
        self.rect.center = self.hitbox.center

    def enemy_update(self, player):
        self.update()
