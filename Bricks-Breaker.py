import heapq
import random
import tkinter as tk


class AStarPaddlePlanner:
    """A* Pathfinding Algorithm to compute optimal paddle movements."""

    def __init__(self, paddle_width, paddle_speed):
        self.paddle_width = paddle_width
        self.paddle_speed = paddle_speed

    def predict_ball_landing_x(
        self, ball_x, ball_y, dx, dy, target_y, canvas_width
    ):
        """Simulates ball trajectory including wall bounces to predict landing position."""
        curr_x, curr_y = ball_x, ball_y
        curr_dx, curr_dy = dx, dy
        r = 8

        if curr_dy <= 0:
            return canvas_width / 2

        while curr_y < target_y:
            curr_x += curr_dx
            curr_y += curr_dy

            if curr_x - r <= 0 or curr_x + r >= canvas_width:
                curr_dx = -curr_dx
                curr_x = max(r, min(curr_x, canvas_width - r))

        return curr_x

    def solve_path(
        self, start_x, target_x, canvas_width, paddle_width, max_steps=60
    ):
        """A* Search Algorithm finding the optimal action sequence."""
        start_h = abs(start_x + paddle_width / 2 - target_x)
        open_set = []
        heapq.heappush(open_set, (start_h, 0, start_x, []))

        visited = set()

        while open_set:
            f, g, curr_x, path = heapq.heappop(open_set)
            center_x = curr_x + paddle_width / 2

            if (
                abs(center_x - target_x) <= self.paddle_speed / 2
                or g >= max_steps
            ):
                return path

            state_key = (round(curr_x, 1), g)
            if state_key in visited:
                continue
            visited.add(state_key)

            for action in [-1, 0, 1]:
                next_x = curr_x + (action * self.paddle_speed)
                next_x = max(10, min(next_x, canvas_width - paddle_width - 10))

                next_g = g + 1
                next_center = next_x + paddle_width / 2
                next_h = abs(next_center - target_x)
                next_f = next_g + next_h

                heapq.heappush(
                    open_set, (next_f, next_g, next_x, path + [action])
                )

        return []


