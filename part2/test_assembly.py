import shutil
import subprocess
import sys
from pathlib import Path

PART2_DIR = Path(__file__).resolve().parent
ROOT_DIR = PART2_DIR.parent
RARS_PATH = ROOT_DIR / "tools" / "rars.jar"
TEMPLATE_PATH = PART2_DIR / "next_token_predictor.s"
TEMP_TEST_PATH = PART2_DIR / "temp_test.s"
TEMP_P2_PATH = PART2_DIR / "temp_p2.s"

EQU_HEADER = """###########################################################################
# Hoisted Constants for RARS Compilation (.eqv for macro expansion)
###########################################################################
.eqv CONST_DIMENSION 4
.eqv CONST_BUFFER_SIZE 1024
.eqv CONST_MAX_VOCAB_TOKENS 100
.eqv CONST_MAX_INPUT_TOKENS 10

.eqv CONST_SYSCALL_PRINT_INT 1
.eqv CONST_SYSCALL_PRINT_STRING 4
.eqv CONST_SYSCALL_PRINT_CHAR 11
.eqv CONST_SYSCALL_EXIT 10
.eqv CONST_SYSCALL_EXIT2 93
.eqv CONST_SYSCALL_OPEN 1024
.eqv CONST_SYSCALL_CLOSE 57
.eqv CONST_SYSCALL_READ 63
.eqv CONST_SYSCALL_WRITE 64 

.eqv CONST_CHAR_EOF 0
.eqv CONST_CHAR_SPACE 32
.eqv CONST_CHAR_NEWLINE 10
.eqv CONST_CHAR_HYPHEN 45
.eqv CONST_CHAR_ZERO 48
"""

def preprocess_assembly_content(content):
    # First replace .zero with aligned .space
    content = content.replace(".zero", ".align 2\n.space")
    
    # Resolve the .zero arithmetic expressions so RARS can compile them
    replacements = {
        "(CONST_MAX_INPUT_TOKENS * 4)": "40",
        "(CONST_MAX_VOCAB_TOKENS * CONST_DIMENSION * 4)": "1600",
        "(CONST_MAX_INPUT_TOKENS * CONST_DIMENSION * 4)": "160",
        "(CONST_DIMENSION * CONST_DIMENSION * 4)": "64",
        "-CONST_CHAR_ZERO": "-48"
    }
    for expr, val in replacements.items():
        content = content.replace(expr, val)
        
    # Also comment out original .equ / .eqv lines to avoid duplication warnings/errors
    lines = []
    for line in content.split('\n'):
        stripped = line.strip()
        if stripped.startswith(".equ ") or stripped.startswith(".eqv "):
            lines.append("# " + line)
        else:
            lines.append(line)
    return '\n'.join(lines)

def run_rars(file_path):
    cmd = ["java", "-jar", str(RARS_PATH), "nc", "dec", "a0", "a1", str(file_path)]
    result = subprocess.run(cmd, cwd=PART2_DIR, capture_output=True, text=True)
    
    if result.returncode != 0 and "Program terminated by calling exit" not in result.stdout:
        return None, None, f"RARS Error:\n{result.stderr}\n{result.stdout}"
        
    a0_val = None
    a1_val = None
    for line in result.stdout.split('\n'):
        if line.startswith('a0\t'):
            a0_val = int(line.split('\t')[1])
        elif line.startswith('a1\t'):
            val = int(line.split('\t')[1])
            if val >= 2**31:
                val -= 2**32
            a1_val = val
            
    return a0_val, a1_val, result.stdout

def create_temp_assembly(test_assembly_prefix):
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"File {TEMPLATE_PATH} not found.")
        
    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        template_content = f.read()
        
    # Replace main: with p2_main: to avoid collision
    modified_content = template_content.replace("\nmain:", "\np2_main:")
    modified_content = preprocess_assembly_content(modified_content)
    
    # Preprocess the test prefix to resolve its .zero to .space
    processed_prefix = preprocess_assembly_content(test_assembly_prefix)
    
    full_code = f"""{EQU_HEADER}

{processed_prefix}

# --- START OF PROJECT 2 CODE ---
{modified_content}
"""
    with TEMP_TEST_PATH.open("w", encoding="utf-8") as f:
        f.write(full_code)

