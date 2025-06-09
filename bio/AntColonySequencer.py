import time
import random


class AntColonySequencer:
    def __init__(self, spectrum, target_length, start_seq, alpha=0.7, beta=0.7, evaporation=0.1, Q=0.5):
        self.spectrum = spectrum
        self.target_length = target_length
        self.start_seq = start_seq
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.Q = Q

        self.k = len(spectrum[0])
        self.pheromone = {oligo: 1.0 for oligo in spectrum}

    def make_pattern(self, sq):
        sq = list(sq)
        for x in range(1, len(sq) - 2, 2):
            sq[x] = 'X'
        return "".join(sq)

    def construct_solution(self):
        path = []
        current_seq = self.start_seq
        current_length = len(current_seq)
        usedOligos = 0
        sqpe = 0

        visited = set()

        while current_length < self.target_length:
            suffix = current_seq[-(self.k - 1):]
            candidates = []
            probabilities = []
            for oligo in self.spectrum:
                if oligo in visited:
                    continue
                suffix = self.make_pattern(suffix)
                a = oligo[:len(suffix)]
                if oligo[:len(suffix)] == suffix:
                    pheromone = self.pheromone[oligo]
                    heuristic = 1.0
                    prob = (pheromone ** self.alpha) * (heuristic ** self.beta)
                    candidates.append(oligo)
                    probabilities.append(prob)

            if not candidates:
                break
            total = sum(probabilities)
            probabilities = [p / total for p in probabilities]

            r = random.random()
            cumulative = 0.0
            selected_oligo = None
            for i, prob in enumerate(probabilities):
                cumulative += prob
                if r <= cumulative:
                    selected_oligo = candidates[i]
                    break

            path.append(selected_oligo)
            visited.add(selected_oligo)
            current_seq += selected_oligo[-1]
            usedOligos += 2
            current_length += 1

        sqpe += (len(self.spectrum) - len(visited)) * 2
        return path, current_seq, usedOligos, sqpe

    def update_pheromones(self, solutions):
        for oligo in self.pheromone:
            self.pheromone[oligo] *= (1.0 - self.evaporation)
            if self.pheromone[oligo] < 0.01:
                self.pheromone[oligo] = 0.01

        for path, seq in solutions:
            reward = self.Q * (len(seq) / self.target_length)
            for oligo in path:
                self.pheromone[oligo] += reward

    def run(self, n_ants=10, n_iterations=100):
        startTime = time.time()
        best_seq = ""
        best_path = []
        whichIteration = 0
        for iteration in range(n_iterations):
            whichAnt = 0
            solutions = []
            for ant in range(n_ants):
                path, seq, lsqpe, lusedOligos = self.construct_solution()
                solutions.append((path, seq))

                if len(seq) > len(best_seq):
                    whichAnt = ant
                    best_seq = seq
                    best_path = path
                    sqpe = lsqpe
                    usedOligos = lusedOligos

            self.update_pheromones(solutions)

            if len(best_seq) >= self.target_length:
                whichIteration = iteration
                break

        finishTime = time.time() - startTime
        return best_seq, best_path, finishTime, usedOligos, sqpe, whichIteration, whichAnt
