@echo off
setlocal
pushd "%~dp0"
cmd /c "python .\src\montador.py .\test\prog2.asm out.bin && python -u .\src\computador.py out.bin"
popd
endlocal
