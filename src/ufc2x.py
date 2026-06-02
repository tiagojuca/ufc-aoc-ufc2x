import memoria
from array import array

MPC = 0
MIR = 0

MAR = 0
MDR = 0
PC = 0
MBR = 0
X = 0
Y = 0
H = 0

N = 0
Z = 1

BUS_A = 0
BUS_B = 0
BUS_C = 0

firmware = array('L',[0]) * 512

#MICROPROGRAMA:

#0: INIT
firmware[0] = 0b000000000_100_00110101_001000_001_101_001 #BUS_C = PC + 1; PC = BUS_C; MBR = memoria.read_byte(PC) (FETCH); GOTO MBR.
              
#2: X = X + mem[address]
firmware[2] = 0b000000011_000_00110101_001000_001_101_001 #PC = PC + 1; MBR = memoria.read_byte(PC); GOTO 3
firmware[3] = 0b000000100_000_00010100_100000_010_101_010 #MAR = MBR; MDR = memoria.read_word(MAR); GOTO 4
firmware[4] = 0b000000101_000_00010100_000001_000_101_000 #H = MDR; GOTO 5
firmware[5] = 0b000000000_000_00111100_000100_000_101_011 #X = H + X; GOTO 0

#6: memoria[address] = X
firmware[6] = 0b000000111_000_00110101_001000_001_101_001 #PC = PC + 1; FETCH; GOTO 7
firmware[7] = 0b000001000_000_00010100_100000_000_101_010 #MAR = MBR; GOTO 8
firmware[8] = 0b000000000_000_00010100_010000_100_101_011 #MDR = X; WRITE_WORD; GOTO 0
              
#9: GOTO address
firmware[9]  = 0b000001010_000_00110101_001000_001_101_001 #PC = PC + 1; FETCH; GOTO 10
firmware[10] = 0b000000000_100_00010100_001000_001_101_010 #PC = MBR; FETCH; GOTO MBR

#11: IF X == 0 GOTO address
firmware[11] =  0b000001100_001_00010100_000000_000_101_011 #BUS_C = X; IF ALU == 0 GOTO 268 ELSE GOTO 12
firmware[12] =  0b000000000_000_00110101_001000_000_101_001 #PC = PC + 1; GOTO 0
firmware[268] = 0b000001001_000_00000000_000000_000_101_000 #GOTO 9

#13: X = X - mem[address]
firmware[13] = 0b000001110_000_00110101_001000_001_101_001 #PC <- PC + 1; fetch; goto 14
firmware[14] = 0b000001111_000_00010100_100000_010_101_010 #MAR <- MBR; read; goto 15
firmware[15] = 0b000010000_000_00010100_000001_000_101_000 #H <- MDR; goto 16
firmware[16] = 0b000000000_000_00111111_000100_000_101_011 #X <- X - H; goto 0

#255: HALT
firmware[255] = 0b000000000_000_00000000_000000_000_000_000


#1:  SOMA A X O VALOR NO END. 215
#3:  IF X = 0 GOTO 20
#5:  GRAVE O VALOR DO REG. X NO END. 220
#7:  HALT
#20: SOMA A X O VALOR NO END. 200
#22: GOTO 5
# memory.write_byte(1, 2) #SOMA A X
# memory.write_byte(2, 215) #O VALOR NO END. 215
# memory.write_byte(3, 11) #IF X = 0 GOTO
# memory.write_byte(4, 20) #20
# memory.write_byte(5, 6) #GRAVE O VALOR DO REG. X
# memory.write_byte(6, 220) #NO END. 220
# memory.write_byte(7, 255) #HALT
# memory.write_byte(20, 2) #SOMA A X
# memory.write_byte(21, 200) #O VALOR NO END. 200
# memory.write_byte(22, 9) #GOTO
# memory.write_byte(23, 5) #5


