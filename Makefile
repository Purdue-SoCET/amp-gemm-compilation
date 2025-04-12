DUMP_DIR = ./dumps/
SRC_DIR = ./src/
INCLUDE_DIR = ./inc/

SOURCE_FILES = \
	$(INCLUDE_DIR)amp_def.h \
	$(INCLUDE_DIR)matrix_alloc.h \
	$(INCLUDE_DIR)matrix_init.h \

help:
	@echo "Available make targets:"
	@echo "Note: replace all % with file name. Ex: for main.c run make main_all"
	@echo "  %_all         - compile files, disassemble, and dump bin&hex file"
	@echo "  %_compile     - compile the elf file from the program"
	@echo "  %_dump        - disassemble the program"
	@echo "  %_bin         - convert ELF to raw binary"
	@echo "  %_hex         - convert ELF to hex file"
	@echo "  init          - setup src, inc, and dumps directory"

%_all: compile disassemble bin hex

%_compile: | init
	riscv64-unknown-elf-gcc \
  	-march=rv32i -mabi=ilp32 \
	-Wl,-EL -Wl,-m,elf32lriscv \
	-nostartfiles -nostdlib \
	-O2 \
	-I $(INCLUDE_DIR) \
	-o "$(DUMP_DIR)$*.elf" $(SRC_DIR)$*.c $(SOURCE_FILES)

%_dump:
	riscv64-unknown-elf-objdump -D $(DUMP_DIR)$*.elf > $(DUMP_DIR)$*_dump.txt

%_bin:
	riscv64-unknown-elf-objcopy -O binary $(DUMP_DIR)$*.elf $(DUMP_DIR)$*.bin

%_hex:
	riscv64-unknown-elf-objcopy -O ihex $(DUMP_DIR)$*.elf $(DUMP_DIR)$*.hex

init:
	@mkdir -p $(DUMP_DIR) $(SRC_DIR) $(INCLUDE_DIR)
