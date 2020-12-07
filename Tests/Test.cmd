@echo off

set WORK_DIR=%~dp0..
set FSP_DIR=%WORK_DIR%\IntelFsp
set FSPSDK_DIR=%WORK_DIR%\fspsdk
set OUT_DIR=%WORK_DIR%\Output
set BSF2YAML=%WORK_DIR%\Tools\FspDscBsf2Yaml.py
set GEN_CFG=%WORK_DIR%\Tools\GenCfgData.py

set FSP_NAME=Apl
set FSPSDK_NAME=Qemu

if not exist %OUT_DIR% (
  mkdir %OUT_DIR%
)

if "%FSP_NAME%" == "Cfl" (
    set BSF_FILE=%FSP_DIR%\CoffeeLakeFspBinPkg\Fsp.bsf
    set UPD_KEY=CFL
)
if "%FSP_NAME%" == "Apl" (
    set BSF_FILE=%FSP_DIR%\ApolloLakeFspBinPkg\FspBin\Fsp.bsf
    set UPD_KEY=APL
)

set DSC_FILE=%FSPSDK_DIR%\QemuFspPkg\QemuFspPkg.dsc

@echo  Generating BSF YAML
python %BSF2YAML% %BSF_FILE%  %OUT_DIR%\%FSP_NAME%.yaml
if not "%ERRORLEVEL%" == "0" goto :EOF

@echo  Generating DSC YAML
python %BSF2YAML% %DSC_FILE%  %OUT_DIR%\%FSPSDK_NAME%.yaml
if not "%ERRORLEVEL%" == "0" goto :EOF

@echo  Generating Pickle file for loading speed
python %GEN_CFG% GENPKL %OUT_DIR%\%FSP_NAME%.yaml         %OUT_DIR%\%FSP_NAME%.pkl

@echo  Generating full yaml
python %GEN_CFG% GENYML %OUT_DIR%\%FSP_NAME%.yaml@%UPD_KEY%UPD_S %OUT_DIR%\%FSP_NAME%Full.yaml

@echo  Generating C header
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_T %OUT_DIR%\FsptUpd.h
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_M %OUT_DIR%\FspmUpd.h
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_S %OUT_DIR%\FspsUpd.h

@echo  Generating binary
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_T %OUT_DIR%\FsptUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_M %OUT_DIR%\FspmUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@%UPD_KEY%UPD_S %OUT_DIR%\FspsUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl                %OUT_DIR%\FspUpd.bin

@echo  Generating delta
python %GEN_CFG% GENDLT %OUT_DIR%\%FSP_NAME%.pkl;%OUT_DIR%\FspUpd.bin  %OUT_DIR%\%FSP_NAME%.dlt -D FULL=1


echo.



