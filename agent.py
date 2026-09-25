from collections import deque
import heapq
import math

from logic_engine import KnowledgeBase


class SearchAgent:
    """Search agent using BFS, DFS, UCS and A* with a Knowledge Base."""

    def __init__(self):

        self.plan = []
        self.active_algo = "AStar"

# Knowledge Base


        self.kb = KnowledgeBase()

        self.kb.tell_rule(
            ["TargetVisible", "HasDust"],
            "SafeToEngage"
        )

        self.kb.tell_rule(
            [
                "SafeToEngage",
                "BloodseekerMissing"
            ],
            "Retreat"
        )

# NEIGHBORS

    def get_neighbors(
        self,
        state,
        grid_size,
        walls
    ):

        x, y = state

        width, height = grid_size

        moves = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y))
        ]

        neighbors = []

        for action, new_state in moves:

            nx, ny = new_state

            if (
                0 <= nx < width
                and 0 <= ny < height
                and new_state not in walls
            ):
                neighbors.append(
                    (new_state, action)
                )

        return neighbors

# HEURISTICS

    def manhattan_distance(
        self,
        pos,
        goal
    ):

        return (
            abs(pos[0] - goal[0])
            +
            abs(pos[1] - goal[1])
        )

    def euclidean_distance(
        self,
        pos,
        goal
    ):

        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            +
            (pos[1] - goal[1]) ** 2
        )

# BFS

    def bfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = deque(
            [(start, [])]
        )

        reached = {start}

        while frontier:

            state, path = frontier.popleft()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(
                        next_state
                    )

                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )

        return []

    # DFS

    def dfs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = [
            (start, [])
        ]

        reached = {start}

        while frontier:

            state, path = frontier.pop()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                if next_state not in reached:

                    reached.add(
                        next_state
                    )

                    frontier.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )

        return []

# UCS

    def ucs_search(
        self,
        start,
        goal,
        grid_size,
        walls
    ):

        frontier = []

        heapq.heappush(
            frontier,
            (0, start, [])
        )

        reached = {
            start: 0
        }

        while frontier:

            cost, state, path = (
                heapq.heappop(frontier)
            )

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state,
                grid_size,
                walls
            ):

                new_cost = cost + 1

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            path + [action]
                        )
                    )

        return []

# CHECK LOGICAL FEASIBILITY

    def is_feasible(
        self,
        position,
        tile_facts
    ):
        """
        Ask the Knowledge Base whether a tile
        should be treated as logically infeasible.
        """

        self.kb.clear_facts()

        facts = tile_facts.get(
            position,
            []
        )

        for fact in facts:
            self.kb.tell_fact(fact)

        self.kb.forward_chain()

        if "Retreat" in self.kb.facts:
            return False

        return True

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        tile_facts,
        heuristic_type="manhattan"
    ):

        if heuristic_type == "euclidean":
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        frontier = []

        reached_states = set()

        start_g = 0

        start_h = heuristic(
            start_pos,
            goal_pos
        )

        start_f = (
            start_g
            + start_h
        )

        heapq.heappush(
            frontier,
            (
                start_f,
                start_g,
                start_pos,
                []
            )
        )

        while frontier:

            (
                f_cost,
                g_cost,
                current_pos,
                path_taken
            ) = heapq.heappop(frontier)

            if current_pos == goal_pos:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(
                current_pos
            )

            for next_state, action in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                if next_state in reached_states:
                    continue

                if not self.is_feasible(
                    next_state,
                    tile_facts
                ):
                    continue

                new_g = (
                    g_cost
                    + 1
                )

                new_h = heuristic(
                    next_state,
                    goal_pos
                )

                new_f = (
                    new_g
                    + new_h
                )

                new_path = (
                    path_taken
                    + [action]
                )

                heapq.heappush(
                    frontier,
                    (
                        new_f,
                        new_g,
                        next_state,
                        new_path
                    )
                )

        return []

# AGENT DECISION LOOP


    def sense_and_act(
        self,
        percept
    ):

        if not self.plan:

            start = tuple(
                percept["agent_pos"]
            )

            food_positions = [
                tuple(food)
                for food in percept["all_food"]
            ]

            if not food_positions:
                return "Stay"

            goal = min(
                food_positions,

                key=lambda food:
                self.manhattan_distance(
                    start,
                    food
                )
            )

            grid_size = tuple(
                percept["grid_size"]
            )

            walls = set(
                tuple(wall)
                for wall in percept["walls"]
            )

            tile_facts = (
                percept.get(
                    "tile_facts",
                    {}
                )
            )

            if self.active_algo == "BFS":

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "DFS":

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "UCS":

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == "AStar":

                self.plan = self.astar_search(
                    start_pos=start,
                    goal_pos=goal,
                    walls=walls,
                    grid_size=grid_size,
                    tile_facts=tile_facts,
                    heuristic_type="manhattan"
                )

        if self.plan:
            return self.plan.pop(0)

        return "Stay"