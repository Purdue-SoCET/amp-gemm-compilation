from collections import defaultdict
import math
import pandas as pd

# This file allocates the regs as needed for 1 outer loop iteration
# Also -- this uses 48 matrix registers not -- 64. 
# Matrix Register 0 is treated as a 0 register -- needed for correctness.

# Configuration for 1 outer tile = 16x16 matrix block using 4x4 tiling

INNER_TILES = 4  # Number of inner tiles per outer tile
TILE_SIZE = 4    # Size of each tile
NUM_MREGS = 64   # Total matrix registers
K_OUTER = 4      # Number of tiles along K dimension

# Matrix register setup
mreg_pool = [f"{i}" for i in range(NUM_MREGS)]
mreg_allocated = [False] * NUM_MREGS
mreg_allocated[0] = True  # Reserve m0 as MZERO
reg_assignment = {}
reg_reverse = {}
output_defines = ["#define MZERO 0", "#define SCALAR_REG 10"]
output_macros = []

def allocate_mreg(tile_name):
    if tile_name in reg_assignment:
        return reg_assignment[tile_name]
    for i in range(1, NUM_MREGS):
        if not mreg_allocated[i]:
            mreg_allocated[i] = True
            reg_assignment[tile_name] = i
            reg_reverse[i] = tile_name
            return i
    raise RuntimeError(f"Out of matrix registers while assigning {tile_name}")

# i_outer, j_outer fixed to 0 for this tile
i_outer, j_outer = 0, 0
C_tiles = [[f"C_{i_outer}_{j_outer}_{ii}_{jj}" for jj in range(INNER_TILES)] for ii in range(INNER_TILES)]

# Assign matrix registers for C tiles
for ii in range(INNER_TILES):
    for jj in range(INNER_TILES):
        c_tile = C_tiles[ii][jj]
        mreg_id = allocate_mreg(c_tile)
        output_defines.append(f"#define {c_tile} {mreg_id}")
        output_defines.append(f"#define {c_tile}_ACC {mreg_id}")
        output_defines.append(f"#define base_{c_tile} base_C[{ii}][{jj}]")
        output_defines.append(f"#define offset_{c_tile} 0")
# Main GEMM loop
for k_outer in range(K_OUTER):
    loaded_this_iter = set()

    for ii in range(INNER_TILES):
        a_tile = f"A_{i_outer}_{k_outer}_{ii}"
        if a_tile not in reg_assignment:
            mreg_id = allocate_mreg(a_tile)
            output_defines.append(f"#define {a_tile} {mreg_id}")
        output_defines.append(f"#define base_{a_tile} base_A[{ii}][{k_outer}]")
        output_defines.append(f"#define offset_{a_tile} 0")

        if a_tile not in loaded_this_iter:
            output_macros.append(f"LD_M_IMM({a_tile}, base_{a_tile}, SCALAR_REG, offset_{a_tile});")
            loaded_this_iter.add(a_tile)

        for jj in range(INNER_TILES):
            b_tile = f"B_{k_outer}_{j_outer}_{jj}"
            if b_tile not in reg_assignment:
                mreg_id = allocate_mreg(b_tile)
                output_defines.append(f"#define {b_tile} {mreg_id}")
            output_defines.append(f"#define base_{b_tile} base_B[{k_outer}][{jj}]")
            output_defines.append(f"#define offset_{b_tile} 0")

            if b_tile not in loaded_this_iter:
                output_macros.append(f"LD_M_IMM({b_tile}, base_{b_tile}, SCALAR_REG, offset_{b_tile});")
                loaded_this_iter.add(b_tile)

            c_tile = C_tiles[ii][jj]
            acc_tile = "MZERO" if k_outer == 0 else f"{c_tile}_ACC"

            if k_outer == 0:
                output_macros.append(f"LD_M_IMM({c_tile}, base_{c_tile}, SCALAR_REG, offset_{c_tile});")
            output_macros.append(f"GEMM({c_tile}, {a_tile}, {b_tile}, {acc_tile});")

            # only bother writing the things back for the very last tile. 
            if k_outer == K_OUTER - 1:
                output_macros.append(f"ST_M_IMM({c_tile}, base_{c_tile}, SCALAR_REG, offset_{c_tile});")

# Final ST_M pass
# for ii in range(INNER_TILES):
#     for jj in range(INNER_TILES):
#         c_tile = C_tiles[ii][jj]
#         output_macros.append(f"ST_M({c_tile}, base_{c_tile}, offset_{c_tile});")

header_output = "\n".join(sorted(set(output_defines)))
body_output = "\n".join(output_macros)

with open("matrix_alloc.h", "w") as f:
    f.write(header_output)

with open("matrix_body.inc", "w") as f:
    f.write(body_output)

print("Files written: matrix_alloc.h and matrix_body.inc")