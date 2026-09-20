# Processor Architecture

Part 3 implements a custom **single-cycle 16-bit processor** in Logisim-Evolution, designed around the vector operations required by the Mini-Transformer computation.

The design is modular: the `main` circuit connects dedicated subcircuits for the control unit, ALU operations, register file, and custom instruction datapaths.

## Instruction Set Architecture

The processor uses a 16-bit instruction word with a **2-bit opcode**, giving four primary instructions.

| Instruction | Opcode | Format (MSB → LSB) | Operation |
|---|---:|---|---|
| `li rd, imm` | `00` | `imm[10:0] \| rd[2:0] \| opcode[1:0]` | \(R[rd] \leftarrow imm\) |
| `add rd, rs1` | `01` | `0^8 \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | \(R[rd] \leftarrow R[rd] + R[rs1]\) |
| `dot rd, rs1` | `10` | `0^8 \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | \(R[rd] \leftarrow R[rd]R[rs1] + R[rd+1]R[rs1+1]\) |
| `dota rd, rs1, rs2` | `11` | `0^5 \| rs2[2:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | \(R[rd] \leftarrow R[rd] + R[rs1]R[rs2] + R[rs1+1]R[rs2+1]\) |

The `dot` and `dota` instructions use consecutive registers to represent 2-element vectors. The architecture therefore trades opcode space for compact vector operations that can be executed directly by the custom datapath.

## Datapath

The processor contains:

- An **8-register register file** (`R0`–`R7`)
- A **4-port read interface** to support parallel vector operands
- A **16-bit ALU**
- Dedicated multiplication and addition logic for vector dot products
- A control unit that decodes the 2-bit opcode
- Immediate-value handling for `li`

For `dot`, the datapath obtains two pairs of operands in parallel, computes two products, and sums them.

For `dota`, the dot-product result is combined with the value already stored in the destination register.

## Register File

The 3-bit register identifiers allow eight registers.

The four read paths make it possible to access the base operands and their consecutive registers in the same cycle. Small adders generate the `base + 1` register addresses required by the 2-element vector operations.

This organization was chosen to keep the instruction encoding compact while supporting the vector operations needed by the project.

## Control Unit

The control unit decodes the 2-bit opcode and generates the signals required by the datapath:

- ALU operation selection
- Register write enable
- Register-file read-address selection
- Immediate-value routing

Because the opcode directly identifies the instruction class, the decoder remains small and easy to trace in simulation.

## Design Trade-offs

The 16-bit instruction width creates a strict encoding budget. Allocating two bits to the opcode leaves limited space for additional instructions, but it allows the remaining bits to be used efficiently for register identifiers and an 11-bit immediate.

The custom vector instructions prioritize the operations most relevant to the Mini-Transformer workload instead of attempting to build a general-purpose instruction set.

## Simulation

Open [`../part3/processor.circ`](../part3/processor.circ) with Logisim-Evolution 4.1.0 or a compatible release.

The circuit contains modular subcircuits for the main processor components, making it possible to inspect and simulate the datapath at different abstraction levels.
