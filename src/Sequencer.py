import copy
import time

class Sequencer:
    def __init__(self, S1, S2, N, start):
        self.N = N
        self.start = start
        self.initial_S1 = S1
        self.initial_S2 = S2

    def run(self):
        startTime = time.time()
        result, usedOligos, sqpe = self._build_with_backtrack(self.start, self.initial_S1.copy(), self.initial_S2.copy(), 0, 0)
        finishTime = time.time() - startTime
        return result, sqpe, finishTime, usedOligos

    def _build_with_backtrack(self, sequence, S1, S2, usedOligos, sqpe):
        while len(sequence) < self.N:
            candidates1 = self.find_in_S1(sequence, S1)
            candidates2 = self.find_in_S2(sequence, S2)

            matches = self.find_matches(candidates1, candidates2)

            if not matches:
                return None  # Ślepy zaułek

            if len(matches) == 1:
                # tylko jedna możliwość – kontynuujemy bez rekursji
                c1, c2 = matches[0]
                sequence += c1[-1]
                usedOligos += 2
                if c1 in S1:
                    S1.remove(c1)
                if c2 in S2:
                    S2.remove(c2)
            else:
                # wiele możliwości – wchodzimy rekurencyjnie
                for c1, c2 in matches:
                    new_seq = sequence + c1[-1]
                    usedOligos += 2
                    new_S1 = S1.copy()
                    new_S2 = S2.copy()
                    if c1 in new_S1:
                        new_S1.remove(c1)
                    if c2 in new_S2:
                        new_S2.remove(c2)

                    res = self._build_with_backtrack(new_seq, new_S1, new_S2, usedOligos, sqpe)
                    if res is None:
                        return "", 0, 0  # lub inne wartości domyślne
                    result, usedOligos, sqpe = res
                    if result:
                        return result, usedOligos, sqpe  # sukces
                return None  # żadna ścieżka nie działała

        sqpe += len(S1)
        sqpe += len(S2)
        return sequence, usedOligos, sqpe  # pełna sekwencja gotowa

    def find_in_S1(self, sequence, S1):
        return [seq for seq in S1 if self.can_overlap(sequence, seq)]

    def find_in_S2(self, sequence, S2):
        return [seq for seq in S2 if self.can_overlap(sequence, seq)]

    def find_matches(self, candidates1, candidates2):
        return [(c1, c2) for c1 in candidates1 for c2 in candidates2 if c1[-1] == c2[-1]]

    def can_overlap(self, seq1, seq2):
        prefix_len = len(seq2) - 1
        end1 = seq1[-prefix_len:]
        start2 = seq2[:prefix_len]
        for c1, c2 in zip(end1, start2):
            if c2 != 'X' and c1 != c2:
                return False
        return True