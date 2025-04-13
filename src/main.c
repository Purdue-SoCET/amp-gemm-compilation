#include <stdint.h>
#include "matrix_alloc.h"  // defines A_*, B_*, C_* tile register mappings
#include "amp_def.h"       // LD_M_IMM, ST_M_IMM, GEMM, etc.

#include "matrix_init.h"  // defines A_INIT, B_INIT

#define N 128
#define TILE_SIZE 4
#define INNER_TILES (N / TILE_SIZE)   // = 32
#define OUTER_TILE_SIZE 16
#define OUTER_TILES (N / OUTER_TILE_SIZE) // = 8


uint16_t A[N][N] = A_INIT;
uint16_t B[N][N] = B_INIT;
uint16_t C[N][N] = {0};

void run_matmul() {
    for (int i_outer = 0; i_outer < OUTER_TILES; ++i_outer) {
        for (int j_outer = 0; j_outer < OUTER_TILES; ++j_outer) {

            // base addresses for the current outer tile
            uintptr_t base_A[4][4];  // [ii][k_outer]
            uintptr_t base_B[4][4];  // [k_outer][jj]
            uintptr_t base_C[4][4];

            for (int ii = 0; ii < 4; ++ii) {
                for (int k = 0; k < 4; ++k) {
                    base_A[ii][k] = (uintptr_t)&A[i_outer * OUTER_TILE_SIZE + ii * TILE_SIZE]
                                                [k * TILE_SIZE + 0 + 0 /* K_offset */];
                }
            }
            for (int k = 0; k < 4; ++k) {
                for (int jj = 0; jj < 4; ++jj) {
                    base_B[k][jj] = (uintptr_t)&B[k * TILE_SIZE + 0 + 0]
                                                [j_outer * OUTER_TILE_SIZE + jj * TILE_SIZE];
                }
            }

            for (int ii = 0; ii < 4; ++ii) {
                for (int jj = 0; jj < 4; ++jj) {
                    base_C[ii][jj] = (uintptr_t)&C[i_outer * OUTER_TILE_SIZE + ii * TILE_SIZE][j_outer * OUTER_TILE_SIZE + jj * TILE_SIZE];
                }
            }

            // Run the matrix_body code with tile-local bases
            // This just expands one outer tile's GEMMs
            #include "matrix_body.inc"
        }
    }
}

int main() {

    run_matmul();
    HALT();
    return 0;
}