class DualModeBreakoutGame:

    def __init__(self, root):
        self.root = root
        self.root.title("Brick Breaker - Fully Responsive Fullscreen")
        self.root.configure(bg="#0d1117")

        # Initial Dimensions
        self.width = 700
        self.height = 600
        self.is_fullscreen = False

        # Brick Configuration
        self.rows = 5
        self.cols = 12

        # Game State
        self.score = 0
        self.balls_left = 3
        self.bricks_left = 0
        self.game_over = False
        self.ai_mode = False

        # Input States
        self.left_pressed = False
        self.right_pressed = False

        # Physics
        self.ball_speed = 7
        self.dx = self.ball_speed
        self.dy = -self.ball_speed

        self.paddle_width = int(self.width * 0.16)
        self.paddle_height = 14
        self.paddle_speed = 12

        self.planner = AStarPaddlePlanner(
            self.paddle_width, self.paddle_speed
        )

        # Control Panel Header
        self.control_frame = tk.Frame(root, bg="#0d1117", pady=8)
        self.control_frame.pack(fill="x")

        self.btn_manual = tk.Button(
            self.control_frame,
            text="🕹️ Manual",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.set_manual_mode,
        )
        self.btn_manual.pack(side="left", padx=(20, 5))

        self.btn_auto = tk.Button(
            self.control_frame,
            text="🤖 A* Search AI",
            font=("Helvetica", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.set_auto_mode,
        )
        self.btn_auto.pack(side="left", padx=5)

        self.btn_fullscreen = tk.Button(
            self.control_frame,
            text="⛶ Fullscreen",
            font=("Helvetica", 10, "bold"),
            bg="#21262d",
            fg="#ffffff",
            activebackground="#30363d",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.toggle_fullscreen,
        )
        self.btn_fullscreen.pack(side="left", padx=5)

        self.btn_restart = tk.Button(
            self.control_frame,
            text="🔄 Restart",
            font=("Helvetica", 10, "bold"),
            bg="#30363d",
            fg="#ffffff",
            activebackground="#484f58",
            activeforeground="#ffffff",
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=4,
            command=self.restart_game,
        )
        self.btn_restart.pack(side="right", padx=(5, 20))

        # Main Dynamic Canvas
        self.canvas = tk.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#0d1117",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Keyboard & Mouse Bindings
        self.root.bind("<Left>", lambda e: self.set_key_state("left", True))
        self.root.bind("<Right>", lambda e: self.set_key_state("right", True))
        self.root.bind(
            "<KeyRelease-Left>", lambda e: self.set_key_state("left", False)
        )
        self.root.bind(
            "<KeyRelease-Right>", lambda e: self.set_key_state("right", False)
        )

        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<f>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda e: self.exit_fullscreen())

        self.canvas.bind("<Configure>", self.on_canvas_resize)
        self.canvas.bind("<Motion>", self.mouse_move)

        self.init_game()
        self.update_button_styles()
        self.game_loop()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes("-fullscreen", self.is_fullscreen)
        if self.is_fullscreen:
            self.btn_fullscreen.config(bg="#34a853", text="🗗 Exit Fullscreen")
        else:
            self.btn_fullscreen.config(bg="#21262d", text="⛶ Fullscreen")

    def exit_fullscreen(self):
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes("-fullscreen", False)
            self.btn_fullscreen.config(bg="#21262d", text="⛶ Fullscreen")

    def on_canvas_resize(self, event):
        """Dynamically rescales HUD, paddle, and bricks when entering/exiting fullscreen."""
        if event.width <= 20 or event.height <= 20:
            return

        self.width = event.width
        self.height = event.height

        # Rescale Paddle Width dynamically based on screen size
        self.paddle_width = max(90, int(self.width * 0.16))

        # Re-center HUD text
        self.canvas.coords(self.hud_text, self.width // 2, 20)
        self.canvas.coords(self.mode_text, self.width // 2, 42)

        # Reposition paddle relative to new height
        if hasattr(self, "paddle"):
            p_coords = self.canvas.coords(self.paddle)
            if p_coords:
                cur_x = p_coords[0]
                new_x = min(cur_x, self.width - self.paddle_width - 10)
                py = self.height - 40
                self.canvas.coords(
                    self.paddle,
                    new_x,
                    py,
                    new_x + self.paddle_width,
                    py + self.paddle_height,
                )

        # Re-fit remaining bricks to span the entire updated screen width
        self.refit_bricks()

    def set_manual_mode(self):
        self.ai_mode = False
        self.update_button_styles()
        self.update_hud()

    def set_auto_mode(self):
        self.ai_mode = True
        self.update_button_styles()
        self.update_hud()

    def update_button_styles(self):
        if self.ai_mode:
            self.btn_auto.config(
                bg="#00ffcc",
                fg="#000000",
                activebackground="#00cca3",
                activeforeground="#000000",
            )
            self.btn_manual.config(
                bg="#21262d",
                fg="#8b949e",
                activebackground="#30363d",
                activeforeground="#ffffff",
            )
        else:
            self.btn_manual.config(
                bg="#ffcc00",
                fg="#000000",
                activebackground="#e6b800",
                activeforeground="#000000",
            )
            self.btn_auto.config(
                bg="#21262d",
                fg="#8b949e",
                activebackground="#30363d",
                activeforeground="#ffffff",
            )

    def set_key_state(self, key, state):
        if key == "left":
            self.left_pressed = state
        elif key == "right":
            self.right_pressed = state

    def mouse_move(self, event):
        if not self.ai_mode and not self.game_over:
            px = event.x - (self.paddle_width / 2)
            px = max(10, min(px, self.width - self.paddle_width - 10))
            self.canvas.coords(
                self.paddle,
                px,
                self.height - 40,
                px + self.paddle_width,
                self.height - 40 + self.paddle_height,
            )

    def init_game(self):
        self.canvas.delete("all")
        self.score = 0
        self.balls_left = 3
        self.game_over = False

        self.hud_text = self.canvas.create_text(
            self.width // 2,
            20,
            text="",
            fill="#ffffff",
            font=("Helvetica", 11, "bold"),
        )
        self.mode_text = self.canvas.create_text(
            self.width // 2,
            42,
            text="",
            fill="#00ffcc",
            font=("Helvetica", 10, "bold"),
        )

        px = (self.width - self.paddle_width) / 2
        py = self.height - 40
        self.paddle = self.canvas.create_rectangle(
            px,
            py,
            px + self.paddle_width,
            py + self.paddle_height,
            fill="#4285f4",
            outline="#ffffff",
        )

        self.bricks_grid = {}
        self.create_bricks()
        self.reset_ball()

    def create_bricks(self):
        """Creates initial grid of bricks mapped by (row, col) matrix indices."""
        colors = ["#ea4335", "#fbbc05", "#34a853", "#4285f4", "#a142f4"]
        margin = 30
        brick_w = (self.width - (margin * 2)) / self.cols
        brick_h = max(22, int(self.height * 0.04))

        self.bricks_grid = {}

        for r in range(self.rows):
            for c in range(self.cols):
                x1 = margin + c * brick_w + 3
                y1 = 70 + r * brick_h + 3
                x2 = x1 + brick_w - 6
                y2 = y1 + brick_h - 6

                brick_id = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill=colors[r % len(colors)], outline=""
                )
                self.bricks_grid[(r, c)] = brick_id

        self.bricks_left = len(self.bricks_grid)
        self.update_hud()

    def refit_bricks(self):
        """Recalculates coordinates for all active bricks to seamlessly fill the new screen width."""
        if not hasattr(self, "bricks_grid") or not self.bricks_grid:
            return

        margin = 30
        brick_w = (self.width - (margin * 2)) / self.cols
        brick_h = max(22, int(self.height * 0.04))

        for (r, c), brick_id in self.bricks_grid.items():
            x1 = margin + c * brick_w + 3
            y1 = 70 + r * brick_h + 3
            x2 = x1 + brick_w - 6
            y2 = y1 + brick_h - 6
            self.canvas.coords(brick_id, x1, y1, x2, y2)

    def reset_ball(self):
        p_coords = self.canvas.coords(self.paddle)
        p_center = (p_coords[0] + p_coords[2]) / 2
        r = 8

        if hasattr(self, "ball"):
            self.canvas.delete(self.ball)

        self.ball = self.canvas.create_oval(
            p_center - r,
            p_coords[1] - 2 * r,
            p_center + r,
            p_coords[1],
            fill="#ffffff",
            outline="",
        )
        self.dx = random.choice([-self.ball_speed, self.ball_speed])
        self.dy = -self.ball_speed

    def update_hud(self):
        mode_str = "A* SEARCH (AI)" if self.ai_mode else "MANUAL (HUMAN)"
        self.canvas.itemconfig(
            self.hud_text,
            text=f"Score: {self.score}   |   Balls: {self.balls_left}   |   Bricks: {self.bricks_left}",
        )
        self.canvas.itemconfig(
            self.mode_text,
            text=f"Current Mode: {mode_str}",
            fill="#00ffcc" if self.ai_mode else "#ffcc00",
        )

    def run_human_controller(self):
        paddle_coords = self.canvas.coords(self.paddle)
        if not paddle_coords:
            return

        if self.left_pressed and paddle_coords[0] > 10:
            self.canvas.move(self.paddle, -self.paddle_speed, 0)
        if self.right_pressed and paddle_coords[2] < self.width - 10:
            self.canvas.move(self.paddle, self.paddle_speed, 0)

    def run_ai_controller(self):
        ball_coords = self.canvas.coords(self.ball)
        paddle_coords = self.canvas.coords(self.paddle)

        if not ball_coords or not paddle_coords:
            return

        ball_x = (ball_coords[0] + ball_coords[2]) / 2
        ball_y = (ball_coords[1] + ball_coords[3]) / 2
        paddle_x = paddle_coords[0]
        paddle_y = paddle_coords[1]

        target_x = self.planner.predict_ball_landing_x(
            ball_x, ball_y, self.dx, self.dy, paddle_y, self.width
        )
        path = self.planner.solve_path(
            paddle_x, target_x, self.width, self.paddle_width
        )

        if path:
            action = path[0]
            if action == -1 and paddle_coords[0] > 10:
                self.canvas.move(self.paddle, -self.paddle_speed, 0)
            elif action == 1 and paddle_coords[2] < self.width - 10:
                self.canvas.move(self.paddle, self.paddle_speed, 0)

    def update_physics(self):
        self.canvas.move(self.ball, self.dx, self.dy)
        ball_coords = self.canvas.coords(self.ball)
        paddle_coords = self.canvas.coords(self.paddle)

        if not ball_coords or not paddle_coords:
            return

        # Screen Boundary Collisions
        if ball_coords[0] <= 0 or ball_coords[2] >= self.width:
            self.dx = -self.dx

        if ball_coords[1] <= 60:
            self.dy = -self.dy

        # Loss Check
        if ball_coords[3] >= self.height:
            self.balls_left -= 1
            self.update_hud()
            if self.balls_left <= 0:
                self.end_game("GAME OVER")
            else:
                self.reset_ball()
            return

        # Paddle Collision
        if (
            ball_coords[2] >= paddle_coords[0]
            and ball_coords[0] <= paddle_coords[2]
            and ball_coords[3] >= paddle_coords[1]
            and ball_coords[1] <= paddle_coords[3]
        ):
            self.dy = -abs(self.dy)

        # Brick Collisions
        hit_key = None
        for key, brick_id in list(self.bricks_grid.items()):
            b = self.canvas.coords(brick_id)
            if not b:
                continue
            if (
                ball_coords[2] >= b[0]
                and ball_coords[0] <= b[2]
                and ball_coords[3] >= b[1]
                and ball_coords[1] <= b[3]
            ):
                self.canvas.delete(brick_id)
                hit_key = key
                self.dy = -self.dy
                self.score += 10
                break

        if hit_key:
            del self.bricks_grid[hit_key]
            self.bricks_left = len(self.bricks_grid)
            self.update_hud()

            if not self.bricks_grid:
                self.end_game("VICTORY!")

    def end_game(self, text):
        self.game_over = True
        self.canvas.create_text(
            self.width // 2,
            self.height // 2,
            text=text,
            fill="#00ffcc",
            font=("Helvetica", 32, "bold"),
        )

    def restart_game(self):
        self.init_game()
        self.update_hud()

    def game_loop(self):
        if not self.game_over:
            if self.ai_mode:
                self.run_ai_controller()
            else:
                self.run_human_controller()
            self.update_physics()
        self.root.after(20, self.game_loop)


if __name__ == "__main__":
    root = tk.Tk()
    game = DualModeBreakoutGame(root)
    root.mainloop()