def read_regs(reg_num_a, reg_num_b):
    global MDR, PC, MBR, X, Y, H, BUS_A, BUS_B
    
    if reg_num_a == 0:
       BUS_A = MDR
    elif reg_num_a == 1:
       BUS_A = PC
    elif reg_num_a == 2:
       BUS_A = MBR
    elif reg_num_a == 3:
       BUS_A = X
    elif reg_num_a == 4:
       BUS_A = Y
    elif reg_num_a == 5:
       BUS_A = H
    else:
       BUS_A = 0
    
    if reg_num_b == 0:
       BUS_B = MDR
    elif reg_num_b == 1:
       BUS_B = PC
    elif reg_num_b == 2:
       BUS_B = MBR
    elif reg_num_b == 3:
       BUS_B = X
    elif reg_num_b == 4:
       BUS_B = Y
    elif reg_num_b == 5:
       BUS_B = H
    else:
       BUS_B = 0

def write_regs(reg_bits):
    global MAR, MDR, PC, X, Y, H, BUS_C
    
    if reg_bits & 0b100000:
       MAR = BUS_C
    if reg_bits & 0b010000:
       MDR = BUS_C
    if reg_bits & 0b001000:
       PC = BUS_C
    if reg_bits & 0b000100:
       X = BUS_C
    if reg_bits & 0b000010:
       Y = BUS_C
    if reg_bits & 0b000001:
       H = BUS_C

def alu(control_bits):
    global N, Z, BUS_A, BUS_B, BUS_C
    
    a = BUS_A
    b = BUS_B
    o = 0
    
    shift_bits = control_bits & 0b11000000
    shift_bits = shift_bits >> 6

    control_bits = control_bits & 0b00111111
    
    if control_bits == 0b011000:
       o = a
    elif control_bits == 0b010100:
       o = b
    elif control_bits == 0b011010:
       o = ~a
    elif control_bits == 0b101100:
       o = ~b
    elif control_bits == 0b111100:
       o = a + b
    elif control_bits == 0b111101:
       o = a + b + 1
    elif control_bits == 0b111001:
       o = a + 1
    elif control_bits == 0b110101:
       o = b + 1
    elif control_bits == 0b111111:
       o = b - a
    elif control_bits == 0b110110:
       o = b - 1
    elif control_bits == 0b111011:
       o = -a
    elif control_bits == 0b001100:
       o = a & b
    elif control_bits == 0b011100:
       o = a | b
    elif control_bits == 0b010000:
       o = 0
    elif control_bits == 0b110001:
       o = 1
    elif control_bits == 0b110010:
       o = -1
   
    if o == 0:
       N = 0
       Z = 1
    else:
       N = 1
       Z = 0
    
    if shift_bits == 0b01:
       o = o << 1
    elif shift_bits == 0b10:
       o = o >> 1
    elif shift_bits == 0b11:
       o = o << 8

    BUS_C = o
    
def next_instruction(nextadd, jam):
    global MPC
    
    if jam == 0b000:
        MPC = nextadd
        return
        
    if jam & 0b001:
        nextadd = nextadd | (Z << 8)
        
    if jam & 0b010:
        nextadd = nextadd | (N << 8)
        
    if jam & 0b100:
        nextadd = nextadd | MBR
        
    MPC = nextadd

def memoria_io(mem_bits):
    global PC, MAR, MDR, MBR
    
    if mem_bits & 0b001:
       MBR = memoria.read_byte(PC)
    if mem_bits & 0b010:
       MDR = memoria.read_word(MAR)
    if mem_bits & 0b100:
       memoria.write_word(MAR, MDR)

def step():
   global MIR, MPC
   
   MIR = firmware[MPC]
   
   if MIR == 0:
      return False
   
   read_regs( (MIR & 0b000000000_000_00000000_000000_000_111_000) >> 3, MIR & 0b000000000_000_00000000_000000_000_000_111 )
   alu((MIR & 0b000000000_000_11111111_000000_000_000_000) >> 15)
   write_regs( (MIR & 0b000000000_000_00000000_111111_000_000_000) >> 9)
   memoria_io( (MIR & 0b000000000_000_00000000_000000_111_000_000) >> 6 )
   next_instruction(MIR >> 26, (MIR & 0b000000000_111_00000000_000000_000_000_000) >> 23)
   
   return True
