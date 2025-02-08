@echo off
set PATH=%PATH%;%NAND2TETRIS_IDE%\tools
set PROJECTS_PATH=%NAND2TETRIS_IDE%\projects

@REM Project 7
set PROJECT_DIR=%PROJECTS_PATH%\7\MemoryAccess\BasicTest
set VM_PATH=%PROJECT_DIR%\BasicTest.vm
set TST_NAME=BasicTest.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

set PROJECT_DIR=%PROJECTS_PATH%\7\MemoryAccess\PointerTest
set VM_PATH=%PROJECT_DIR%\PointerTest.vm
set TST_NAME=PointerTest.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

set PROJECT_DIR=%PROJECTS_PATH%\7\MemoryAccess\StaticTest
set VM_PATH=%PROJECT_DIR%\StaticTest.vm
set TST_NAME=StaticTest.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

set PROJECT_DIR=%PROJECTS_PATH%\7\StackArithmetic\SimpleAdd
set VM_PATH=%PROJECT_DIR%\SimpleAdd.vm
set TST_NAME=SimpleAdd.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

set PROJECT_DIR=%PROJECTS_PATH%\7\StackArithmetic\StackTest
set VM_PATH=%PROJECT_DIR%\StackTest.vm
set TST_NAME=StackTest.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

@REM Project 8
set PROJECT_DIR=%PROJECTS_PATH%\8\ProgramFlow\BasicLoop
set VM_PATH=%PROJECT_DIR%\BasicLoop.vm
set TST_NAME=BasicLoop.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

set PROJECT_DIR=%PROJECTS_PATH%\8\ProgramFlow\FibonacciSeries
set VM_PATH=%PROJECT_DIR%\FibonacciSeries.vm
set TST_NAME=FibonacciSeries.tst
call :VMTranslatorTest %VM_PATH% %PROJECT_DIR% %TST_NAME%

exit /b

:VMTranslatorTest
echo ==================================================================
echo Running VM Translator:'%1'...
pushd src\VMTranslator
python VMTranslator.py %1
popd
echo Testing on CPU Emulator: '%2\%3'...
pushd %2
call CPUEmulator %3
popd
echo ==================================================================
exit /b
