import memoria
import sys
import clock
import ufc2x as cpu
import disco

disco.read(str(sys.argv[1]))

if len(sys.argv) > 2: 
    input1 = int(sys.argv[2]) & 0xFFFFFFFF;
    memoria.write_word(2, input1);
if len(sys.argv) == 4: 
    input2 = int(sys.argv[3]) & 0xFFFFFFFF;
    memoria.write_word(3, input2);
memoria.write_word(1, 0);

ticks = clock.start([cpu])
print(memoria.read_word(1),";",ticks)
