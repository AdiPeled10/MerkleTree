# Adi Peled, 318814308, Itamar Fisch, 312502602
import math
import base64
from hashlib import sha256

merkle_tree = None
sparse_merkle_tree = None


def print_error(msg):
    # TODO before submit make sure to replace the code with "print('')"
    # This function will help us make all the prints disappear before submit
    print(msg)


# This function is wrong! Listen to your recording with the improvements
def calculate_max_needed_values_for_sparse_tree():
    num_hashes_in_tree_level = [0] * 257
    nodes_in_level = 2 ** 256
    num_possible_values_in_level = 2
    for i in range(-1, -len(num_hashes_in_tree_level) - 1, -1):
        if num_possible_values_in_level < nodes_in_level:
            num_hashes_in_tree_level[i] = num_possible_values_in_level
            num_possible_values_in_level *= num_possible_values_in_level
        else:
            num_hashes_in_tree_level[i] = nodes_in_level
        nodes_in_level >>= 1
    return num_hashes_in_tree_level


