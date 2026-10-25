from dataclasses import dataclass

#yardımcı veri yapıları

@dataclass
class Successor:
    action: str
    cost: float
    state: str

@dataclass
class Step:
    action: str
    cost: float
    state: str

@dataclass
class Solution:
    steps: list
    total_cost: float

@dataclass
class Backpointer:
    prev_state: str
    action: str
    cost: float

class SearchProblem:
    """üst sınıf: her arama problemi bu üç metodu sağlar."""

    def start_state(self):
        raise NotImplementedError #raise NotImplementedError, alt sınıfın bunları doldurması gerektiğini söyler.

    def is_end(self, state):
        raise NotImplementedError

    def successors(self, state):
        raise NotImplementedError

class PriorityQueue:
    """ucs için öncelik kuyruğu (sınır bölgesi / frontier).

    dışarıdan hiçbir modül yok (heapq gibi): bekleyen durumları 
    bir sözlükte (durum -> öncelik tutar), en küçüğü bulmak için sözlüğü tarar.
    """

    def __init__(self):
        self.priorities = {} #bekleyen durumlar: durum->en düşük bilinen öncelik
        self.removed = set() #kuyruktan çıkarılıp kesinleşen durumlar

    def update(self, state, new_priority):
        """daha iyi bir yol bulunduysa günceller ve true döner."""
        if state in self.removed:
            return False
        old = self.priorities.get(state)
        if old is None or new_priority < old:
            self.priorities[state] = new_priority
            return True
        return False

    def remove_min(self):
        """en düşük öncelikli durumu çıkarır. kuyruk boşsa (none, none)."""
        if not self.priorities:
            return None, None
        min_state = None
        min_priority = None
        for state, priority in self.priorities.items():
            if min_priority is None or priority < min_priority:
                min_state = state
                min_priority = priority
            del self.priorities[min_state]
            self.removed.add(min_state)
            return min_state, min_priority

# PROBLEM TANIMI

class DiamondSearchProblem(SearchProblem):
    def __init__(self):
        # state -> state -> cost
        self.graph = {
            "A": {"B": 1, "C": 100},
            "B": {"A": 1, "C": 1, "D": 100},
            "C": {"A": 100, "B": 1, "D": 1},
            "D": {"B": 100, "C": 1},
        }

    def start_state(self):
        return "A"

    def is_end(self, state):
        return "D"

    def successors(self, state):
        return [
            Successor(action=neighbor, cost=cost, state=neighbor)
            for neighbor, cost in self.graph[state].items()
        ]

# UNIFORM COST SEARCH (DIJKSTRA)

def uniform_cost_search(problem: SearchProblem):
    frontier = PriorityQueue()
    backpointers = {}
    num_explored = 0

    start_state = problem.start_state()
    frontier.update(start_state, 0)

    while True:
        #sınırdan en ucuz durumu al
        state, past_cost = frontier.remove_min()
        if state is None:
            return None, num_explored #çözüm yok
        num_explored += 1

        #hedefe ulaştık mı? geriye doğru yolu kur.
        if problem.is_end(state):
            steps = []
            total_cost = past_cost
            while state != start_state:
                bp = backpointers[state]
                steps.insert(0, Step(bp.action, bp.cost, state))
                state = bp.prev_state
            return Solution(steps=steps, total_cost=total_cost), num_explored

        #sınır bölgesini genişlet
        for successor in problem.successors(state):
            if frontier.update(successor.state, past_cost + successor.cost):
                #bu duruma daha iyi bir yol bulduk -> backpointer ile güncelle
                backpointers[successor.state] = Backpointer(
                    prev_state=state, action=successor.action, cost=successor.cost
                )

if __name__ == "__main__":
    problem = DiamondSearchProblem()

    print(problem.successors("A"))

    solution, num_explored = uniform_cost_search(problem)
    print("keşfedilen durum sayısı:", num_explored)
    if solution:
        print("toplam maliyet:", solution.total_cost)
        for step in solution.steps:
            print(f"{step.state} (eylem: {step.action}, maliyet: {step.cost})")
    else:
        print("çözüm bulunamadı.")