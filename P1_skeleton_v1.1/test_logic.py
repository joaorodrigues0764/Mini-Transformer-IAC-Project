import sys

# Constantes para simular os limites de inteiros de 32 bits com sinal em RISC-V
INT32_MIN = -2147483648
INT32_MAX = 2147483647

def argmax_oracle(arr):
    """
    Retorna (status, index).
    Status: 0 (Sucesso), 50 (Tamanho < 1)
    Em caso de empate, devolve o menor índice.
    """
    if len(arr) < 1:
        return 50, -1
    
    max_val = arr[0]
    max_idx = 0
    for i in range(1, len(arr)):
        # Condição estritamente maior (>) para preservar o menor índice em caso de empate
        if arr[i] > max_val:
            max_val = arr[i]
            max_idx = i
            
    return 0, max_idx

def select_oracle(arr, idx):
    """
    Retorna (status, valor).
    Status: 0 (Sucesso), 50 (Tamanho < 1), 100 (Index out of bounds)
    """
    if len(arr) < 1:
        return 50, -1
        
    if idx >= len(arr) or idx < 0:
        return 100, -1
        
    return 0, arr[idx]

def dot_oracle(arr1, arr2):
    """
    Retorna (status, valor).
    Status: 0 (Sucesso), 50 (Tamanho < 1), 200 (Overflow)
    """
    if len(arr1) < 1 or len(arr2) < 1 or len(arr1) != len(arr2):
        return 50, -1
    
    acc = 0
    for a, b in zip(arr1, arr2):
        # 1. Verificar Overflow na Multiplicação
        prod = a * b
        if prod < INT32_MIN or prod > INT32_MAX:
            return 200, -1
        
        # 2. Verificar Overflow na Adição (Acumulação)
        acc += prod
        if acc < INT32_MIN or acc > INT32_MAX:
            return 200, -1
            
    return 0, acc

class TestRunner:
    def __init__(self):
        self.passed = 0
        self.failed = 0

    def assert_eq(self, test_name, expected, got):
        if expected == got:
            print(f"✅ PASSED: {test_name}")
            self.passed += 1
        else:
            print(f"❌ FAILED: {test_name}")
            print(f"    Esperado (Status, Res): {expected}")
            print(f"    Obtido (Status, Res):   {got}")
            self.failed += 1

def run_tests():
    runner = TestRunner()
    
    print("="*40)
    print("      TESTES ARGMAX")
    print("="*40)
    runner.assert_eq("Lista normal", (0, 2), argmax_oracle([1, 2, 5, 4]))
    runner.assert_eq("Lista com empates", (0, 1), argmax_oracle([1, 5, 5, 4]))
    runner.assert_eq("Tudo negativo", (0, 0), argmax_oracle([-1, -2, -5, -4]))
    runner.assert_eq("Erro: Tamanho < 1", (50, -1), argmax_oracle([]))

    print("\n" + "="*40)
    print("      TESTES SELECT")
    print("="*40)
    runner.assert_eq("Acesso normal", (0, 6), select_oracle([-6, -1, 6, 1], 2))
    runner.assert_eq("Erro: Tamanho < 1", (50, -1), select_oracle([], 0))
    runner.assert_eq("Erro: Index = Tamanho", (100, -1), select_oracle([1, 2, 3], 3))
    runner.assert_eq("Erro: Index > Tamanho", (100, -1), select_oracle([1, 2], 5))
    runner.assert_eq("Erro: Index < 0", (100, -1), select_oracle([1, 2, 3], -1))

    print("\n" + "="*40)
    print("      TESTES DOT (Produto Escalar)")
    print("="*40)
    runner.assert_eq("Produto Escalar Normal", (0, 32), dot_oracle([1, 2, 3], [4, 5, 6]))
    runner.assert_eq("Valores negativos normais", (0, -32), dot_oracle([-1, -2, -3], [4, 5, 6]))
    runner.assert_eq("Erro: Tamanho < 1", (50, -1), dot_oracle([], []))
    
    # OVERFLOW - Multiplicação
    # 50000 * 50000 = 2500000000 (> 2147483647)
    runner.assert_eq("Erro 200: Overflow Mult Positiva", (200, -1), dot_oracle([50000], [50000]))
    
    # 50000 * -50000 = -2500000000 (< -2147483648)
    runner.assert_eq("Erro 200: Overflow Mult Negativa", (200, -1), dot_oracle([50000], [-50000]))
    
    # Edge Case: INT32_MIN * -1 -> Resulta em +2147483648 (maior que o max)
    runner.assert_eq("Erro 200: Overflow INT32_MIN * -1", (200, -1), dot_oracle([INT32_MIN], [-1]))

    # OVERFLOW - Adição
    # Max + 1
    runner.assert_eq("Erro 200: Overflow Soma Positiva", (200, -1), dot_oracle([INT32_MAX, 1], [1, 1]))
    
    # Min - 1
    runner.assert_eq("Erro 200: Overflow Soma Negativa", (200, -1), dot_oracle([INT32_MIN, -1], [1, 1]))
    
    print("\n" + "="*40)
    print(f"Resumo: {runner.passed} passaram, {runner.failed} falharam.")
    print("="*40)
    
    if runner.failed > 0:
        sys.exit(1)

if __name__ == '__main__':
    run_tests()