def create_temp_p2_assembly():
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"File {TEMPLATE_PATH} not found.")
        
    with TEMPLATE_PATH.open("r", encoding="utf-8") as f:
        content = f.read()
        
    content = preprocess_assembly_content(content)
    
    full_code = f"""{EQU_HEADER}
{content}
"""
    with TEMP_P2_PATH.open("w", encoding="utf-8") as f:
        f.write(full_code)

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_eq(self, test_name, test_assembly_prefix, expected_a0, expected_a1):
        create_temp_assembly(test_assembly_prefix)
        a0, a1, out = run_rars(TEMP_TEST_PATH)
        
        if a0 is None or a1 is None:
            print(f"❌ FAILED: {test_name}")
            print(f"    Error executing RARS:\n{out}")
            self.failed += 1
            return
            
        if a0 == expected_a0 and (expected_a0 != 0 or a1 == expected_a1):
            print(f"✅ PASSED: {test_name}")
            self.passed += 1
        else:
            print(f"❌ FAILED: {test_name}")
            if expected_a0 == 0:
                print(f"    Expected (a0, a1): {(expected_a0, expected_a1)}")
            else:
                print(f"    Expected (a0):     {expected_a0}")
            print(f"    Got (a0, a1):      {(a0, a1)}")
            self.failed += 1

