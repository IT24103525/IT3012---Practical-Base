from collections import deque
import heapq
import math


class SearchAgent:
    """Goal-based search agent using BFS, DFS, UCS, or A*."""

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # Default search algorithm

    def get_neighbors(self, state, grid_size, walls):
        """Return valid neighboring states and the action to reach them."""

        x, y = state
        width, height = grid_size

        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        neighbors = []

        for action, new_state in moves:
            nx, ny = new_state

            # Check grid boundaries
            if 0 <= nx < width and 0 <= ny < height:

                # Check that the new cell is not a wall
                if new_state not in walls:
                    neighbors.append((new_state, action))

        return neighbors

    # ---------------------------------------------------------
    # HEURISTIC FUNCTIONS - PRACTICAL 04
    # ---------------------------------------------------------

    def manhattan_distance(self, pos, goal):
        """Calculate Manhattan distance between two positions."""

        return (
            abs(pos[0] - goal[0])
            + abs(pos[1] - goal[1])
        )

    def euclidean_distance(self, pos, goal):
        """Calculate Euclidean distance between two positions."""

        return math.sqrt(
            (pos[0] - goal[0]) ** 2
            + (pos[1] - goal[1]) ** 2
        )

    # ---------------------------------------------------------
    # BFS
    # ---------------------------------------------------------

    def bfs_search(self, start, goal, grid_size, walls):
        """Breadth-First Search."""

        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:

            state, path = frontier.popleft()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ---------------------------------------------------------
    # DFS
    # ---------------------------------------------------------

    def dfs_search(self, start, goal, grid_size, walls):
        """Depth-First Search."""

        frontier = []
        frontier.append((start, []))

        reached = {start}

        while frontier:

            state, path = frontier.pop()

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):

                if next_state not in reached:

                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append(
                        (next_state, new_path)
                    )

        return []

    # ---------------------------------------------------------
    # UCS
    # ---------------------------------------------------------

    def ucs_search(self, start, goal, grid_size, walls):
        """Uniform-Cost Search."""

        # (cost, state, path)
        frontier = []

        heapq.heappush(
            frontier,
            (0, start, [])
        )

        # Store the cheapest known cost for each state
        reached = {
            start: 0
        }

        while frontier:

            cost, state, path = heapq.heappop(frontier)

            if state == goal:
                return path

            for next_state, action in self.get_neighbors(
                state, grid_size, walls
            ):

                new_cost = cost + 1

                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_cost,
                            next_state,
                            new_path
                        )
                    )

        return []

    # ---------------------------------------------------------
    # A* SEARCH - PRACTICAL 04
    # ---------------------------------------------------------

    def astar_search(
        self,
        start_pos,
        goal_pos,
        walls,
        grid_size,
        heuristic_type='manhattan'
    ):
        """A* Search using g(n) + h(n)."""

        # Select the heuristic function
        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else:
            heuristic = self.manhattan_distance

        # Priority queue
        frontier = []

        # States that have already been reached
        reached_states = set()

        # Starting node
        start_g = 0
        start_h = heuristic(start_pos, goal_pos)
        start_f = start_g + start_h

        # (f_cost, g_cost, current_pos, path_taken)
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

            f_cost, g_cost, current_pos, path_taken = (
                heapq.heappop(frontier)
            )

            # Goal reached
            if current_pos == goal_pos:
                return path_taken

            # Skip states that have already been reached
            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            # Expand neighboring states
            for next_state, action in self.get_neighbors(
                current_pos,
                grid_size,
                walls
            ):

                # Skip already reached states
                if next_state in reached_states:
                    continue

                # Cost to reach the neighbor
                new_g = g_cost + 1

                # Estimated cost from neighbor to goal
                new_h = heuristic(
                    next_state,
                    goal_pos
                )

                # A* evaluation function
                new_f = new_g + new_h

                # Add action to the path
                new_path = path_taken + [action]

                # Add neighbor to priority queue
                heapq.heappush(
                    frontier,
                    (
                        new_f,
                        new_g,
                        next_state,
                        new_path
                    )
                )

        # No path found
        return []

    # ---------------------------------------------------------
    # Agent decision
    # ---------------------------------------------------------

    def sense_and_act(self, percept):
        """Create a plan when necessary and execute it one action at a time."""

        # If there is no existing plan, create one.
        if not self.plan:

            start = tuple(percept['agent_pos'])

            food_positions = percept['all_food']

            # No food left
            if not food_positions:
                return 'Up'

            # Find the closest food using Manhattan distance
            goal = min(
                food_positions,
                key=lambda position:
                abs(position[0] - start[0])
                + abs(position[1] - start[1])
            )

            grid_size = percept['grid_size']

            walls = set(percept['walls'])

            # Select the search algorithm
            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    start_pos=start,
                    goal_pos=goal,
                    walls=walls,
                    grid_size=grid_size,
                    heuristic_type='manhattan'
                )

        # Execute the first action in the plan
        if self.plan:
            return self.plan.pop(0)

        # Fallback if no path was found
        return 'Up'