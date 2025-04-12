// ===================================================================================
// the below encodes give you the exact binary representation of the string that 
// you want. NEED TO DEBUG THESE AND MAKE SURE THAT IT MATCHES WHATEVER ITS SUPPOSED TO BE.
#define ENCODE_LD_M(mreg, rs1, imm) \
  (((mreg & 0x3F) << 26) | ((rs1 & 0x1F) << 21) | ((imm & 0x3FF) << 11) | 0x087)

#define ENCODE_ST_M(mreg, rs1, imm) \
  (((mreg & 0x3F) << 26) | ((rs1 & 0x1F) << 21) | ((imm & 0x3FF) << 11) | 0x0A7)

#define ENCODE_GEMM(md, ma, mb, mc) \
  (((md & 0x3F) << 26) | ((ma & 0x3F) << 20) | ((mb & 0x3F) << 14) | ((mc & 0x3F) << 8) | 0x77)

// ===================================================================================
// the macros below are set up to ensure that the scalar register is correctly 
// used in the local scope. This means that a store to the stack and load back
// from the stack are guaranteed to happen correctly. 
#define LD_M_IMM(mreg, val, scalar_regnum, imm)                     \
  do {                                                              \
    register uintptr_t __addr __asm__("a0") =        \
        (uintptr_t)(val);                                           \
    asm volatile(".word %0\n"                                       \
                 :                                                  \
                 : "i"(ENCODE_LD_M(mreg, scalar_regnum, imm)),     \
                   "r"(__addr)                                      \
                 : "memory");                                       \
  } while (0)
  

// if you use anyhting other than a0, make sure that you
// modify the register a0 - to correspond. 
#define ST_M_IMM(mreg, val, scalar_regnum, imm)                        \
  do {                                                                 \
    register uintptr_t __addr __asm__("a0") =           \
        (uintptr_t)(val);                                              \
    asm volatile(".word %0\n"                                          \
                 :                                                     \
                 : "i"(ENCODE_ST_M(mreg, scalar_regnum, imm)),        \
                   "r"(__addr)                                         \
                 : "memory");                                          \
  } while (0)

// ===================================================================================
// no scalar register assign for this -- else this will be really hard to work with.
#define GEMM(md, ma, mb, mc) \
  asm volatile(".word %0" :: "i"(ENCODE_GEMM(md, ma, mb, mc)) : "memory")

// ===================================================================================


