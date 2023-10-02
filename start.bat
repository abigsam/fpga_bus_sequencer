@ECHO OFF
set vivado_path=C:\Xilinx\Vivado\2023.1
@REM set build_type="create_bd"
set board_name="microphase_lite_7010"
@REM set project_folder_name="vivado_bd"
set tool_name="vivado"
set menu_type="menu_main"

:BEGIN
CLS
ECHO.
ECHO #########################################################
ECHO # Build project for testing protocol sequncer project
ECHO # Author: abigsam@gmail.com
ECHO # Supported tools: Vivado 2023.1
ECHO #########################################################
rem Choose menu type
if %menu_type%=="menu_main" goto MAIN_MENU_START
if %menu_type%=="menu_board_amd" goto MAIN_BOARD_AMD_START

:MAIN_MENU_START
ECHO.
ECHO Avaliable options:
ECHO [1] Make project for AMD Vivado
ECHO [2] Cleanup Git repository
ECHO [3] Exit
ECHO [4] Test Python
ECHO.

rem CHOICE /C 123 /N /M "Enter your choice:"

CHOICE /C 1234 /N /M "Enter your choice:"
IF ERRORLEVEL 4 GOTO TEST_PYTHON
IF ERRORLEVEL 3 GOTO END
IF ERRORLEVEL 2 GOTO RUN_CLEANUP_PRJ
IF ERRORLEVEL 1 GOTO MAIN_MENU_AMD_START


:TEST_PYTHON
set pytho_path=.\ip_repo\bus_sequencer\python\parser_script.py
set asm_src=.\sequence_prog.txt
set python_out_dir=.\ip_repo\bus_sequencer\mem_files\
CALL :RUN_PYTHON %pytho_path% %asm_src% %python_out_dir%
pause
goto END

:MAIN_MENU_AMD_START
set menu_type="menu_board_amd"
set tool_name="vivado"
goto BEGIN

:MAIN_BOARD_AMD_START
ECHO.
ECHO Avaliable options:
ECHO [1] Microphase Lite 7010
ECHO [2] Return
ECHO [3] Exit
ECHO.

CHOICE /C 123 /N /M "Enter your choice:"
IF ERRORLEVEL 3 GOTO END
IF ERRORLEVEL 2 GOTO MAIN_MENU_AMD_START
IF ERRORLEVEL 1 GOTO MAIN_BOARD_AMD_MLITE_Z7010

:MAIN_BOARD_AMD_RETURN
set menu_type="menu_main"

:MAIN_BOARD_AMD_MLITE_Z7010
set board_name="mlite_7010"
goto RUN_VIVADO

:RUN_VIVADO
set project_folder_name=%tool_name:"=%_%board_name:"=%
ECHO Run Vivado Tcl build script for board %board_name%...
CALL :RUN_VIVADO_SCRIPT "%~dp0\scripts\vivado\build.tcl" %project_folder_name% %board_name%
CALL :OPEN_VIVADO_PROJECT %project_folder_name% %board_name%
goto RUN_CLEANUP


:RUN_CLEANUP_PRJ
ECHO Cleanup project folder...
rmdir /s /q "%~dp0\vivado_mlite_7010"
del "%~dp0\*.log"

:RUN_CLEANUP
ECHO Cleanup Vivado files...
del "%~dp0\*.jou"
del "%~dp0\*.dmp"
rmdir /s /q "%~dp0\.Xil"
goto END

:END
rem pause


rem ###########################################################
rem # Batch procedures
rem ###########################################################

:RUN_VIVADO_SCRIPT
    set vivado_bat_path=%vivado_path%\bin\vivado.bat
    if not exist %vivado_bat_path% (
        echo ERROR! Path %vivado_bat_path% did not found
        pause
        exit
    )
    if not exist %~1 (
        echo ERROR! Script file %~1 did not found
        pause
        exit
    )

    rem Cleanup old logs
    del "%~dp0\*.jou"
    del "%~dp0\*.log"

    call %vivado_bat_path% -mode batch -nojournal -notrace -source %~1 -tclargs %~2 %~3 %~4 %~5
EXIT /B 0


:OPEN_VIVADO_PROJECT
    if "%~2"=="" (
        set xpr_name=%~1.xpr
    ) else (
        set xpr_name=%~2.xpr
    )
    set prj_path=%~dp0\%~1\%xpr_name%
    set vivado_bat_path=%vivado_path%\bin\vivado.bat
    set vivado_vvgl_path=%vivado_path%\bin\unwrapped\win64.o\vvgl.exe
    if not exist %vivado_bat_path% (
        echo ERROR! Path %vivado_bat_path% did not found
        pause
        exit
    )
    if not exist %prj_path% (
        echo ERROR! Vivado project file %prj_path% did not found
        pause
        exit
    )
    pushd "%~dp0\%~1"
    call %vivado_vvgl_path% %vivado_bat_path% -project %prj_path%
    popd
EXIT /B 0


:RUN_PYTHON
    echo Check if Python is installed...
    python -V | find /v "Python" >NUL 2>NUL && (set python_exist=0)
    python -V | find "Python"    >NUL 2>NUL && (set python_exist=1)

    if %python_exist% EQU 0 (
        echo Python is not found int PATH.
        echo Please wisit https://www.python.org/downloads/windows/
        pause
        exit
    )

    if %python_exist% EQU 1 (
        @REM for /f "delims=" %%V in (`python -V`) do @set ver=%%V
        @REM echo Python version %ver% was found...
    )

    if not exist %~1 (
        echo ERROR! Script file %~1 did not found
        pause
        exit
    )

    if not exist %~2 (
        echo ERROR! Assembler source file %~1 did not found
        pause
        exit
    )

    if "%~3"=="" (
        echo ERROR! Specify output path
        pause
        exit
    )

    python %~1 %~2 %~3

EXIT /B 0