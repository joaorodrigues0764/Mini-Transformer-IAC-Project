PYTHON ?= python3

.PHONY: test test-part1 test-part2 clean

test: test-part1 test-part2

test-part1:
	$(PYTHON) part1/test_assembly.py

test-part2:
	$(PYTHON) part2/test_assembly.py

clean:
	rm -f part1/temp_test.s
	rm -f part2/temp_test.s part2/temp_p2.s part2/test_read.txt part2/input.txt.bak
	rm -rf part1/__pycache__ part2/__pycache__
