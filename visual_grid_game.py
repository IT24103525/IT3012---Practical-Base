import random
import tkinter as tk
from agent import SearchAgent

class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents, toxic traps and agent architectures."""

    def __init__(
        self,
        width=10,
        height=10,
        num_food=10,
        num_opponents=2,
        custom_walls=None
    ):
        self.width = width
        self.height = height

        # Starting position
        self.agent_pos = [0, 0]

        # Agent starts facing Up
        self.agent_direction = "Up"

        # Walls
        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            self.walls = {
                (2, 2),
                (2, 3),
                (5, 5),
                (6, 5),
                (3, 7)
            }

        # Generate food

        self.food_positions = set()

        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)

            food_pos = (fx, fy)

            if (
                food_pos != (0, 0)
                and food_pos not in self.walls
            ):
                self.food_positions.add(food_pos)

        # LAB 01: Generate toxic traps

        self.toxic_traps = set()

        while len(self.toxic_traps) < 3:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)

            trap_pos = (tx, ty)

            if (
                trap_pos != (0, 0)
                and trap_pos not in self.walls
                and trap_pos not in self.food_positions
            ):
                self.toxic_traps.add(trap_pos)

        # Generate opponents

        self.opponents = []

        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)

            op_pos = [ox, oy]
            op_tuple = tuple(op_pos)

            if (
                op_tuple != (0, 0)
                and op_tuple not in self.walls
                and op_tuple not in self.food_positions
                and op_tuple not in self.toxic_traps
            ):
                self.opponents.append(op_pos)

        self.score = 0
        self.steps = 0
        self.collision = False

    # Helper method: Get cell in front of agent

    def get_ahead_position(self):
        x, y = self.agent_pos

        if self.agent_direction == "Up":
            return (x, y + 1)

        elif self.agent_direction == "Down":
            return (x, y - 1)

        elif self.agent_direction == "Left":
            return (x - 1, y)

        elif self.agent_direction == "Right":
            return (x + 1, y)

        return (x, y)

    # LAB 02 - Step 1.1
    # Partial Observable Perception

    def get_percept(self) -> dict:

        ahead_x, ahead_y = self.get_ahead_position()

        # Check whether forward position is outside grid
        outside_grid = (
            ahead_x < 0
            or ahead_x >= self.width
            or ahead_y < 0
            or ahead_y >= self.height
        )

        wall_ahead = (
            outside_grid
            or (ahead_x, ahead_y) in self.walls
        )

        food_here = (
            tuple(self.agent_pos)
            in self.food_positions
        )

        # LAB 01 toxic sensor
        smells_toxin = (
            tuple(self.agent_pos)
            in self.toxic_traps
        )

        # IMPORTANT:
        # agent_pos is NOT returned.
        # Only local Boolean information is returned.
        return {

            "agent_pos": tuple(self.agent_pos),
            "wall_ahead": wall_ahead,
            "food_here": food_here,
            "smells_toxin": smells_toxin,

            "grid_size": (
                self.width,
                self.height
            ),

            "walls": list(
                self.walls
            ),

            "all_food": list(
                self.food_positions
            )
        }

    # Turn agent left

    def turn_left(self):

        directions = ["Up", "Left", "Down", "Right"]

        current_index = directions.index(
            self.agent_direction
        )

        self.agent_direction = directions[
            (current_index + 1) % 4
        ]

    # Turn agent right

    def turn_right(self):

        directions = ["Up", "Right", "Down", "Left"]

        current_index = directions.index(
            self.agent_direction
        )

        self.agent_direction = directions[
            (current_index + 1) % 4
        ]

    # Execute an action

    def execute_action(self, action: str):

        self.steps += 1

        old_pos = list(self.agent_pos)

        # Turn actions

        if action == "TurnLeft":
            self.turn_left()

        elif action == "TurnRight":
            self.turn_right()

        # Move forward according to facing direction

        elif action == "MoveForward":

            next_x, next_y = self.get_ahead_position()

            # Check grid boundary
            outside_grid = (
                next_x < 0
                or next_x >= self.width
                or next_y < 0
                or next_y >= self.height
            )

            if (
                outside_grid
                or (next_x, next_y) in self.walls
            ):
                # Wall penalty
                self.score -= 5

            else:
                self.agent_pos = [
                    next_x,
                    next_y
                ]

        # Keep support for original actions

        elif action in ["Up", "Down", "Left", "Right"]:

            self.agent_direction = action

            next_x, next_y = self.get_ahead_position()

            outside_grid = (
                next_x < 0
                or next_x >= self.width
                or next_y < 0
                or next_y >= self.height
            )

            if (
                outside_grid
                or (next_x, next_y) in self.walls
            ):
                self.score -= 5

            else:
                self.agent_pos = [
                    next_x,
                    next_y
                ]

        # Food reward

        current_pos = tuple(self.agent_pos)

        if current_pos in self.food_positions:
            self.food_positions.remove(current_pos)
            self.score += 20

        # LAB 01 Toxic Trap Penalty
        # Only penalize when agent enters trap

        moved = old_pos != self.agent_pos

        if (
            moved
            and current_pos in self.toxic_traps
        ):
            self.score -= 15

        # Move opponents

        for op in self.opponents:

            move = random.choice(
                ["Up", "Down", "Left", "Right", "Stay"]
            )

            old_op = list(op)

            if move == "Up":
                op[1] += 1

            elif move == "Down":
                op[1] -= 1

            elif move == "Left":
                op[0] -= 1

            elif move == "Right":
                op[0] += 1

            # Prevent opponent leaving grid
            if (
                op[0] < 0
                or op[0] >= self.width
                or op[1] < 0
                or op[1] >= self.height
            ):
                op[:] = old_op

            # Prevent opponent entering wall
            elif tuple(op) in self.walls:
                op[:] = old_op

            # Collision
            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:

        return (
            len(self.food_positions) == 0
            or self.steps >= 60
            or self.collision
        )

# LAB 02 - Step 1.2
# SIMPLE REFLEX AGENT
class SimpleReflexAgent:
    """
    Simple Reflex Agent.

    Uses only the CURRENT percept.
    No history or internal memory is stored.
    """

    def sense_and_act(self, percept):

        # Condition-Action Rule 1
        # IF toxin detected THEN turn
        if percept["smells_toxin"]:
            return "TurnRight"

        # Condition-Action Rule 2
        # IF wall ahead THEN turn left
        if percept["wall_ahead"]:
            return "TurnLeft"

        # ELSE move forward
        return "MoveForward"

# LAB 02 - Step 1.3
# MODEL-BASED AGENT

class ModelBasedAgent:
    """
    Model-Based Agent. Maintains an internal state using:
    - relative position
    - facing direction
    - visited cells
    - blocked cells
    - previous percept
    - last action
    """

    def __init__(self):

        # Internal relative position.
        # The agent does NOT receive the real global agent_pos.
        self.relative_pos = (0, 0)

        # Internal estimate of facing direction.
        self.direction = "Up"

        # Memory
        self.visited_cells = {(0, 0)}
        self.blocked_cells = set()

        # Previous information
        self.last_action = None
        self.last_percept = None

    # Get next relative position

    def position_in_direction(
        self,
        position,
        direction
    ):
        x, y = position

        if direction == "Up":
            return (x, y + 1)

        elif direction == "Down":
            return (x, y - 1)

        elif direction == "Left":
            return (x - 1, y)

        elif direction == "Right":
            return (x + 1, y)

        return position

    # Get left direction

    def left_direction(self):

        turns = {
            "Up": "Left",
            "Left": "Down",
            "Down": "Right",
            "Right": "Up"
        }

        return turns[self.direction]

    # Get right direction

    def right_direction(self):

        turns = {
            "Up": "Right",
            "Right": "Down",
            "Down": "Left",
            "Left": "Up"
        }

        return turns[self.direction]

    # Update Internal State
    # Transition Model + Previous Action

    def update_state(self):

        if self.last_action is None:
            return

        # Previous action was TurnLeft
        if self.last_action == "TurnLeft":
            self.direction = self.left_direction()

        # Previous action was TurnRight
        elif self.last_action == "TurnRight":
            self.direction = self.right_direction()

        # Previous action was MoveForward
        elif self.last_action == "MoveForward":

            # If previous percept did NOT detect wall,
            # we assume the movement succeeded.
            if (
                self.last_percept is not None
                and not self.last_percept["wall_ahead"]
            ):
                self.relative_pos = (
                    self.position_in_direction(
                        self.relative_pos,
                        self.direction
                    )
                )

                self.visited_cells.add(
                    self.relative_pos
                )

            # If wall was detected,
            # remember that cell as blocked.
            elif self.last_percept is not None:

                blocked_position = (
                    self.position_in_direction(
                        self.relative_pos,
                        self.direction
                    )
                )

                self.blocked_cells.add(
                    blocked_position
                )

    # Select action using percept + memory

    def sense_and_act(self, percept):

        # FIRST:
        # Update internal state using
        # previous action + previous percept
        self.update_state()

        current = self.relative_pos

        forward_position = (
            self.position_in_direction(
                current,
                self.direction
            )
        )

        left_dir = self.left_direction()

        left_position = (
            self.position_in_direction(
                current,
                left_dir
            )
        )

        right_dir = self.right_direction()

        right_position = (
            self.position_in_direction(
                current,
                right_dir
            )
        )

        # SENSOR MODEL
        # Store current percept
        if percept["wall_ahead"]:
            self.blocked_cells.add(
                forward_position
            )

        # Condition-Action Rules using memory


        # IF toxin here THEN turn away
        if percept["smells_toxin"]:
            action = "TurnRight"

        # IF wall ahead AND left already visited
        # THEN turn right
        elif (
            percept["wall_ahead"]
            and left_position in self.visited_cells
        ):
            action = "TurnRight"

        # IF wall ahead THEN turn left
        elif percept["wall_ahead"]:
            action = "TurnLeft"

        # IF forward cell has NOT been visited
        # THEN move forward
        elif (
            forward_position
            not in self.visited_cells
            and forward_position
            not in self.blocked_cells
        ):
            action = "MoveForward"

        # IF left cell is unvisited
        # THEN turn left
        elif (
            left_position
            not in self.visited_cells
            and left_position
            not in self.blocked_cells
        ):
            action = "TurnLeft"

        # IF right cell is unvisited
        # THEN turn right
        elif (
            right_position
            not in self.visited_cells
            and right_position
            not in self.blocked_cells
        ):
            action = "TurnRight"

        # Otherwise choose another direction
        else:
            action = "TurnRight"

        # Save current information for next cycle
        self.last_percept = dict(percept)
        self.last_action = action

        return action

# GUI

class GridGameGUI:

    def __init__(
        self,
        root,
        width=10,
        height=10,
        num_food=12,
        num_opponents=2,
        walls=None
    ):

        self.root = root

        self.root.title(
            "IT3012 - Scalable Multi-Agent Grid Hunt"
        )

        self.env = VisualGridHuntGame(
            width=width,
            height=height,
            num_food=num_food,
            num_opponents=num_opponents,
            custom_walls=walls
        )

        # LAB 02 AGENT

        #self.agent = SimpleReflexAgent()

        self.agent = SearchAgent()

        self.agent.active_algo = "BFS"

        # Canvas setup

        max_canvas_dim = 600

        self.cell_size = max(
            20,
            min(
                max_canvas_dim // self.env.width,
                max_canvas_dim // self.env.height
            )
        )

        canvas_w = (
            self.env.width
            * self.cell_size
        )

        canvas_h = (
            self.env.height
            * self.cell_size
        )

        self.canvas = tk.Canvas(
            root,
            width=canvas_w,
            height=canvas_h,
            bg="white"
        )

        self.canvas.pack()

        self.label = tk.Label(
            root,
            text="Score: 0 | Steps: 0",
            font=("Arial", 14)
        )

        self.label.pack(
            pady=10
        )

        self.btn = tk.Button(
            root,
            text="Start Simulation",
            command=self.run_loop,
            font=("Arial", 12),
            bg="#000066",
            fg="white"
        )

        self.btn.pack(
            pady=5
        )

        self.draw_grid()

    # Draw grid

    def draw_grid(self):

        self.canvas.delete("all")

        # Grid + Walls
        for x in range(self.env.width):

            for y in range(self.env.height):

                x1 = x * self.cell_size

                y1 = (
                    self.env.height
                    - 1
                    - y
                ) * self.cell_size

                x2 = (
                    x1
                    + self.cell_size
                )

                y2 = (
                    y1
                    + self.cell_size
                )

                if (x, y) in self.env.walls:
                    color = "#64748b"
                else:
                    color = "#f1f5f9"

                self.canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=color,
                    outline="#cbd5e1"
                )

                if (
                    self.cell_size >= 40
                    and (x, y) in self.env.walls
                ):
                    self.canvas.create_text(
                        x1 + self.cell_size / 2,
                        y1 + self.cell_size / 2,
                        text="W",
                        fill="white",
                        font=("Arial", 8, "bold")
                    )

        # Food

        for fx, fy in self.env.food_positions:

            offset = self.cell_size * 0.25

            x1 = (
                fx * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - fy
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="#f59e0b",
                outline="#d97706"
            )

        # LAB 01: Toxic traps

        for tx, ty in self.env.toxic_traps:

            offset = self.cell_size * 0.25

            x1 = (
                tx * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - ty
            ) * self.cell_size + offset

            self.canvas.create_oval(
                x1,
                y1,
                x1 + self.cell_size * 0.5,
                y1 + self.cell_size * 0.5,
                fill="purple",
                outline="black"
            )

        # Opponents

        for ox, oy in self.env.opponents:

            offset = self.cell_size * 0.2

            x1 = (
                ox * self.cell_size
                + offset
            )

            y1 = (
                self.env.height
                - 1
                - oy
            ) * self.cell_size + offset

            self.canvas.create_rectangle(
                x1,
                y1,
                x1 + self.cell_size * 0.6,
                y1 + self.cell_size * 0.6,
                fill="#990000",
                outline="#7a0000"
            )

        # Agent

        ax, ay = self.env.agent_pos

        offset = self.cell_size * 0.15

        x1 = (
            ax * self.cell_size
            + offset
        )

        y1 = (
            self.env.height
            - 1
            - ay
        ) * self.cell_size + offset

        self.canvas.create_oval(
            x1,
            y1,
            x1 + self.cell_size * 0.7,
            y1 + self.cell_size * 0.7,
            fill="#000066",
            outline="#1e3a8a"
        )


    # Simulation loop

    def run_loop(self):

        self.btn.config(
            state="disabled"
        )

        def step():

            if not self.env.is_done():

                # Sensors
                percept = (
                    self.env.get_percept()
                )

                # Agent Program
                action = (
                    self.agent.sense_and_act(
                        percept
                    )
                )

                # Actuator
                self.env.execute_action(
                    action
                )

                self.draw_grid()

                self.label.config(
                    text=(
                        f"Score: {self.env.score} | "
                        f"Steps: {self.env.steps} | "
                        f"Direction: {self.env.agent_direction} | "
                        f"Action: {action}"
                    )
                )

                self.root.after(
                    250,
                    step
                )

            else:

                if self.env.collision:

                    end_text = (
                        "Collision! Game Over! "
                        f"Final Score: {self.env.score}"
                    )

                else:

                    end_text = (
                        "Finished! "
                        f"Final Score: {self.env.score}"
                    )

                self.label.config(
                    text=end_text
                )

                self.btn.config(
                    state="normal"
                )

        step()


# Main

if __name__ == "__main__":

    root = tk.Tk()

    app = GridGameGUI(
        root,
        width=12,
        height=12,
        num_food=15,
        num_opponents=0
    )

    root.mainloop()