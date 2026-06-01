@echo off
python .\src\montador.py .\test\prog2.asm out.bin
python .\src\computador.py out.bin
