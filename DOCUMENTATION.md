# Cycle of Curse - Comprehensive Technical Documentation

## 1. System Overview
**Cycle of Curse** is a sophisticated action-RPG built with Python 3.11 and Pygame-ce. It is designed as an educational project to demonstrate the practical application of **Data Structures and Algorithms (DSA)** in a dynamic gaming environment.

---

## 2. Architecture & Module Breakdown

### 2.1 Game Controller (`main.py`)
The orchestrator of the entire system.
*   **`Game.__init__()`**: Initializes Pygame, screen, clock, and top-level states (Menu, Settings, Leaderboard, Game).
*   **`Game.run()`**: The master game loop. Manages state transitions and events.
*   **`Game.check_controls_ready()`**: Ensures all movement and action keys are assigned before starting.

### 2.2 World & Level Manager (`level.py`)
Orchestrates the environment and sprite interactions.
*   **`Level.create_map()`**: Parses the map layout and populates tiles, player, and enemies.
*   **`Level.run(events)`**: Updates and draws all sprites, manages combat logic, and handles UI overlays.
*   **`Level.check_map_progression()`**: Detects when a round is cleared and manages the transition to the next stage or the win screen.
*   **`YSortCameraGroup.custom_draw(player)`**: Implements **Y-Sorting** to handle depth perception.
*   **`YSortCameraGroup.enemy_update(player)`**: Updates enemy AI by passing a list of valid targets (Player + Summons).

### 2.3 Player Controller (`player.py`)
Handles the protagonist's state, progression, and special effects.
*   **`Player.get_status()`**: Updates animation states (idle, move, attack) based on input.
*   **`Player.move(speed)`**: Standard movement with collision detection.
*   **`Player.ghost_logic()`**: Implements a **Singly Linked List** to render after-image effects.
*   **`Player.skill_tree_logic()`**: Applies permanent stat upgrades and weapon unlocks.

### 2.4 Enemy AI & Bosses (`enemy.py`)
Complex AI logic for various enemy types.
*   **`Enemy.get_target_distance_direction(targets)`**: Renamed from player-only targeting to support multiple targets (Summons).
*   **`Enemy.get_bfs_direction(targets)`**: Implements **Breadth-First Search (BFS)** to navigate around walls.
*   **`Enemy.summon_update()`**: Specific logic for Boss 2 (Megumi) to manage mana and summon shikigami.

### 2.5 Shikigami System (`summon.py`)
Support entities for both Player and Bosses.
*   **`DivineDog.update()`**: Manages states (Spawning, Orbiting, Chasing, Despawning).
*   **`DivineDog._try_attack()`**: AOE damage logic with friendly-fire prevention.
*   **`DivineDog.separation_logic()`**: Proximity-based algorithm to prevent summons from stacking.

### 2.6 User Interface & Skill Tree (`ui.py`)
Interactive HUD and progression system.
*   **`UI.show_bar()` / `UI.show_armor_bar()`**: Renders health/armor with smooth transitions and numerical overlays.
*   **`UI.draw_skill_tree()`**: A tiered upgrade system with scrolling support and prerequisite-checking logic.
*   **`UI.show_round_enemy_intro()`**: Renders a dynamic card-based layout for enemy intelligence.

---

## 3. Data Structures & Algorithms (DSA) Highlights

### 3.1 Pathfinding (BFS)
*   **Logic**: Uses a queue-based exploration of the coordinate grid.
*   **Complexity**: $O(V + E)$.
*   **Purpose**: Allows enemies to "think" ahead and move around corners rather than getting stuck on walls.

### 3.2 Depth Rendering (Y-Sorting)
*   **Logic**: Every frame, the camera group sorts the list of visible sprites by their `rect.centery`.
*   **Purpose**: Simulates a 3D Z-axis in a 2D space.

### 3.3 Movement Trail (Linked List)
*   **Logic**: The "Ghost" effect uses a linked list where nodes represent recent positions.
*   **Purpose**: Efficiently manages many temporary visual elements with fast head-insertion and tail-removal.

### 3.4 Dependency Graph (Skill Tree)
*   **Logic**: Nodes are organized in categories with `prereq` IDs.
*   **Purpose**: Models a progression tree where advanced skills depend on basic ones.

---

## 4. Combat Mechanics

### 4.1 Status Effects
*   **Anti-Heal (Sword/Magic)**: Prevents health regeneration for a fixed duration.
*   **Freeze (Axe)**: Disables movement and attack logic via a `frozen` state.
*   **Burn (Magic)**: Applies damage over time (DOT) with a visual red flickering effect.
*   **Slow (Magic)**: Reduces movement speed by a percentage.

### 4.2 Persistence
*   **Summon Health**: The player's Divine Dogs store their health in the `Player` object, ensuring they maintain damage levels across weapon swaps.
*   **Leaderboard**: Scores (Round and Time) are persisted in `leaderboard.json` using JSON serialization.

---

## 5. Technical Specifications
*   **Language**: Python 3.11+
*   **Rendering**: Pygame-ce (Community Edition)
*   **Design Pattern**: Component-based entity architecture within an OOP framework.
