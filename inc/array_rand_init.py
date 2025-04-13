import numpy as np
import struct

N = 128
np.random.seed(42)  # for reproducibility
A = np.random.rand(N, N).astype(np.float16)
B = np.random.rand(N, N).astype(np.float16)

def fp16_to_bits(fp16):
    packed = struct.pack('>e', fp16)        # '>e' = big-endian half-float (16-bit)
    [bits] = struct.unpack('>H', packed)   # unpack as 16-bit unsigned int
    return bits


def array_to_c_macro(name, arr):
    lines = [f"#define {name} {{"]
    for row in arr:
        line = ", ".join(f"{hex(fp16_to_bits(x))}" for x in row)
        lines.append("    {" + line + "},")
    lines.append("}")
    return "".join(lines)

with open("matrix_init.h", "w") as f:
    f.write(array_to_c_macro("A_INIT", A) + "\n\n")
    f.write(array_to_c_macro("B_INIT", B) + "\n")