def main():
    if not RARS_PATH.exists():
        print(f"❌ Error: RARS was not found at {RARS_PATH}")
        sys.exit(1)

    if not TEMPLATE_PATH.exists():
        print(f"❌ Error: {TEMPLATE_PATH.name} was not found.")
        sys.exit(1)

    runner = TestRunner()

    print("="*60)
    print("   TESTING INDIVIDUAL FUNCTIONS (UNIT TESTS) - PROJECT 2")
    print("="*60)

    # ----------------------------------------------------
    # 1. UNIT TESTS: dot
    # ----------------------------------------------------
    print("\n--- Testing dot ---")
    
    # 1.1 Normal Dot Product
    runner.assert_eq(
        "dot: Normal Dot Product",
        """.data
test_v1: .word 1, 2, 3
test_v2: .word 4, 5, 6
.text
main:
  la a1, test_v1
  la a2, test_v2
  li a3, 3
  jal ra, dot
  li a7, 10
  ecall""",
        0, 32
    )

    # 1.2 Normal negative values
    runner.assert_eq(
        "dot: Negative values",
        """.data
test_v1: .word -1, -2, -3
test_v2: .word 4, 5, 6
.text
main:
  la a1, test_v1
  la a2, test_v2
  li a3, 3
  jal ra, dot
  li a7, 10
  ecall""",
        0, -32
    )

    # 1.3 Invalid size (< 1)
    runner.assert_eq(
        "dot: Error size < 1",
        """.text
main:
  li a1, 0
  li a2, 0
  li a3, 0
  jal ra, dot
  li a7, 10
  ecall""",
        50, -1
    )

    # 1.4 Multiplication overflow
    runner.assert_eq(
        "dot: Multiplication overflow",
        """.data
test_v1: .word 50000
test_v2: .word 50000
.text
main:
  la a1, test_v1
  la a2, test_v2
  li a3, 1
  jal ra, dot
  li a7, 10
  ecall""",
        200, -1
    )

    # ----------------------------------------------------
    # 2. UNIT TESTS: argmax
    # ----------------------------------------------------
    print("\n--- Testing argmax ---")
    
    # 2.1 Normal Argmax
    runner.assert_eq(
        "argmax: Normal Search",
        """.data
test_v: .word 1, 5, 3, 2
.text
main:
  la a1, test_v
  li a2, 4
  jal ra, argmax
  li a7, 10
  ecall""",
        0, 1
    )

    # 2.2 Argmax with ties (returns lowest index)
    runner.assert_eq(
        "argmax: Tie case",
        """.data
test_v: .word 1, 5, 3, 5, 2
.text
main:
  la a1, test_v
  li a2, 5
  jal ra, argmax
  li a7, 10
  ecall""",
        0, 1
    )

    # 2.3 Invalid size (< 1)
    runner.assert_eq(
        "argmax: Error size < 1",
        """.data
test_v: .word 1
.text
main:
  la a1, test_v
  li a2, 0
  jal ra, argmax
  li a7, 10
  ecall""",
        50, -1
    )

    # ----------------------------------------------------
    # 3. UNIT TESTS: indices_to_tokens
    # ----------------------------------------------------
    print("\n--- Testing indices_to_tokens ---")
    
    # 3.1 Convert index 2 to word
    runner.assert_eq(
        "indices_to_tokens: Normal index access",
        """.data
test_vocab: .string "the\\na\\ncat\\ndog\\n"
.text
main:
  la a0, test_vocab
  li a1, 2
  jal ra, indices_to_tokens
  lb t1, 0(a0)
  li t2, 99   # ASCII 'c'
  bne t1, t2, fail
  li a0, 0
  li a1, 0
  j exit
fail:
  li a0, 1
  mv a1, t1
exit:
  li a7, 10
  ecall""",
        0, 0
    )

    # ----------------------------------------------------
    # 4. UNIT TESTS: read_file
    # ----------------------------------------------------
    print("\n--- Testing read_file ---")
    
    # Write a temporary file for reading
    test_file_path = "test_read.txt"
    with (PART2_DIR / test_file_path).open("w", encoding="utf-8") as f:
        f.write("Hello RISC-V!")

    runner.assert_eq(
        "read_file: Normal read",
        f""".data
test_filename: .string "{test_file_path}"
test_buffer:   .zero 32
.text
main:
  la a0, test_filename
  la a1, test_buffer
  li a2, 32
  jal ra, read_file
  la t0, test_buffer
  lw t1, 0(t0)        # "Hell"
  li t2, 0x6c6c6548    # "Hell" in Little Endian
  bne t1, t2, fail
  mv a1, a0            # Pass the number of read bytes in a1
  li a0, 0
  j exit
fail:
  li a0, 1
  mv a1, t1
exit:
  li a7, 10
  ecall""",
        0, 13
    )

    if (PART2_DIR / test_file_path).exists():
        (PART2_DIR / test_file_path).unlink(missing_ok=True)

    # ----------------------------------------------------
    # 5. UNIT TESTS: parse_matrix_buffer
    # ----------------------------------------------------
    print("\n--- Testing parse_matrix_buffer ---")
    
    runner.assert_eq(
        "parse_matrix_buffer: Matrix with integers and negatives",
        """.data
test_buffer: .string "-5 -3\\n6 -1\\n"
test_matrix: .zero 16
.text
main:
  la a0, test_matrix
  la a1, test_buffer
  jal ra, parse_matrix_buffer
  la t0, test_matrix
  lw t1, 0(t0)
  lw t2, 4(t0)
  lw t3, 8(t0)
  lw t4, 12(t0)
  
  li t5, -5
  bne t1, t5, fail
  li t5, -3
  bne t2, t5, fail
  li t5, 6
  bne t3, t5, fail
  li t5, -1
  bne t4, t5, fail
  
  li a0, 0
  # a1 already contains the matrix rows (should be 2)
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 2
    )

    # ----------------------------------------------------
    # 6. UNIT TESTS: tokens_to_indices
    # ----------------------------------------------------
    print("\n--- Testing tokens_to_indices ---")
    
    runner.assert_eq(
        "tokens_to_indices: Translation of words to indices",
        """.data
test_vocab:  .string "the\\na\\ncat\\ndog\\n"
test_input:  .string "a\\ndog\\n"
test_indices:.zero 16
.text
main:
  la a0, test_indices
  la a2, test_input
  la a3, test_vocab
  jal ra, tokens_to_indices
  la t0, test_indices
  lw t1, 0(t0) # index of "a" -> 1
  lw t2, 4(t0) # index of "dog" -> 3
  
  li t3, 1
  bne t1, t3, fail
  li t3, 3
  bne t2, t3, fail
  
  li a0, 0
  # a1 already contains the size (should be 2)
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 2
    )

    # ----------------------------------------------------
    # 7. UNIT TESTS: build_input_embeddings_matrix
    # ----------------------------------------------------
    print("\n--- Testing build_input_embeddings_matrix ---")
    
    runner.assert_eq(
        "build_input_embeddings_matrix: Matrix construction",
        """.data
test_vocab_emb: .word 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12
test_indices:   .word 2, 0
test_out_emb:   .zero 32
.text
main:
  la a0, test_out_emb
  la a1, test_vocab_emb
  la a2, test_indices
  li a3, 2
  jal ra, build_input_embeddings_matrix
  
  la t0, test_out_emb
  
  lw t1, 0(t0)
  li t2, 9
  bne t1, t2, fail
  
  lw t1, 4(t0)
  li t2, 10
  bne t1, t2, fail
  
  lw t1, 8(t0)
  li t2, 11
  bne t1, t2, fail
  
  lw t1, 12(t0)
  li t2, 12
  bne t1, t2, fail
  
  lw t1, 16(t0)
  li t2, 1
  bne t1, t2, fail
  
  lw t1, 20(t0)
  li t2, 2
  bne t1, t2, fail
  
  lw t1, 24(t0)
  li t2, 3
  bne t1, t2, fail
  
  lw t1, 28(t0)
  li t2, 4
  bne t1, t2, fail
  
  li a0, 0
  li a1, 2
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 2
    )

    # ----------------------------------------------------
    # 8. UNIT TESTS: matrix_multiply
    # ----------------------------------------------------
    print("\n--- Testing matrix_multiply ---")
    
    runner.assert_eq(
        "matrix_multiply: Multiplication 2x3 by 3x2",
        """.data
test_A: .word 1, 2, 3, 4, 5, 6
test_B: .word 7, 8, 9, 10, 11, 12
test_C: .zero 16
.text
main:
  la a0, test_C
  la a1, test_A
  li a2, 2
  li a3, 3
  la a4, test_B
  li a5, 3
  li a6, 2
  jal ra, matrix_multiply
  
  la t0, test_C
  lw t1, 0(t0)  # 58
  lw t2, 4(t0)  # 64
  lw t3, 8(t0)  # 139
  lw t4, 12(t0) # 154
  
  li t5, 58
  bne t1, t5, fail
  li t5, 64
  bne t2, t5, fail
  li t5, 139
  bne t3, t5, fail
  li t5, 154
  bne t4, t5, fail
  
  li a0, 0
  li a1, 0
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 0
    )

    # ----------------------------------------------------
    # 9. UNIT TESTS: compute_scores
    # ----------------------------------------------------
    print("\n--- Testing compute_scores ---")
    
    runner.assert_eq(
        "compute_scores: Attention scores calculation",
        """.data
test_Q: .word 1, 2, 3, 4, 5, 6
test_K: .word 7, 8, 9, 10, 11, 12
test_S: .zero 8
.text
main:
  la a0, test_S
  la a1, test_Q
  la a2, test_K
  li a3, 2 # rows
  li a4, 3 # cols
  li a5, 1 # target index
  jal ra, compute_scores
  
  la t0, test_S
  lw t1, 0(t0) # 122
  lw t2, 4(t0) # 167
  
  li t3, 122
  bne t1, t3, fail
  li t3, 167
  bne t2, t3, fail
  
  li a0, 0
  li a1, 0
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 0
    )

    # ----------------------------------------------------
    # 10. UNIT TESTS: select_vector_in_matrix
    # ----------------------------------------------------
    print("\n--- Testing select_vector_in_matrix ---")
    
    runner.assert_eq(
        "select_vector_in_matrix: Row selection",
        """.data
test_matrix: .word 1, 2, 3, 4, 5, 6, 7, 8
.text
main:
  la a1, test_matrix
  li a2, 2
  li a3, 4
  li a4, 1
  jal ra, select_vector_in_matrix
  la t0, test_matrix
  addi t0, t0, 16
  bne a0, t0, fail
  
  li a0, 0
  li a1, 0
  j exit
fail:
  li a0, 1
  li a1, -1
exit:
  li a7, 10
  ecall""",
        0, 0
    )

    # ----------------------------------------------------
    # 11. UNIT TESTS: decide_next_token
    # ----------------------------------------------------
    print("\n--- Testing decide_next_token ---")
    
    runner.assert_eq(
        "decide_next_token: Choice of the most similar token",
        """.data
test_target:    .word 2, -1, 3, 0
test_vocab_emb: .word 1, 1, 1, 1, 3, -2, 1, 0, -1, 0, 1, 5
.text
main:
  la a0, test_target
  la a1, test_vocab_emb
  li a2, 3
  jal ra, decide_next_token
  mv a1, a0
  li a0, 0
  li a7, 10
  ecall""",
        0, 1
    )

    # Clean up any temporary assembly file
    if TEMP_TEST_PATH.exists():
        TEMP_TEST_PATH.unlink(missing_ok=True)

    # ----------------------------------------------------
    # 12. INTEGRATION TESTS (END-TO-END FLOW)
    # ----------------------------------------------------
    print("\n" + "="*60)
    print("   TESTING FULL FLOW (INTEGRATION TESTS)")
    print("="*60)

    # Create temporary next_token_predictor.s with preprocessed expressions so RARS can compile it
    create_temp_p2_assembly()

    # List of integration test cases: (input words list, expected predicted word)
    integration_cases = [
        (["a", "boy", "eats"], "food"),
        (["a", "girl", "eats"], "food"),
        (["a", "bird", "drinks"], "water"),
        (["a", "fish", "needs"], "water"),
        (["a", "boy", "needs"], "food")
    ]

    input_filename = PART2_DIR / "input.txt"
    backup_filename = PART2_DIR / "input.txt.bak"

    # Backup the original input.txt
    backup_made = False
    if input_filename.exists():
        shutil.copyfile(input_filename, backup_filename)
        backup_made = True

    integration_passed = 0
    integration_failed = 0

    try:
        for idx, (words, expected) in enumerate(integration_cases, 1):
            # Write current test words to input.txt
            with open(input_filename, "w") as f:
                for w in words:
                    f.write(w + "\n")
            
            # Run the entire temp_p2.s program in RARS
            cmd = ["java", "-jar", str(RARS_PATH), "nc", "dec", str(TEMP_P2_PATH)]
            result = subprocess.run(cmd, cwd=PART2_DIR, capture_output=True, text=True)
            
            if result.returncode != 0 and "Program terminated by calling exit" not in result.stdout:
                print(f"❌ INTEGRATION FAILED {idx}: {' '.join(words)} -> Error executing RARS:\n{result.stderr}")
                integration_failed += 1
                continue
                
            # Parse the predicted token from the output
            lines = result.stdout.split('\n')
            predicted_word = None
            for i, line in enumerate(lines):
                if "=== Decision ===" in line:
                    # The next non-empty line should be the predicted token
                    for next_line in lines[i+1:]:
                        cleaned = next_line.strip()
                        if cleaned:
                            predicted_word = cleaned
                            break
                    break
            
            if predicted_word == expected:
                print(f"✅ INTEGRATION PASSED {idx}: {' '.join(words)} -> {predicted_word}")
                integration_passed += 1
            else:
                print(f"❌ INTEGRATION FAILED {idx}: {' '.join(words)}")
                print(f"    Expected: {expected}")
                print(f"    Got:      {predicted_word}")
                integration_failed += 1

    finally:
        # Restore backup
        if backup_made:
            shutil.copyfile(backup_filename, input_filename)
            backup_filename.unlink(missing_ok=True)
        elif input_filename.exists():
            input_filename.unlink(missing_ok=True)
            
        # Clean up temp_p2.s
        if TEMP_P2_PATH.exists():
            TEMP_P2_PATH.unlink(missing_ok=True)

    # ----------------------------------------------------
    # GENERAL SUMMARY
    # ----------------------------------------------------
    print("\n" + "="*60)
    print("   PROJECT 2 TEST SUMMARY")
    print("="*60)
    total_passed = runner.passed + integration_passed
    total_failed = runner.failed + integration_failed
    print(f"Unit Tests:  {runner.passed} passed, {runner.failed} failed.")
    print(f"Integration: {integration_passed} passed, {integration_failed} failed.")
    print(f"General Total: {total_passed} passed, {total_failed} failed.")
    print("="*60)

    if total_failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()