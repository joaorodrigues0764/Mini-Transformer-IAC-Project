# IAC - Mini-Transformer / RISC-V Next-Token Predictor & Custom Hardware Accelerator

[English](#english) | [Português](#português)

---

## English

### Project Overview
This project was developed as part of the **IAC (Introduction to Computer Architecture / Introdução à Arquitetura de Computadores)** course at **Instituto Superior Técnico (IST)**. The objective is to design, implement, and accelerate a **Mini-Transformer next-token prediction pipeline** (specifically focusing on a Single-Layer Self-Attention step) using a hardware-software co-design approach. 

The project spans low-level software engineering in RISC-V assembly and custom hardware architecture design in Logisim, split into three coherent development phases:
1. **Part 1 (P1)**: Implementation of low-level vector mathematical routines in pure RISC-V assembly.
2. **Part 2 (P2)**: Implementation of a full Single-Layer Self-Attention and Next-Token Prediction pipeline in pure RISC-V assembly.
3. **Part 3 (P3)**: Hardware design of a custom 16-bit processor datapath, control unit, and arithmetic logical unit (ALU) in Logisim, optimized with dedicated instructions to accelerate the transformer's matrix operations.

---

### Key Objectives
- **RISC-V Vector Assembly Programming**: Write high-performance, low-level mathematical functions with robust overflow and out-of-bounds error handling.
- **Attention Pipeline Software Emulation**: Implement file I/O parsing, tokenization, dynamic embedding lookup, projections ($Q$, $K$, $V$), attention scoring, value vector selection, and vocabulary similarity lookup (next-token prediction) in assembly.
- **Hardware-Software Co-Design**: Architect a custom 16-bit processor featuring a 4-port register file and customized ALU instructions (`dot` and `dota`) to execute 2D vector dot products and accumulations natively in hardware.

---

### Phase-by-Phase Reference

#### Part 1: RISC-V Vector Operations
Implements core mathematical routines in RISC-V assembly for 1D integer arrays. These files are tested using the **RARS (RISC-V Assembler and Runtime Simulator)**:
- **[argmax.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/argmax.s)**: Scans an integer array to find the index of the largest element. Employs tie-breaking logic returning the smallest index in case of duplicate maximum values, with input size validation.
- **[dot.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/dot.s)**: Computes the dot product of two integer arrays. Implements full signed overflow detection for both multiplication and accumulation stages, returning specific exit codes on arithmetic overflow or invalid size.
- **[select.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/select.s)**: Selects and extracts a specific element from an integer array given an index, complete with array bounds checking (negative indices, and out-of-limits exceptions).

#### Part 2: Single-Layer Self-Attention & Prediction
A complete software emulation of a Single-Layer Self-Attention token predictor. The pipeline processes files, parses text representations of matrices into memory buffers, tokenizes strings, and performs calculations:
- **File Input & Buffer Parsing**: Dynamically reads vocabulary definitions (`vocab.txt`), input sequence (`input.txt`), projection matrices ($W_Q$, $W_K$, $W_V$), and vocabulary word representations (`embeddings.txt`), translating ASCII matrices into memory-resident integers.
- **Tokenization**: Maps the incoming raw space-separated text to their corresponding vocabulary indices by executing an optimized assembly string matching algorithm.
- **Projection & Scores**: Multiplies the input sequence embeddings ($X$) by the weight matrices ($W_Q, W_K, W_V$) to yield the Query ($Q$), Key ($K$), and Value ($V$) matrices. It then computes the dot-product similarity scores between the query vector of the *last input token* and the key vectors of all previous tokens.
- **Prediction**: Applies `argmax` to select the value vector in $V$ with the highest attention score, computes the dot-product similarity between this selected vector and all vocabulary embeddings, and identifies the best match to output the predicted next word.

#### Part 3: Custom 16-bit Logisim Processor Design
A custom hardware accelerator tailormade to run the Mini-Transformer's vector operations in logisim (`P3_V2.circ`). It implements a 16-bit word Instruction Set Architecture (ISA) with 8 registers (`R0` to `R7`) and a 2-bit opcode.

##### Instruction Set Architecture (ISA)
| Instruction | Opcode | Format (MSB to LSB) | Description | Formula / Operation |
|-------------|--------|---------------------|-------------|---------------------|
| `li rd, imm` | `00` | `immediate[10:0] \| rd[2:0] \| opcode[1:0]` | Load 11-bit immediate value | $R[rd] \leftarrow \text{imm}$ |
| `add rd, rs1` | `01` | `zeros[7:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Simple 16-bit addition | $R[rd] \leftarrow R[rd] + R[rs1]$ |
| `dot rd, rs1` | `10` | `zeros[7:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Parallel 2D Vector Dot Product | $R[rd] \leftarrow (R[rd] \times R[rs1]) + (R[rd+1] \times R[rs1+1])$ |
| `dota rd, rs1, rs2` | `11` | `zeros[4:0] \| rs2[2:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Vector Dot-Accumulate | $R[rd] \leftarrow R[rd] + (R[rs1] \times R[rs2]) + (R[rs1+1] \times R[rs2+1])$ |

##### Hardware Design Architecture
- **Register File with 4 Read Ports**: To compute 2D vector dot products in a single clock cycle, the register file provides 4 simultaneous read ports. Port 1 and 2 read the base registers ($R[rd]$ / $R[rs1]$ or $R[rs1]$ / $R[rs2]$), while internal 3-bit adders calculate consecutive indices in parallel, allowing Port 3 and 4 to read the corresponding consecutive vector components ($R[base+1]$) with zero clock overhead.
- **Custom ALU Layout**:
  - **Pass-through logic** for immediate values (`li`).
  - **16-bit Adder** for basic arithmetic (`add`).
  - **Vector Dot Product Block**: Employs two 16-bit hardware multipliers running in parallel, feeding into a 16-bit adder.
  - **Accumulator Bypass**: Connects the output of Read Port 1 ($R[rd]$) directly to a final accumulation stage during the execution of `dota`, summing it with the dot product result.
- **Control Unit**: Decodes the 2-bit opcode to drive the datapath selectors (`SinalALU`), controls register file read multiplexers (`OrigAlu` is set to `1` only for `dota` instructions to redirect addresses), and keeps the register write enable line (`RegWrite`) active.

---

### Command & Testing Reference
Automated Python test runners are included in each assembly phase to verify the correctness of the low-level logic against the RARS runtime environment.

To run the unit tests for **Part 1** routines:
```bash
cd P1_skeleton_v1.1
python3 test_assembly.py
```

To run the comprehensive unit and integration pipeline tests for **Part 2**:
```bash
cd P2_skeleton
python3 test_assembly.py
```

To simulate and test the **Part 3** processor datapath:
1. Open Logisim or Logisim-Evolution.
2. Load the circuit diagram: `P3/P3_V2.circ`.
3. Load the machine code instructions into the Instruction Memory ROM.
4. Enable the simulation clock to step through execution.

---

## Português

### Resumo do Projeto
Este projeto foi desenvolvido no âmbito da Unidade Curricular de **IAC (Introdução à Arquitetura de Computadores)** no **Instituto Superior Técnico (IST)**. O objetivo é desenhar, implementar e acelerar um **pipeline de previsão do próximo token (Mini-Transformer)**, focando-se num passo de Auto-Atenção de Camada Única (Single-Layer Self-Attention), seguindo uma abordagem de co-desenho hardware-software.

O projeto estende-se desde engenharia de software de baixo nível em assembly RISC-V até ao desenho de uma arquitetura de hardware personalizada em Logisim, dividindo-se em três fases distintas:
1. **Parte 1 (P1)**: Implementação de rotinas matemáticas vetoriais básicas em assembly RISC-V.
2. **Parte 2 (P2)**: Implementação do fluxo completo de Auto-Atenção e previsão de tokens em assembly RISC-V.
3. **Parte 3 (P3)**: Desenho de uma arquitetura de processador de 16 bits, unidade de controlo e ALU em Logisim, otimizados com instruções dedicadas à aceleração de operações matriciais do transformador.

---

### Objetivos Principais
- **Programação Vetorial em RISC-V**: Desenvolver rotinas matemáticas de baixo nível com validações robustas contra overflow aritmético e acessos fora de limites.
- **Emulação do Pipeline de Atenção**: Codificar em assembly o carregamento de ficheiros, parsing de matrizes textuais, tokenização de texto, procura de embeddings, projeções lineares ($Q$, $K$, $V$), cálculo de scores de atenção e correspondência por similaridade de cosseno.
- **Co-Desenho de Hardware Dedicado**: Projetar um processador de 16 bits em Logisim com um banco de registos de 4 portas de leitura e instruções de ALU personalizadas (`dot` e `dota`) para efetuar produtos escalares e acumulações diretamente em hardware.

---

### Guia de Desenvolvimento por Fase

#### Parte 1: Operações Vetoriais em RISC-V
Implementação das rotinas aritméticas elementares para vetores de inteiros, validadas com o simulador **RARS**:
- **[argmax.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/argmax.s)**: Procura num vetor de inteiros o índice do maior elemento. Em caso de empate, devolve o menor índice. Inclui validação de tamanho.
- **[dot.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/dot.s)**: Calcula o produto escalar de dois vetores. Deteta e trata de forma robusta o overflow com sinal durante as fases de multiplicação e acumulação.
- **[select.s](file:///Users/joseconceicao/Documents/Universidade/IAC/Mini-Transformer-IAC-Project/P1_skeleton_v1.1/select.s)**: Obtém o valor de um elemento no índice fornecido, contendo verificação estrita de limites do vetor.

#### Parte 2: Pipeline de Auto-Atenção & Previsão
Desenvolvimento em assembly do algoritmo de Self-Attention completo, englobando todas as transformações de dados necessárias:
- **Leitura e Parsing de Ficheiros**: Processa as definições do vocabulário (`vocab.txt`), entrada (`input.txt`), matrizes de projeção ($W_Q$, $W_K$, $W_V$) e representações do vocabulário (`embeddings.txt`), convertendo representações textuais em inteiros na memória RAM.
- **Tokenização**: Traduz os termos em texto da sequência de entrada para os respetivos índices numéricos do vocabulário recorrendo a um algoritmo de correspondência de strings em assembly.
- **Projeções e Atenção**: Executa multiplicações de matrizes para obter $Q$, $K$ e $V$. Determina o score de similaridade (produto escalar) entre o vetor Query do *último token de entrada* e os vetores Key de todos os tokens anteriores.
- **Previsão**: Utiliza a função `argmax` para selecionar o vetor de Value em $V$ com maior peso, calcula a semelhança por produto escalar com todas as palavras do vocabulário e escolhe o termo ideal para impressão no ecrã.

#### Parte 3: Processador Personalizado de 16 bits em Logisim
Arquitetura de hardware dedicada no Logisim (`P3_V2.circ`) implementada com um conjunto de instruções customizadas (ISA) com 8 registos genéricos (`R0` a `R7`) e opcode de 2 bits.

##### Conjunto de Instruções (ISA)
| Instrução | Opcode | Formato (MSB para LSB) | Descrição | Operação / Fórmula |
|-------------|--------|---------------------|-------------|---------------------|
| `li rd, imm` | `00` | `imediato[10:0] \| rd[2:0] \| opcode[1:0]` | Carrega valor imediato de 11 bits | $R[rd] \leftarrow \text{imm}$ |
| `add rd, rs1` | `01` | `zeros[7:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Adição simples de 16 bits | $R[rd] \leftarrow R[rd] + R[rs1]$ |
| `dot rd, rs1` | `10` | `zeros[7:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Produto Escalar Paralelo de Vetores 2D | $R[rd] \leftarrow (R[rd] \times R[rs1]) + (R[rd+1] \times R[rs1+1])$ |
| `dota rd, rs1, rs2` | `11` | `zeros[4:0] \| rs2[2:0] \| rs1[2:0] \| rd[2:0] \| opcode[1:0]` | Produto Escalar Vetorial com Acumulação | $R[rd] \leftarrow R[rd] + (R[rs1] \times R[rs2]) + (R[rs1+1] \times R[rs2+1])$ |

##### Arquitetura Física da Unidade Central de Processamento
- **Banco de Registos com 4 Portas de Leitura**: Para permitir a execução do produto escalar de vetores bidimensionais num único ciclo de relógio, o banco possui 4 portas de leitura paralelas. Duas portas leem os registos base indicados, enquanto somadores internos de 3 bits calculam os endereços adjacentes de forma concorrente para as portas 3 e 4 lerem os componentes seguintes do vetor ($R[base+1]$).
- **Estrutura Interna da ALU**:
  - **Passagem direta** de dados para carga de imediatos (`li`).
  - **Somador de 16 bits** clássico para adição comum (`add`).
  - **Bloco de Produto Escalar**: Composto por dois multiplicadores de 16 bits em paralelo acoplados a um somador intermédio.
  - **Desvio de Acumulador**: Liga o conteúdo do registo de destino $R[rd]$ lido diretamente à saída do bloco de produto escalar, somando-os no ciclo de execução da instrução `dota`.
- **Unidade de Controlo**: Descodifica a instrução para comandar a ALU (`SinalALU`), sinaliza a escrita de registo (`RegWrite`) e redireciona os barramentos de leitura do banco (`OrigAlu` ativa-se apenas na instrução `dota`).

---

### Execução e Testes Aritméticos
A verificação das soluções de software é efetuada localmente utilizando scripts automatizados em Python.

Para executar os testes unitários das rotinas da **Parte 1**:
```bash
cd P1_skeleton_v1.1
python3 test_assembly.py
```

Para correr os testes funcionais de integração do pipeline da **Parte 2**:
```bash
cd P2_skeleton
python3 test_assembly.py
```

Para simular o processador da **Parte 3** no Logisim:
1. Abra o Logisim ou Logisim-Evolution.
2. Importe o ficheiro do circuito: `P3/P3_V2.circ`.
3. Carregue o programa compilado na memória ROM de Instruções.
4. Ative os impulsos do relógio (clock) para depurar a execução de cada ciclo.
