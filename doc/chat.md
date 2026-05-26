O microprograma (firmware) implementa a ISA. Explique.

---

Vou te explicar essa parte de microprograma ligada à ISA com base no teu próprio código, então primeiro vou abrir os arquivos centrais da CPU para mapear o ciclo de microinstruções e depois te devolvo uma explicação passo a passo.

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/ufc2x.py)

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/computador.py)

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/montador.py)

Mapeei o núcleo: a ISA do montador gera opcodes (2,6,9,11,13,255) e o microprograma em ufc2x.py executa cada opcode por sequência de microinstruções. Vou abrir o relógio e a memória para te mostrar o fluxo completo fetch-decode-execute.

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/memoria.py)

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/clock.py)

Read [](file:///c%3A/Users/tiago.juca/Desktop/Tiago/ufc-aoc-ufc2x/src/disco.py)

Agora vou pegar os números de linha do arquivo da CPU para referenciar certinho onde cada campo da microinstrução é usado, e te explicar sem abstração.

Ran terminal command: $i=1; Get-Content .\src\ufc2x.py | ForEach-Object { '{0,4}: {1}' -f $i, $_; $i++ }

Ran terminal command: $i=1; Get-Content .\src\montador.py | ForEach-Object { '{0,4}: {1}' -f $i, $_; $i++ }

Você está exatamente na parte mais “travada” de arquitetura: a ISA é o nível visível, e o microprograma é o “como fazer” por baixo.

Resumo mental que destrava:
1. ISA diz o que cada instrução significa (add, sub, goto, jz, mov, halt).
2. Microprograma diz como executar isso em passos internos de registradores, ALU e memória.

No teu projeto, isso está assim:

1. ISA (opcodes)
- O montador mapeia instruções para opcodes em montador.py.
- Exemplo: add = 0x02, mov = 0x06, goto = 0x09, jz = 0x0B, sub = 0x0D, halt = 0xFF.

2. Microprograma (firmware)
- O firmware é um vetor de 512 microinstruções em ufc2x.py.
- Cada opcode da ISA aponta para um endereço de microcódigo:
- add (0x02) começa em ufc2x.py.
- mov (0x06) começa em ufc2x.py.
- goto (0x09) começa em ufc2x.py.
- jz (0x0B) começa em ufc2x.py.
- sub (0x0D) começa em ufc2x.py.
- halt (0xFF) em ufc2x.py.

3. Ciclo de execução da microarquitetura
- A cada tick, step busca uma microinstrução MIR = firmware[MPC] em ufc2x.py.
- Depois “quebra” essa palavra em campos e executa em ordem:
- leitura de registradores em ufc2x.py
- ALU em ufc2x.py
- escrita de registradores em ufc2x.py
- acesso à memória em ufc2x.py
- próximo endereço micro (MPC) em ufc2x.py

4. Formato da microinstrução (pela forma como step decodifica)
- bits 0..2: qual registrador vai para BUS_B (função read_regs)
- bits 3..5: sinais de memória (fetch byte, read word, write word)
- bits 6..11: quais registradores recebem BUS_C
- bits 12..19: controle da ALU e shift
- bits 20..22: JAM (desvio microcondicional / OR com MBR)
- bits 23..31: next address base

5. O pulo do gato: fetch e despacho por opcode
- A microinstrução 0 faz PC = PC + 1, busca byte em MBR e faz GOTO MBR em ufc2x.py.
- Isso significa: o opcode vira o endereço inicial do microprograma daquela instrução.

6. Exemplo completo: add x, label
- Opcode 0x02 cai no microendereço 2.
- 2: pega operando (próximo byte do programa) em MBR.
- 3: MAR = MBR; lê memória de palavra para MDR.
- 4: H = MDR.
- 5: X = H + X; volta para 0.
- Tudo isso está em ufc2x.py.

7. Por que labels de add/sub/mov viram endereço dividido por 4
- Em montador.py, add/sub/mov fazem //4.
- Motivo: esses usam read_word(MAR), então MAR é endereço de palavra.
- Já goto/jz pulam no fluxo de bytes (PC/MBR), então não dividem por 4 em montador.py.

Se quiser, no próximo passo eu pego uma instrução binária específica do teu firmware e te mostro bit a bit como ela vira sinais internos (tipo “dissecção de uma linha” de verdade).

---

pelo que entendo, só podemos ler 1 registrador, mas podemos escrever em todos ao mesmo tempo se quisermos, é isso mesmo? pq?

---

Sim, no teu modelo é isso mesmo, com um detalhe importante.

1. Leitura “selecionável”: só 1 registrador por vez no BUS_B.
- Em ufc2x.py, a função read_regs escolhe apenas uma fonte para BUS_B via campo de 3 bits.
- Esse campo é extraído em ufc2x.py.
- O outro operando da ALU (BUS_A) nem é selecionável: ele é sempre H em ufc2x.py.

2. Escrita “em paralelo”: pode escrever em vários registradores no mesmo ciclo.
- Em ufc2x.py, write_regs usa bits de habilitação (load enables).
- Se vários bits estiverem 1, o mesmo valor de BUS_C é latched em vários registradores ao mesmo tempo.
- Isso é chamado de broadcast no barramento de escrita (um BUS_C para vários destinos).

3. Por que essa assimetria (1 leitura, N escritas)?
- Custo/simplicidade: ler muitos registradores simultaneamente exigiria mais barramentos ou múltiplas portas de leitura.
- Projeto didático clássico: um mux de leitura (escolhe 1 fonte) + sinais de carga independentes na escrita.
- É eficiente para microcódigo: você calcula uma vez na ALU e replica o resultado para mais de um registrador quando útil.

4. Detalhe importante no teu código:
- “Todos” não é literalmente todos os registradores globais.
- write_regs só escreve em MAR, MDR, PC, X, Y e H (veja ufc2x.py).
- MBR não entra por write_regs; ele é carregado por memória em ufc2x.py.

Se quiser, eu te mostro uma microinstrução real tua e decodifico bit a bit para você ver exatamente quando ela lê 1 e escreve em vários.

---

ok, acho que entendi a ideia. cada programa da ISA termina voltando para o endereço 0 do firmware, o que repete o processo, mas sempre incrementando o PC para ler a proxima instrucao que consta na memoria, certo? o que acontece quando extrapola o PC? pois um computador fica rodando indefiidamente

---

Vou só confirmar os pontos de máscara de endereço na memória para te responder com precisão sobre overflow do PC e comportamento de loop.

Ran terminal command: $i=1; Get-Content .\src\memoria.py | ForEach-Object { '{0,4}: {1}' -f $i, $_; $i++ }

Está certinho o teu entendimento.

1. Fluxo normal
- Cada micro-rotina da ISA termina voltando para o microendereço 0, que é o ciclo de busca da próxima instrução em ufc2x.py.
- Nesse ciclo, o PC é incrementado, um byte é buscado para MBR, e o próximo microendereço vira o opcode (GOTO MBR), em ufc2x.py e ufc2x.py.

2. Quando o PC “extrapola”
- No teu simulador, acesso de byte mascara o endereço para 20 bits em memoria.py.
- Então o endereço efetivo vira módulo 2^20 (1 MB). Ou seja: passou do fim, dá wrap-around e volta ao início do espaço de memória.
- Para palavra, a máscara é 18 bits em memoria.py, coerente com 1 MB em words de 4 bytes.

3. O computador roda indefinidamente?
- Pode rodar indefinidamente se o programa formar laço (por exemplo com goto/jz), ou se entrar em região de memória sem halt.
- No teu caso, memória não escrita tende a ser 0, e opcode 0 cai de volta no microendereço 0 (fetch), então vira um loop de fetch contínuo.
- Ele só para quando step retorna falso, que ocorre quando a microinstrução lida é 0 em ufc2x.py. Isso acontece, por exemplo, se cair num opcode sem microcódigo implementado (firmware nessa posição = 0), ou se o programa executar halt (opcode 255 aponta para firmware[255] = 0) em ufc2x.py.
- O loop externo de clock segue chamando step até isso acontecer em clock.py.

Se quiser, eu te mostro um traço curto de execução (PC, MBR, MPC por tick) para você enxergar exatamente onde ele entra em loop.

---
