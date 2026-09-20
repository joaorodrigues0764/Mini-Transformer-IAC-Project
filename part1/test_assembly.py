import os
import subprocess
import sys
from pathlib import Path

PART1_DIR = Path(__file__).resolve().parent
ROOT_DIR = PART1_DIR.parent
RARS_PATH = ROOT_DIR / "tools" / "rars.jar"
TEMP_TEST_PATH = PART1_DIR / "temp_test.s"

INT32_MIN = -2147483648
INT32_MAX = 2147483647


def run_rars(file_path: Path):
    cmd = ["java", "-jar", str(RARS_PATH), "nc", "dec", "a0", "a1", str(file_path)]
    result = subprocess.run(
        cmd,
        cwd=PART1_DIR,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0 and "Program terminated by calling exit" not in result.stdout:
        return None, None, f"RARS Error:\n{result.stderr}\n{result.stdout}"

    a0_val = None
    a1_val = None

    for line in result.stdout.splitlines():
        if line.startswith("a0\t"):
            a0_val = int(line.split("\t")[1])
        elif line.startswith("a1\t"):
            val = int(line.split("\t")[1])
            if val >= 2**31:
                val -= 2**32
            a1_val = val

    return a0_val, a1_val, result.stdout


def to_word_list(arr):
    return "0" if not arr else ", ".join(map(str, arr))


def create_temp_assembly(func_name, func_code, arr1, arr2=None, index=None):
    if func_name == "argmax":
        data_section = f"""
.data
A:    .word {to_word_list(arr1)}
SIZE: .word {len(arr1)}

.text
main:
  la a1, A
  lw a2, SIZE
  jal ra, argmax
exit:
  li a7, 10
  ecall

{func_code}
"""
    elif func_name == "select":
        data_section = f"""
.data
A:    .word {to_word_list(arr1)}
SIZE: .word {len(arr1)}
INDEX:.word {index}

.text
main:
  la a1, A
  lw a2, SIZE
  lw a3, INDEX
  jal ra, select
exit:
  li a7, 10
  ecall

{func_code}
"""
    elif func_name == "dot":
        data_section = f"""
.data
A:    .word {to_word_list(arr1)}
B:    .word {to_word_list(arr2)}
SIZE: .word {len(arr1)}

.text
main:
  la a1, A
  la a2, B
  lw a3, SIZE
  jal ra, dot
exit:
  li a7, 10
  ecall

{func_code}
"""
    else:
        raise ValueError(f"Unsupported function: {func_name}")

    TEMP_TEST_PATH.write_text(data_section, encoding="utf-8")


class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_eq(self, test_name, func_name, expected, func_code, arr1, arr2=None, index=None):
        create_temp_assembly(func_name, func_code, arr1, arr2, index)
        a0, a1, out = run_rars(TEMP_TEST_PATH)

        expected_status, expected_res = expected
        got_status = a0
        got_res = a1

        if expected_status != 0:
            if got_status == expected_status:
                print(f"✅ PASSED: {test_name}")
                self.passed += 1
            else:
                print(f"❌ FAILED: {test_name}")
                print(f"    Expected Status: {expected_status}")
                print(f"    Got Status:      {got_status}")
                self.failed += 1
        elif got_status == expected_status and got_res == expected_res:
            print(f"✅ PASSED: {test_name}")
            self.passed += 1
        else:
            print(f"❌ FAILED: {test_name}")
            print(f"    Expected (Status, Res): {expected}")
            print(f"    Got (Status, Res):      {(got_status, got_res)}")
            self.failed += 1


def extract_func(filename, func_name):
    path = PART1_DIR / filename
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    func_start = content.find(f"{func_name}:")
    if func_start == -1:
        return None
    return content[func_start:]


def main():
    if not RARS_PATH.exists():
        print(f"❌ Error: RARS was not found at {RARS_PATH}")
        sys.exit(1)

    runner = TestRunner()

    code_argmax = extract_func("argmax.s", "argmax")
    code_select = extract_func("select.s", "select")
    code_dot = extract_func("dot.s", "dot")

    if not all((code_argmax, code_select, code_dot)):
        print("❌ Error: one or more assembly functions could not be loaded.")
        sys.exit(1)

    print("=" * 60)
    print("   TESTING ASSEMBLY: argmax.s")
    print("=" * 60)
    runner.assert_eq("Normal list", "argmax", (0, 2), code_argmax, [1, 2, 5, 4])
    runner.assert_eq("List with ties", "argmax", (0, 1), code_argmax, [1, 5, 5, 4])
    runner.assert_eq("All negative", "argmax", (0, 0), code_argmax, [-1, -2, -5, -4])
    runner.assert_eq("Error: Size < 1", "argmax", (50, -1), code_argmax, [])

    print("\n" + "=" * 60)
    print("   TESTING ASSEMBLY: select.s")
    print("=" * 60)
    runner.assert_eq("Normal access", "select", (0, 6), code_select, [-6, -1, 6, 1], index=2)
    runner.assert_eq("Error: Size < 1", "select", (50, -1), code_select, [], index=0)
    runner.assert_eq("Error: Index = Size", "select", (100, -1), code_select, [1, 2, 3], index=3)
    runner.assert_eq("Error: Index > Size", "select", (100, -1), code_select, [1, 2], index=5)
    runner.assert_eq("Error: Index < 0", "select", (100, -1), code_select, [1, 2, 3], index=-1)

    print("\n" + "=" * 60)
    print("   TESTING ASSEMBLY: dot.s")
    print("=" * 60)
    runner.assert_eq("Normal dot product", "dot", (0, 32), code_dot, [1, 2, 3], [4, 5, 6])
    runner.assert_eq("Normal negative values", "dot", (0, -32), code_dot, [-1, -2, -3], [4, 5, 6])
    runner.assert_eq("Error: Size < 1", "dot", (50, -1), code_dot, [], [])

    runner.assert_eq("Error 200: Positive multiplication overflow", "dot", (200, -1), code_dot, [50000], [50000])
    runner.assert_eq("Error 200: Negative multiplication overflow", "dot", (200, -1), code_dot, [50000], [-50000])
    runner.assert_eq("Error 200: INT32_MIN * -1 overflow", "dot", (200, -1), code_dot, [INT32_MIN], [-1])
    runner.assert_eq("Error 200: Positive accumulation overflow", "dot", (200, -1), code_dot, [INT32_MAX, 1], [1, 1])
    runner.assert_eq("Error 200: Negative accumulation overflow", "dot", (200, -1), code_dot, [INT32_MIN, -1], [1, 1])

    print("\n   --- Edge cases ---")
    runner.assert_eq("Two positive products", "dot", (0, 2), code_dot, [1, 1], [1, 1])
    runner.assert_eq("Two negative products", "dot", (0, -2), code_dot, [-1, -1], [1, 1])

    print("\n" + "=" * 60)
    print(f"General Assembly Summary: {runner.passed} passed, {runner.failed} failed.")
    print("=" * 60)

    TEMP_TEST_PATH.unlink(missing_ok=True)

    if runner.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
