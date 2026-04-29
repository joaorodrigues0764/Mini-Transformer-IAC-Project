# You can change these values to test your solution.
.data
A:    .word 6, 1, 3, 9, 12, 4, 13, 153
B:    .word 6, 1, 3, 9, 12, 4, 13, 153
SIZE: .word 8

.text
main:
  la a1, A                        # a1 = pointer to array A
  la a2, B                        # a2 = pointer to array B
  lw a3, SIZE                     # a3 = number of elements in each array
  jal ra, dot                     # call dot function
exit:
  li a7, 10                       # exit syscall code
  ecall                           # terminate the program


# ==========================================================================
# FUNCTION: dot
#   This function computes the dot product of two integer arrays.
# Arguments:
#   a1 = pointer to first array
#   a2 = pointer to second array
#   a3 = array length
# Returns:
#   a0 = status code  li t1, 0                        
#   a1 = dot product result
# ===========================================================================
dot:
  # TODO: Implement the dot product function here
  li t2, 0                        # accumulator 
  li t3, 1                        # minimum vector size
  blt a3, t3, argInv              # invalid lenght
  j loop_start
  
loop_start:
  lw a4, 0(a1)                    # current value first vector
  lw a5, 0(a2)                    # current value second vector
  bge t1, a3, loop_end            # if the index overtakes, the size ends
    
  mv t4, a4                       # store temporaly the value 1 to evaluate its signal
  mv t5, a5                       # store temporaly the value 2 to evaluate its signal
  srli t4, t4, 31                 # shifts the 31 bit to the first
  srli t5, t5, 31                 # shifts the 31 bit to the first
  xor t6, t4, t5                  # if the bit is equal (therefore the sign) the result is 0, otherwise is 1
  bne t6, x0, negative_mul        # if the bits are different, the result will be negative
  mulh t4, a4, a5                 # upper 32 bits of the inner product
  bne t4, x0, overflow            # there is overflow
  j inner_product                 # loop continues
    
negative_mul:
  mulh t4, a4, a5                 # upper 32 bits of the inner product
  addi t3, t3, -2                   # the expected value is -1
  bne t4, t3, overflow            # there is overflow
  j inner_product                 # loop continues

inner_product:
  mul t4, a4, a5                  # inner product of each element of each vector
  
  mv t3, t4                       # store temporaly the new value to evaluate its signal
  mv t5, t2                       # store temporaly the current inner product to evaluate its signal
  srli t3, t3, 31                 # shifts the 31 bit to the first
  srli t5, t5, 31                 # shifts the 31 bit to the first
  xor t6, t3, t5                  # if the bit is equal (therefore the sign) the result is 0, otherwise is 1
  beq t6, x0, possible_overflow   # if the signs are equal, it may be overflow, otherwize it is impossible
  j finalize_inner_product

finalize_inner_product:
  add t2, t2, t4                  # adds the inner product to the accumulator
  addi t1, t1, 1                  # next index

  addi a1, a1, 4                  # next element
  addi a2, a2, 4                  # next element
  j loop_start                    # loop continues

possible_overflow:
  mv t3, t2
  add t3, t3, t4                  # adds the inner product to the accumulator
  srli t2, t2, 31                 # shifts the 31 bit to the first
  xor t6, t3, t5                  # if the bit is equal (therefore the sign) the result is 0, otherwise is 1
  bne t6, x0, overflow            # if the signs are different there is overflow
  j finalize_inner_product

overflow:
  li a0, 200                      # status code is updated to 200 (OverFlow)
  j dot_end                       # jump to the end

argInv:
  li a0, 50                       # invalid size
  j dot_end                       # jump to the end

loop_end:
  li a0, 0                        # success
  mv a1, t2                       # final dot product 

dot_end:
  jr ra                           # return to the caller