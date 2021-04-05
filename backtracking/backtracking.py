import sys
import time
from itertools import permutations

board = []
depth = 0


def import_board():
    input_path = sys.argv[1]
    input_file = open(input_path, "r+")
    split_list = input_file.read().split('\n')
    # reading data
    dimensions = []
    rows_array = []
    cols_array = []
    for number in split_list.pop(0).split():
        if len(number) > 0:
            dimensions.append(int(number))
    x = 0
    while x < dimensions[1]:
        rows_array.append((split_list.pop(0)))
        x = x+1
    rows_array = [list(map(int, row.split(" "))) for row in rows_array]
    x = 0
    while x < dimensions[0]:
        cols_array.append((split_list.pop(0)))
        x = x + 1
    cols_array = [list(map(int, col.split(" "))) for col in cols_array]
    input_file.close()
    # creating board
    grid = [[0 for x in range(dimensions[0])] for y in range(dimensions[1])]
    return grid, rows_array, cols_array


def print_board():
    for x in range(len(board[0])):
        print("---", end="")
    print()
    for i in range(len(board)):
        for j in range(len(board[0])):
            print(board[i][j], end="  ")
        print()
    for x in range(len(board[0])):
        print("---", end="")
    print()


# counts cells with black color
def count_black_cells():
    black = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 2:
                black += 1
    return black


# validates finished boards
def final_validation(rows, cols):
    original_cols = []
    single_col = []
    for x in range(len(board[0])):
        prev_white = True
        for i in range(len(board)):
            if board[i][x] == 1:
                prev_white = True
            elif board[i][x] == 2:
                if prev_white:
                    single_col.append(1)
                else:
                    single_col[len(single_col)-1] += 1
                prev_white = False
        original_cols.append(single_col.copy())
        single_col.clear()
    if cols != original_cols:
        return False

    original_rows = []
    single_row = []
    for x in range(len(board)):
        prev_white = True
        for i in range(len(board[0])):
            if board[x][i] == 1:
                prev_white = True
            elif board[x][i] == 2:
                if prev_white:
                    single_row.append(1)
                else:
                    single_row[len(single_row)-1] += 1
                prev_white = False
        original_rows.append(single_row.copy())
        single_row.clear()
    return False if rows != original_rows else True


# find first row with an empty cell otherwise returns board height
def find_empty():
    for i in range(len(board)):
        if board[i][0] == 0:
            return i
    return len(board)


# n is the integer to partition, k is the length of partitions, l is the min partition element size
def partition(n, k, l=1):
    if k < 1:
        raise StopIteration
    if k == 1:
        if n >= l:
            yield (n,)
        return
    for i in range(l, n + 1):
        for result in partition(n - i, k - 1, i):
            yield (i,) + result


# all possible combinations of row with index idx
def row_permutations(board_length, rows, idx):
    row_elems = len(rows[idx])
    partitions_elems_size = row_elems + 1
    first_elem = True
    row_elems_size = 0
    for x in range(len(rows[idx])):
        if not first_elem:
            row_elems_size += 1
        row_elems_size += rows[idx][x]
    partitions_elems = board_length - row_elems_size - row_elems + 1

    partitions = []
    for i in partition(partitions_elems, partitions_elems_size, 0):
        partitions.append(i)

    partition_permutations_set = set()
    for i in partitions:
        partition_permutations_set.update(permutations(i))

    partition_permutations_list = [list(ele) for ele in partition_permutations_set]
    partition_permutations_list.sort()

    possible_rows = []
    for perm in partition_permutations_list:
        poss_row = []
        first_block = True
        for n in range(row_elems):
            for cell in range(perm[n]):
                poss_row.append(1)
            if not first_block:
                poss_row.append(1)
            first_block = False
            for cell in range(rows[idx][n]):
                poss_row.append(2)
        for cell in range(perm[len(perm) - 1]):
            poss_row.append(1)
        possible_rows.append(poss_row)

    return possible_rows


# validates all colored cells in the columns, curr_board_height counts from 0
def validate_vertically(cols, curr_board_height):
    block_height = 0
    block = 0
    row = 0
    for col in range(len(board[0])):
        while row <= curr_board_height:
            if block == len(cols[col]) and board[row][col] == 2:
                return False
            if board[row][col] == 2:
                block_height += 1
                if block_height > cols[col][block]:
                    return False
                row += 1
            elif board[row][col] == 1:
                if block_height == 0:
                    row += 1
                elif block_height == cols[col][block]:
                    block_height = 0
                    block += 1
                    row += 1
                else:
                    return False
            elif board[row][col] == 0:
                row += 1
        block_height = 0
        block = 0
        row = 0
    return True


# recursive function that finds nonogram's solution
def solve(rows, cols):
    global depth
    depth += 1
    if find_empty() == len(board):
        return True
    for idx in range(find_empty(), len(board)):
        for row in row_permutations(len(board[0]), rows, idx):
            board[idx] = row
            if validate_vertically(cols, idx):
                if solve(rows, cols):
                    return True
                for y in range(len(board[idx])):
                    board[idx][y] = 0
            else:
                for y in range(len(board[idx])):
                    board[idx][y] = 0
        return False


# main function
if __name__ == '__main__':
    board, rows, cols = import_board()
    start_time = time.time()
    solve(rows, cols)
    end_time = time.time() - start_time
    print("Działanie funkcji rozwiązującej zakończyło się.")
    output_path = sys.argv[1]
    output_path = output_path.strip('./boards/')
    output_path = "./results/out_" + output_path
    if final_validation(rows, cols):
        with open(output_path, 'a+') as output_file:
            print("Program execution time: %s s" % end_time, file=output_file)
            print("Recursion calls: %d" % depth, file=output_file)
            print(file=output_file)
        output_file.close()
        print("Dodano dane do pliku", output_path)
    else:
        print("Nonogram", sys.argv[1].strip('./boards/'), " nie został poprawnie rozwiązany.")
    print()
