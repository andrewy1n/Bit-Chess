import numpy as np

RANKS = np.array(
    [np.uint64(0x00000000000000FF) << np.uint8(8*i) for i in range(8)],
    dtype=np.uint64)
FILES = np.array(
    [np.uint64(0x0101010101010101) << np.uint8(i) for i in range(8)],
    dtype=np.uint64)

def set_square(bb, index: int) -> None:
    return bb | np.uint64(1) << np.uint64(index)   

# Sets square based on a list of (rank, file) tuples
def set_square_notation(bb, notation_list: list):
    ranks = 'abcdefgh'
    for rank, file in notation_list:
        bb = set_square(bb, ranks.index(rank) + (file-1)*8)
    return bb

WHITE_KINGSIDE_MASK = set_square_notation(np.uint64(0), [('f', 1), ('g', 1)])
BLACK_KINGSIDE_MASK = set_square_notation(np.uint64(0), [('f', 8), ('g', 8)])

WHITE_QUEENSIDE_MASK_2 = set_square_notation(np.uint64(0), [('d', 1), ('c', 1)])
BLACK_QUEENSIDE_MASK_2 = set_square_notation(np.uint64(0), [('d', 8), ('c', 8)])

WHITE_QUEENSIDE_MASK = set_square_notation(WHITE_QUEENSIDE_MASK_2, [('b', 1)])
BLACK_QUEENSIDE_MASK = set_square_notation(BLACK_QUEENSIDE_MASK_2, [('b', 8)])

INDEX64 = [
    0,  1, 48,  2, 57, 49, 28,  3,
   61, 58, 50, 42, 38, 29, 17,  4,
   62, 55, 59, 36, 53, 51, 43, 22,
   45, 39, 33, 30, 24, 18, 12,  5,
   63, 47, 56, 27, 60, 41, 37, 16,
   54, 35, 52, 21, 44, 32, 23, 11,
   46, 26, 40, 15, 34, 20, 31, 10,
   25, 14, 19,  9, 13,  8,  7,  6
]
    
DEBRUIJN64 = np.uint64(0x03f79d71b4cb0a89)

# Uses De Bruijn bitscan
def popLSB(bb: np.uint64):
    if bb == 0:
        return -1 # No bits found
    
    i = int((bb & -bb) * DEBRUIJN64 >> np.uint64(58))

    bb &= (bb - np.uint64(1))

    return bb, INDEX64[i]

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

    # Rotate array 90 degrees -1 times (essentially rotate clockwise)
    rotated_arr = np.rot90(bin_rep, -1)

    # Flip array upside down
    rotated_arr = np.flipud(rotated_arr)

    return rep_to_uint(rotated_arr)

def rotate45(bb, is_right=True) -> np.uint64:
    bin_rep = uint_to_rep(bb)

    # Map diagonal bits of array to new bitboard
    mapped_array = np.array([], dtype=int)
    
    # Iterate through each diagonal, concatenate to new array
    for offset in range(-7, 8):       
        diag = np.diagonal(np.flipud(bin_rep), offset)[::-1] if is_right else np.diagonal(bin_rep, offset)[::-1]
        mapped_array = np.concatenate((mapped_array, diag))
    
    # Convert the flattened array to uint64
    bb = np.packbits(mapped_array, axis=None, bitorder='little')

    return bb.view(np.uint64)

def printBB(bb):
    board = np.unpackbits(np.array([bb], dtype=np.uint64).view(np.uint8))
    board = board.reshape(8, 8)[::-1]
    board = np.flip(board, axis=1)
    
    for row in board:
        print(' '.join(map(str, row)))