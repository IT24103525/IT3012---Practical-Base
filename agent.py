from collections import deque
import heapq


class SearchAgent:
    """
    Goal Based Search Agent
    Supports BFS, DFS and UCS
    """

    def __init__(self):
        self.plan = []
        self.active_algo = "BFS"

        self.current_pos = (0, 0)


    def get_neighbors(self, state, grid_size, walls):

        x, y = state

        width, height = grid_size


        actions = [
            ("Up", (x, y + 1)),
            ("Down", (x, y - 1)),
            ("Left", (x - 1, y)),
            ("Right", (x + 1, y))
        ]


        result = []


        for action, next_state in actions:

            nx, ny = next_state


            if (
                0 <= nx < width
                and 0 <= ny < height
                and next_state not in walls
            ):
                result.append(
                    (action, next_state)
                )


        return result



    # -------------------------
    # BFS
    # -------------------------

    def bfs_search(
            self,
            start,
            goal,
            grid_size,
            walls):


        queue = deque()

        queue.append(
            (start, [])
        )


        reached = {start}


        while queue:

            state, path = queue.popleft()


            if state == goal:
                return path



            for action, next_state in self.get_neighbors(
                    state,
                    grid_size,
                    walls):


                if next_state not in reached:

                    reached.add(next_state)


                    queue.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )


        return []



    # -------------------------
    # DFS
    # -------------------------

    def dfs_search(
            self,
            start,
            goal,
            grid_size,
            walls):


        stack = []

        stack.append(
            (start, [])
        )


        reached = {start}



        while stack:

            state, path = stack.pop()


            if state == goal:
                return path



            for action, next_state in self.get_neighbors(
                    state,
                    grid_size,
                    walls):


                if next_state not in reached:

                    reached.add(next_state)


                    stack.append(
                        (
                            next_state,
                            path + [action]
                        )
                    )


        return []



    # -------------------------
    # UCS
    # -------------------------

    def ucs_search(
            self,
            start,
            goal,
            grid_size,
            walls):


        priority_queue = []


        heapq.heappush(
            priority_queue,
            (
                0,
                start,
                []
            )
        )


        reached = {
            start: 0
        }



        while priority_queue:


            cost, state, path = heapq.heappop(
                priority_queue
            )


            if state == goal:
                return path



            for action, next_state in self.get_neighbors(
                    state,
                    grid_size,
                    walls):


                new_cost = cost + 1



                if (
                    next_state not in reached
                    or new_cost < reached[next_state]
                ):

                    reached[next_state] = new_cost


                    heapq.heappush(
                        priority_queue,
                        (
                            new_cost,
                            next_state,
                            path + [action]
                        )
                    )


        return []



    # -------------------------
    # Select nearest food
    # -------------------------

    def find_food(self, food_list):

        if not food_list:
            return None


        x, y = self.current_pos


        return min(
            food_list,
            key=lambda food:
            abs(food[0]-x)
            +
            abs(food[1]-y)
        )



    # -------------------------
    # Update internal position
    # -------------------------

    def update_position(self, action):

        x, y = self.current_pos


        if action == "Up":
            self.current_pos = (
                x,
                y+1
            )


        elif action == "Down":

            self.current_pos = (
                x,
                y-1
            )


        elif action == "Left":

            self.current_pos = (
                x-1,
                y
            )


        elif action == "Right":

            self.current_pos = (
                x+1,
                y
            )



    # -------------------------
    # Agent decision
    # -------------------------

    def sense_and_act(self, percept):


        self.current_pos = tuple(
            percept["agent_pos"]
        )


        grid_size = percept["grid_size"]


        walls = set(
            tuple(w)
            for w in percept["walls"]
        )


        food = [
            tuple(f)
            for f in percept["all_food"]
        ]



        if not self.plan:


            goal = self.find_food(food)



            if goal is None:
                return "Stay"



            if self.active_algo == "BFS":

                self.plan = self.bfs_search(
                    self.current_pos,
                    goal,
                    grid_size,
                    walls
                )


            elif self.active_algo == "DFS":

                self.plan = self.dfs_search(
                    self.current_pos,
                    goal,
                    grid_size,
                    walls
                )


            elif self.active_algo == "UCS":

                self.plan = self.ucs_search(
                    self.current_pos,
                    goal,
                    grid_size,
                    walls
                )



        if not self.plan:

            return "Stay"



        action = self.plan.pop(0)


        self.update_position(action)


        return action