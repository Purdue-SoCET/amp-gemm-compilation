import numpy as np

N = 128
np.random.seed(42)  # for reproducibility
A = np.random.rand(N, N).astype(np.float16)
B = np.random.rand(N, N).astype(np.float16)

def array_to_c_macro(name, arr):
    lines = [f"#define {name} {{"]
    for row in arr:
        line = ", ".join(f"{x:.4f}f" for x in row)
        lines.append("    {" + line + "},")
    lines.append("}")
    return "".join(lines)

with open("matrix_init.h", "w") as f:
    f.write(array_to_c_macro("A_INIT", A) + "\n\n")
    f.write(array_to_c_macro("B_INIT", B) + "\n")