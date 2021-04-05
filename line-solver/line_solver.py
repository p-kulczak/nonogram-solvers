import sys
import time
from itertools import permutations
import os
# import psutil

board = []
checks = 0


# reads nonograms data from input file
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


# prints board in a readable form
def print_board():
    for x in range(len(board[0])):
        print("---", end="", file=output_file)
    print(file=output_file)
    for i in range(len(board)):
        for j in range(len(board[0])):
            print(board[i][j], end="  ", file=output_file)
        print(file=output_file)
    for x in range(len(board[0])):
        print("---", end="", file=output_file)
    print(file=output_file)


# counts cells with black color
def count_black_cells():
    black = 0
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 2:
                black += 1
    return black


# # reads rrs after allocating all rows and columns' permutations
# def memory_usage():
#     process_id = os.getpid()
#     ps = psutil.Process(process_id)
#     memory_use = ps.memory_info()
#     return memory_use.rss


# check of the final board if it meets the original rules
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


# all possible combinations of given row or col
def all_permutations(board_length, row):
    numb_of_blocks = len(row)
    partitions_elems_size = numb_of_blocks + 1
    first_elem = True
    blocks_size = 0
    for x in range(len(row)):
        if not first_elem:
            blocks_size += 1
        blocks_size += row[x]
    partitions_elems = board_length - blocks_size - numb_of_blocks + 1

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
        for n in range(numb_of_blocks):
            for cell in range(perm[n]):
                poss_row.append(1)
            if not first_block:
                poss_row.append(1)
            first_block = False
            for cell in range(row[n]):
                poss_row.append(2)
        for cell in range(perm[len(perm) - 1]):
            poss_row.append(1)
        possible_rows.append(poss_row)

    return possible_rows


def create_permutations_list():
    row_permutations = []
    for row in rows:
        row_permutations.append(all_permutations(len(board[0]), row))
    col_permutations = []
    for col in cols:
        col_permutations.append(all_permutations(len(board), col))
    return row_permutations, col_permutations


def count_permutations(row_perms, col_perms):
    row_number = 0
    for row in row_perms:
        row_number += len(row)
    col_number = 0
    for col in col_perms:
        col_number += len(col)
    return row_number, col_number


def delete_wrong_row_options(r, row_perms):
    for opt in range(len(row_perms[r])):
        for cell in range(len(row_perms[r][opt])):
            if board[r][cell] != 0 and row_perms[r][opt][cell] != board[r][cell]:
                row_perms[r][opt] = False
                break
    row_perms[r][:] = (value for value in row_perms[r] if value != False)
    return row_perms


def delete_wrong_col_options(c, col_perms):
    for opt in range(len(col_perms[c])):
        for cell in range(len(col_perms[c][opt])):
            if not board[cell][c] == 0:
                if not col_perms[c][opt][cell] == board[cell][c]:
                    col_perms[c][opt] = [3]
                    break
    col_perms[c][:] = (value for value in col_perms[c] if value != [3])
    return col_perms


def check_row(r, row_perms):
    exemplary_row = row_perms[r][0][:]
    for option in row_perms[r]:
        for cell in range(len(option)):
            if not exemplary_row[cell] == 0:
                if not option[cell] == exemplary_row[cell]:
                    exemplary_row[cell] = 0
    new_cells = []
    for cell in range(len(exemplary_row)):
        if exemplary_row[cell] != 0 and board[r][cell] == 0:
            board[r][cell] = exemplary_row[cell]
            new_cells.append(cell)
    return new_cells


def check_col(c, col_perms):
    exemplary_col = col_perms[c][0][:]
    for option in col_perms[c]:
        for cell in range(len(option)):
            if not exemplary_col[cell] == 0:
                if not option[cell] == exemplary_col[cell]:
                    exemplary_col[cell] = 0
    new_cells = []
    for cell in range(len(exemplary_col)):
        if exemplary_col[cell] != 0 and board[cell][c] == 0:
            board[cell][c] = exemplary_col[cell]
            new_cells.append(cell)
    return new_cells


def solve(row_perms, col_perms):
    global checks
    checks = 0
    queue = []
    for i in range(len(board)):
        queue.append(["r", i])
    for i in range(len(board[0])):
        queue.append(["c", i])
    last_check = "r"
    while len(queue) > 0:
        line = queue.pop(0)
        if line[0] == "r":
            if last_check == "c":
                checks += 1
            last_check = "r"
            row_perms = delete_wrong_row_options(line[1], row_perms)
            new_cells = check_row(line[1], row_perms)
            for cell in new_cells:
                if ["w", cell] not in queue:
                    queue.append(["c", cell])
        elif line[0] == "c":
            if last_check == "r":
                checks += 1
            last_check = "c"
            col_perms = delete_wrong_col_options(line[1], col_perms)
            new_cells = check_col(line[1], col_perms)
            for cell in new_cells:
                if ["r", cell] not in queue:
                    queue.append(["r", cell])


if __name__ == '__main__':
    board, rows, cols = import_board()

    output_path = sys.argv[1]
    output_path = output_path.strip('./boards/')
    output_path = "./results/out_" + output_path
    with open(output_path, 'a+') as output_file:
        print("Rozpoczęto działanie programu", file=output_file)
    output_file.close()

    start_time = time.time()
    row_permutations, col_permutations = create_permutations_list()

    with open(output_path, 'a+') as output_file:
        print("Permutacje wszystkich wierszy i kolumn zostały stworzone:", file=output_file)
        print(count_permutations(row_permutations, col_permutations), file=output_file)
    output_file.close()

    solve(row_permutations, col_permutations)
    end_time = time.time() - start_time
    print(checks)

    with open(output_path, 'a+') as output_file:
        print("Koncowe ilosci permutacji:", file=output_file)
        print(count_permutations(row_permutations, col_permutations), file=output_file)
        print("Czas rozwiazywania: %s s" % end_time, file=output_file)
        print_board()
        print(file=output_file)
    output_file.close()
    print()
