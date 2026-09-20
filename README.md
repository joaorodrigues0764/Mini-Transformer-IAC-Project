# Mini-Transformer: RISC-V Assembly & Custom 16-bit Processor

[![CI](https://github.com/joaorodrigues0764/Mini-Transformer-IAC-Project/actions/workflows/ci.yml/badge.svg)](https://github.com/joaorodrigues0764/Mini-Transformer-IAC-Project/actions/workflows/ci.yml)

A low-level computer architecture project built around a simplified Mini-Transformer next-token prediction pipeline, combining **RISC-V assembly**, **automated testing**, and a **custom 16-bit processor designed in Logisim-Evolution**.

Developed for **Introduction to Computer Architecture (IAC)** at **Instituto Superior Técnico (IST)**.

## Overview

The project explores the same computation at three different levels:

1. **Part 1 — RISC-V Vector Operations**  
   Low-level implementations of `argmax`, `dot`, and indexed vector selection, including input validation and signed overflow handling.

2. **Part 2 — Self-Attention & Next-Token Prediction**  
   A complete assembly implementation of a simplified single-layer self-attention pipeline. It reads vocabulary, input, embeddings, and projection matrices; computes the \(Q\), \(K\), and \(V\) representations; scores the last input token against previous tokens; and selects the most similar vocabulary embedding as the predicted next token.

3. **Part 3 — Custom 16-bit Processor**  
   A single-cycle processor designed in Logisim-Evolution with an 8-register file, a 2-bit instruction opcode, and custom `dot` / `dota` instructions aimed at accelerating vector operations.

## Technical Highlights

- RISC-V assembly programming
- Low-level file I/O and text parsing
- Integer vector and matrix operations
- Signed integer overflow detection
- Stack-based temporary storage
- Self-attention style dot-product scoring
- Custom instruction set architecture (ISA)
- 16-bit datapath and control logic
- Multi-port register file
- Hardware-software co-design
- Automated Python test runners
- GitHub Actions continuous integration

## Repository Structure

```text
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── processor-architecture.md
├── part1/
│   ├── argmax.s
│   ├── dot.s
│   ├── select.s
│   └── test_assembly.py
├── part2/
│   ├── data files (*.txt)
│   ├── next_token_predictor.s
│   └── test_assembly.py
├── part3/
│   └── processor.circ
├── tools/
│   └── rars.jar
├── .gitignore
├── Makefile
└── README.md
```

## Requirements

- Python 3
- Java 17 or newer
- GNU Make
- Logisim-Evolution 4.1.0 or a compatible version for Part 3

RARS is included in `tools/rars.jar`, so no separate RARS installation is required to run the automated assembly tests.

## Running the Tests

From the repository root:

```bash
make test
```

Run each part independently:

```bash
make test-part1
make test-part2
```

The test runners are path-independent, so they can also be executed directly from the repository root:

```bash
python3 part1/test_assembly.py
python3 part2/test_assembly.py
```

The test suite covers:

- Vector operations and edge cases in Part 1
- Arithmetic overflow cases
- Individual helper functions in Part 2
- End-to-end next-token prediction cases

## Part 3 — Processor

Open [`part3/processor.circ`](part3/processor.circ) in Logisim-Evolution to inspect and simulate the processor.

The design documentation, including the ISA and datapath decisions, is available in [`docs/processor-architecture.md`](docs/processor-architecture.md).

The circuit is organized into modular subcircuits for the main datapath, control logic, ALU operations, and register file rather than implementing the entire processor as one flat circuit.

## Automation

GitHub Actions runs the automated Part 1 and Part 2 test suites on pushes and pull requests.

## Project Context

This repository contains the final implementation and supporting documentation of an academic computer architecture project. The repository structure and documentation are organized for reproducibility and public technical reference.
