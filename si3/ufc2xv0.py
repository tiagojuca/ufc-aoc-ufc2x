import memory
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

firmware[0] = 0b00000000010000000000000000001000 #MBR = memory.read_byte(0); MPC = MBR.

#PROGRAMA DE CONTAGEM PROGRESSIVA 0-((2^32)-1) = CPR
firmware[2] = 0b00000001100000110001010001100000 
              # BUS_C = 1; H = MDR = BUS_C; memory.write_word(0, MDR); Vai para instrução 1.
firmware[3] = 0b00000001100000111001010001100000
              # BUS_C = H + 1; H = MDR = BUS_C; memory.write_word(0, MDR); Vai para instrução 1.

#PROGRAMA DE CONTAGEM REGRESSIVA 256-0 = CRG
firmware[5] = 0b00000011000011110001010001100000
              # BUS_C = 256; H = MDR = BUS_C; memory.write_word(0, MDR); Vai para instrução 1.
firmware[6] = 0b00000011000100110110010001100000
              # BUS_C = MDR - 1; H = MDR = BUS_C; memory.write_word(0, MDR); Vai para instrução 1 se ALU != 0 ou instrução 262 se ALU == 0.


def read_regs(reg_num):
    global MDR, PC, MBR, X, Y, H, BUS_A, BUS_B
    
    BUS_A = H
    
    if reg_num == 0:
       BUS_B = MDR
    elif reg_num == 1:
       BUS_B = PC
    elif reg_num == 2:
       BUS_B = MBR
    elif reg_num == 3:
       BUS_B = X
    elif reg_num == 4:
       BUS_B = Y
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

def memory_io(mem_bits):
    global PC, MAR, MDR, MBR
    
    if mem_bits & 0b001:
       MBR = memory.read_byte(PC)
    if mem_bits & 0b010:
       MDR = memory.read_word(MAR)
    if mem_bits & 0b100:
       memory.write_word(MAR, MDR)

def step():
   global MIR, MPC
   
   MIR = firmware[MPC]
   
   if MIR == 0:
      return False
   
   read_regs( MIR & 0b00000000000000000000000000000111 )
   alu((MIR & 0b00000000000011111111000000000000) >> 12)
   write_regs( (MIR & 0b00000000000000000000111111000000) >> 6)
   memory_io( (MIR & 0b00000000000000000000000000111000) >> 3 )
   next_instruction(MIR >> 23, (MIR & 0b00000000011100000000000000000000) >> 20)
   
   print(memory.read_word(0))
   
   return True
   