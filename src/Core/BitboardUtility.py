import numpy as np

RANKS = np.array(
    [np.uint64(0x00000000000000FF) << np.uint8(8*i) for i in range(8)],
    dtype=np.uint64)
FILES = np.array(
    [np.uint64(0x0101010101010101) << np.uint8(i) for i in range(8)],
    dtype=np.uint64)

def pop_LSB(bb):
    if bb == 0:
        return -1  # No set bits found
    
    position = 0
    # Use bitwise AND to check the rightmost set bit
    position = bb & -bb
    
    # Count trailing zeros (position of the rightmost set bit)
    position = bin(position).count('0') - 1
    
    return position

def set_square(bb, index: int) -> None:
    return bb | np.uint64(1) << np.uint64(index)   

# Sets square based on a list of (rank, file) tuples
def set_square_notation(bb, notation_list: list):
    ranks = 'abcdefgh'
    for rank, file in notation_list:
        bb = set_square(bb, ranks.index(rank) + (file-1)*8)
    return bb

def contains_square(bb, sq: int) -> bool:
    return bb >> np.uint64(sq) & np.uint64(1) != 0

def uint_to_rep(bb: np.uint64):
    # Convert bitboard to binary representation
    bin_rep = np.unpackbits(np.array([bb], dtype=np.uint64).view(np.uint8))
    
    # Reshape to 8 x 8 array
    return bin_rep.reshape(8, 8)

def rep_to_uint(arr: np.array):
    # Flatten the array to a 1D array
    flattened_array = arr.flatten()
    
    # Convert the flattened array to uint64
    bb = np.packbits(flattened_array)
    
    return bb.view(np.uint64)

# Rotates bitboard 90 degrees counter-clockwise
def rotate90cc(bb) -> np.uint64:
    bin_rep = uint_to_rep(bb)

    # Rotate array 90 degrees
    rotated_arr = np.rot90(bin_rep)
    
    return rep_to_uint(rotated_arr)

def rotate_mirrored90c(bb) -> np.uint64:
    bin_rep = uint_to_rep(bb)

    # Rotate array 90 degrees 3 times (essentially rotate clockwise)
    rotated_arr = np.rot90(bin_rep, 3)

    # Flip array upside down
    rotated_arr = np.flipud(rotated_arr)

    return rep_to_uint(rotated_arr)

def rotate45_shift(bb, shift, is_right=True) -> np.uint64:
    bin_rep = uint_to_rep(bb)

    # Map diagonal bits of array to new bitboard
    mapped_array = np.array([], dtype=int)
    
    # Iterate through each diagonal, concatenate to new array
    for offset in range(-7, 8):       
        diag = np.diagonal(np.flipud(bin_rep), offset) if is_right else np.diagonal(bin_rep, offset)
        mapped_array = np.concatenate((mapped_array, diag))
    
    mapped_array = np.roll(mapped_array, -shift)
    
    return rep_to_uint(mapped_array)

def rotate45L_shift(bb) -> np.uint64:
    # Convert bitboard to binary representation
    bin_rep = np.binary_repr(bb, width=64)

    # Reshape to 8 x 8 array
    bb_arr = np.array(list(bin_rep)).astype(int).reshape(8, 8)[::-1]

    # Map diagonal bits of array to new bitboard
    mapped_array = np.array([], dtype=int)
    
    # Iterate through each diagonal, concatenate to new array
    for offset in range(7, -8, -1):
        diag = np.flipud(bb_arr).diagonal(offset=offset)
        mapped_array = np.concatenate((mapped_array, diag))
    
    flattened_array = mapped_array.flatten()
    
    rotated_bb = np.packbits(flattened_array)
    
    return rotated_bb.view(np.uint64)

def undo45(bb):
    # Convert bitboard to binary representation
    bin_rep = np.unpackbits(np.array([bb], dtype=np.uint64).view(np.uint8))
    
    # Initialize the 8x8 matrix with zeros
    matrix = np.zeros((8, 8), dtype=np.uint64)
    
    # Fill the diagonals
    bit_count = 0
    for i in range(8):
        diagonal_data = np.array([int(bit) for bit in bin_rep[bit_count:bit_count + i + 1]])
        print(diagonal_data)
        np.fill_diagonal(np.flipud(matrix[:i+1, :i+1]), diagonal_data)
        bit_count += i + 1
    
    # Fill the diagonals in reverse order
    for i in range(1, 8):
        diagonal_data = np.array([int(bit) for bit in bin_rep[bit_count:bit_count + 8 - i]])
        print(diagonal_data)
        np.fill_diagonal(np.flipud(matrix[i:, i:]), diagonal_data)
        bit_count += 8 - i
    
    return rep_to_uint(matrix)

def printBB(bb):
    board = np.unpackbits(np.array([bb], dtype=np.uint64).view(np.uint8))
    board = board.reshape(8, 8)[::-1]
    board = np.flip(board, axis=1)
    
    for row in board:
        print(' '.join(map(str, row)))