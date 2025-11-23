from collections import Counter
from typing import List, Dict, Any

import csv
import json
import os


class ProbabilityCalculator:
    @staticmethod
    def calculate_transition_matrix(sequences: List[List[str]], state_idx: Dict[str, int]) -> List[List[float]]:
        n = len(state_idx)
        counts = [[0] * n for _ in range(n)]

        for seq in sequences:
            for cur, nxt in zip(seq, seq[1:]):
                counts[state_idx[cur]][state_idx[nxt]] += 1

        matrix = [[0.0] * n for _ in range(n)]
        for i in range(n):
            row_tot = sum(counts[i])
            inv = 1.0 / (row_tot or 1)
            matrix[i] = [c * inv for c in counts[i]]
        return matrix

    @staticmethod
    def calculate_initial_states(sequences: List[List[str]]) -> Dict[str, float]:
        initial_counter = Counter(seq[0] for seq in sequences)
        total = len(sequences)
        return {state: count / total for state, count in initial_counter.items()}
    
    @staticmethod
    def calculate_final_states(sequences: List[List[str]]) -> Dict[str, float]:
        final_counter = Counter(seq[-1] for seq in sequences)
        total_sequences = len(sequences)        
        final_states = {}
        for state, count in final_counter.items():
            final_states[state] = count / total_sequences
        return final_states

    @staticmethod
    def analyze_sequences(sequences: List[List[str]]) -> Dict[str, Any]:
        all_states = sorted({st for seq in sequences for st in seq})
        state_idx = {s: i for i, s in enumerate(all_states)}        

        transition_matrix = ProbabilityCalculator.calculate_transition_matrix(sequences, state_idx)
        initial_states = ProbabilityCalculator.calculate_initial_states(sequences)
        final_states = ProbabilityCalculator.calculate_final_states(sequences)
        all_states = sorted({state for seq in sequences for state in seq})
        return {
            'transition_matrix': transition_matrix,
            'initial_states': initial_states,
            'final_states': final_states,
            'all_states': all_states,
            'state_idx': state_idx
        }

def integration(csv_file_path: str = 'sequences.csv', json_file_path: str = 'config.json'):
    if not os.path.exists(csv_file_path) or not os.path.exists(json_file_path):
        open(csv_file_path, 'w', encoding='utf-8').close()
        open(json_file_path, 'w', encoding='utf-8').close()
        print('Файлы sequences.csv и config.json созданы. Заполните sequences.csv и перезапустите код.')
        exmp='''
                A, B, C, E, D
                A, B, C, E, H
                A, C, B, E, D
            '''
        print(f'Пример sequences.csv:{exmp}')
        return
    
    with open(csv_file_path, newline='', encoding='utf-8') as f:
        sequences = [[cell.strip() for cell in row]
                     for row in csv.reader(f)]

    result = ProbabilityCalculator.analyze_sequences(sequences)

    initial = max(result['initial_states'], key=result['initial_states'].get)    
    final = list(result['final_states'].keys())

    with open(json_file_path, 'w', encoding='utf-8') as f:
        json.dump(
            {
            "states": result['all_states'],
            "initial": initial,
            "transition_matrix": result['transition_matrix'],
            "terminal_states": final}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    integration()