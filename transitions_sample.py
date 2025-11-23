import json
import pickle
from typing import Any
from transitions import Machine
import random

PATH_TO_CONFIG = 'config.json'

class FSM:
    is_terminated = False
    
    def __init__(self,
                 states: list[str],
                 initial: str,
                 transition_matrix: list[list[float]],
                 terminal_states: list[str]):
        self.states = states
        self.state_index = {state: i for i, state in enumerate(self.states)}
        self.transition_matrix = transition_matrix
        self.terminal_states = terminal_states
        
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=initial          
        )
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> 'FSM':
        """Создание из словаря"""
        fsm = cls(states=data['states'],
                  initial=data['initial'],
                  transition_matrix=data['transition_matrix'])
        return fsm
    
    def trigger_transition(self):
        current_idx = self.state_index[self.state]
        
        next_idx = random.choices(
            range(len(self.states)),
            weights=self.transition_matrix[current_idx]
        )[0]
        
        next_state = self.states[next_idx]
        
        if next_state != self.state:
            getattr(self, f'to_{next_state}')()
        
        return next_state
    
    def __getstate__(self) -> dict[str, Any]:
        """Метод для сериализации pickle"""
        state = {
            'states': self.states,
            'state_index': self.state_index,
            'transition_matrix': self.transition_matrix,
            'current_state': self.state,
            'initial': self.initial if hasattr(self, 'initial') else self.states[0],
            'terminal_states': list(self.terminal_states),
            'is_terminated': self.is_terminated
        }
        return state
    
    def __setstate__(self, state: dict[str, Any]):
        """Метод для десериализации pickle"""
        # Восстанавливаем атрибуты
        self.states = state['states']
        self.state_index = state['state_index']
        self.transition_matrix = state['transition_matrix']
        self.terminal_states = set(state.get('terminal_states', []))
        self.is_terminated = state.get('is_terminated', False)
        
        # Воссоздаем автомат transitions
        self.machine = Machine(
            model=self,
            states=self.states,
            initial=state['initial']
        )
        
        # Восстанавливаем текущее состояние
        if state['current_state'] != self.state:
            getattr(self, f'to_{state["current_state"]}')()

class Config:
    
    @staticmethod
    def load_from_json(file_path: str = PATH_TO_CONFIG) -> FSM:
        with open(file_path, 'r') as file:
            config = json.load(file)
            fsm = FSM(
                states=config['states'],
                initial=config['initial'],
                transition_matrix=config['transition_matrix'],
                terminal_states=config.get('terminal_states', []),
            )
        return fsm
    
    @staticmethod
    def save_to_pickle(fsm: FSM, file_path: str):
        with open(file_path, 'wb') as f:
            pickle.dump(fsm, f)
    
    @staticmethod
    def load_from_pickle(file_path: str) -> FSM:
        with open(file_path, 'rb') as f:
            fsm = pickle.load(f)
        return fsm

if __name__ == '__main__':
    print("=== Демонстрация FSM ===")
    
    loader = Config()
    model = loader.load_from_json()
    
    print(f"Начальное состояние: {model.state}")
    print(f"Все состояния: {model.states}")
    print()
    
    print("Выполняем переходы:")
    for step in range(5):
        before = model.state
        next_state = model.trigger_transition()
        print(f"Шаг {step+1}: {before} -> {model.state}")
        if next_state in model.terminal_states:
            model.is_terminated = True
        if model.is_terminated:
            print(f'Достигнуто терминальное состоние: {next_state}')
            break
    else:
    
        print(f"\nТекущее состояние после переходов: {model.state}")
        
        pickle_path = 'fsm_state.pkl'
        loader.save_to_pickle(model, pickle_path)
        print(f"\nАвтомат сохранен в: {pickle_path}")
        
        loaded_model = loader.load_from_pickle(pickle_path)
        print("Автомат загружен из pickle")
        print(f"Состояние после загрузки: {loaded_model.state}")
        
        print("\nПродолжаем переходы с загруженным автоматом:")
        for step in range(3):
            before = loaded_model.state
            next_state = loaded_model.trigger_transition()
            print(f"Шаг {step+6}: {before} -> {loaded_model.state}")
            
            if next_state in model.terminal_states:
                model.is_terminated = True
            if model.is_terminated:
                print(f'достигнуто терминальное состоние: {next_state}')
                break   