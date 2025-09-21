import threading
import random
import queue
import sys
import os

def check_valid(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def solve(board):
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                for num in range(1, 10):
                    if check_valid(board, row, col, num):
                        board[row][col] = num
                        if solve(board):
                            return True
                        board[row][col] = 0
                return False
    return True

def fill_board(board):
    for _ in range(20): #кол-во итераций - усложнение
        row, col = random.randint(0, 8), random.randint(0, 8)
        num = random.randint(1, 9)
        while not check_valid(board, row, col, num):
            row, col = random.randint(0, 8), random.randint(0, 8)
            num = random.randint(1, 9)
        board[row][col] = num

def remove_numbers(board, attempts=5):
    while attempts > 0:
        row, col = random.randint(0, 8), random.randint(0, 8)
        while board[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        backup = board[row][col]
        board[row][col] = 0
        # проверка на уникальность решения
        board_copy = [r[:] for r in board]
        if not solve(board_copy):
            board[row][col] = backup
        else:
            attempts -= 1

def generate_sudoku(hide):
    board = [[0] * 9 for _ in range(9)]
    fill_board(board)
    solve(board)
    remove_numbers(board, hide)
    return board
    
def generate_sudoku_with_timeout(hide, timeout=2):
    q = queue.Queue()

    def target():
        board = generate_sudoku(hide)
        q.put(board)

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return None
    else:
        return q.get()

def check_solution(board):
    result = True
    
    wrong_rows = [] 
    for y, row in enumerate(board):
        if not len(row) == len(set(row)):
            wrong_rows.append(y)
            result = False
    
    wrong_cols = []
    for col in range(9):
        unit = [board[row][col] for row in range(9)]
        if not len(unit) == len(set(unit)):
            wrong_cols.append(col)
            result = False
    
    wrong_units = []
    for row in range(0, 9, 3):
        for col in range(0, 9, 3):
            unit = [board[r][c] for r in range(row, row + 3) for c in range(col, col + 3)]
            if not len(unit) == len(set(unit)):
                wrong_units.append((row, col))
                result = False
     
    wrong_coordinates = []
    for row in wrong_rows:
        for col in wrong_cols:
            wrong_coordinates.append((row, col))
     
    wrong_coordinates = list(set(wrong_coordinates))

    return result, wrong_coordinates

def print_board(board, hints):
    clear_screen()
    print('\t  | ' + ' '.join(map(str, [i % 10 for i in range(1, 10)])))
    print('\t— — ' + ' '.join(['—' for i in range(10)]))
    for i, row in enumerate(board):
        print(f'\t{(i+1) % 10} |' + ('_'  if (i+1)%3 == 0 and i!=8 else ' '), end='') 
        
        line = ''
        for x, cell in enumerate(row):
            if cell == 0:
                line += '\033[30;1m×\033[0m'
            elif (i, x) in hints:
                line += str(cell)
            else:
                line += f'\033[33;1m{cell}\033[0m'
            if (x+1)%3 == 0 and x != 8:
                line += '|'
            else:
                line += ' '
                
            line = line[:-1] + '_'  if (i+1)%3 == 0 and x == 8 and i!=8 else line
        print(line)
    
    print('\t[x y n]-ход; [11]-проверка; [99]-выход')

def display_wrong_solution(board, hints, wrong_coords):
    clear_screen()
    print('\t  | ' + ' '.join(map(str, [i % 10 for i in range(1, 10)])))
    print('\t— — ' + ' '.join(['—' for i in range(10)]))
    for i, row in enumerate(board):
        print(f'\t{(i+1) % 10} |' + ('_'  if (i+1)%3 == 0 and i!=8 else ' '), end='')
        
        line = ''
        for x, cell in enumerate(row):
            if cell == 0:
                line += '\033[30;1m×\033[0m'
            elif (i, x) in hints:
                line += str(cell)
            else:
                line += ('\033[31;1m' if (i, x) in wrong_coords else '\033[33;1m') + f'{cell}\033[0m'                            
            if (x+1)%3 == 0 and x != 8:
                line += '|'
            else:
                line += ' '
            
            line = line[:-1] + '_'  if (i+1)%3 == 0 and x == 8 and i!=8 else line
        print(line)
    
    print('\t[x y n]-ход; [11]-проверка; [99]-выход')

def start_game(board):
    hints = [(y, x) for y in range(9) for x in range(9) if board[y][x] != 0]
    while True:
        print_board(board, hints)
        query = input('\n\tХод: ').strip().split()
        
        if '99' in query:
            break
            
        if '11' in query:
            if 0 in [cell for row in board for cell in row]:
                continue
                
            is_won, wrong_coords = check_solution(board)
            
            if is_won:
                input('\tYou won! Click Enter to continue...')
                break
            else:
                display_wrong_solution(board, hints, wrong_coords)
                query = input('\n\tХод: ').strip().split()
            
        elif len(query) != 3:
            continue
        try:
            x, y, num = map(int, query[:3])
        except ValueError:
            continue
        y -= 1
        x -= 1
            
        if not (0 <= y < 9 and 0 <= x < 9 and 1 <= num <= 9):
            continue
        
        if num < 1 or num > 9:
            continue
                    
        if (y, x) not in hints:
            board[y][x] = num
        
def display_logo():
    LOGO = r""" ____            _       _
/ ___| _   _  __| | ___ | | ___   _ 
\___ \| | | |/ _` |/ _ \| |/ / | | |
 ___) | |_| | (_| | (_) |   <| |_| |
|____/ \__,_|\__,_|\___/|_|\_\\__,_|
"""
    print(LOGO)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_difficulty_selection(selected_diff, current_hidden_cells):
    difficulties = ['Begginer', 'Intermediate', 'Expert', 'Custom']
    
    def format_option(num, diff):
        var = f'[{num}] {diff}'
        return f'\033[32m{var}\033[0m' if selected_diff == diff else var

    while True:
        clear_screen()
        display_logo()
        choice_text = (
            f"{format_option(1, 'Begginer')} {format_option(2, 'Intermediate')}\n"
            f"{format_option(3, 'Expert')}   "
            f"{format_option(4, 'Custom' + (f'({current_hidden_cells})' if selected_diff == 'Custom' else ''))}\n"
        )
        difficulty = input(choice_text + '>>> ')
        
        if difficulty.isdigit() and 1 <= int(difficulty) <= 4:
            selected_diff = difficulties[int(difficulty) - 1]
            
            return selected_diff

def get_hidden_cells(difficulty):
    difficulties = ['Begginer', 'Intermediate', 'Expert', 'Custom']
    diff_cells = [(30, 40), (40, 50), (50, 60)]
    
    if difficulty != 'Custom':
        return random.randint(*diff_cells[difficulties.index(difficulty)])
    else:
        return int(input('Введите количество спрятанных ячеек:\n>>> '))

def main_menu():
    hidden_cells = random.randint(30,40)
    selected_diff = 'Begginer'
    while True:
        clear_screen()
        display_logo()
        print('[1] Difficulty [99] Exit\n[2] Start')
        query = input('\n>>> ')
        
        if query == '1':
            selected_diff = get_difficulty_selection(selected_diff, hidden_cells)
            hidden_cells = get_hidden_cells(selected_diff)
        elif query == '2':
            print('Генерация карты...')
            board = generate_sudoku_with_timeout(hidden_cells)
            while not board:
                print('Попытка генерации...') 
                board = generate_sudoku_with_timeout(hidden_cells)
            start_game(board)
        elif query == '99':
            sys.exit(0)

if __name__ == '__main__':
    main_menu()