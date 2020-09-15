@echo off

set WORK_DIR=%~dp0..
set FSP_DIR=%WORK_DIR%\IntelFsp
set OUT_DIR=%WORK_DIR%\Output
set BSF2YAML=%WORK_DIR%\Tools\FspBsf2Yaml.py
set SOC_NAME=%WORK_DIR%\Tools\ExtractName.py
set GEN_CFG=%WORK_DIR%\Tools\GenCfgData.py
set BSF_FILE=%FSP_DIR%\CoffeeLakeFspBinPkg\Fsp.bsf
set FSP_NAME=Cfl
if not exist %OUT_DIR% (
  mkdir %OUT_DIR%
)

python %BSF2YAML% %BSF_FILE%  %OUT_DIR%\%FSP_NAME%.yaml
if not "%ERRORLEVEL%" == "0" goto :EOF

@echo  Generating Pickle file for loading speed
python %GEN_CFG% GENPKL %OUT_DIR%\%FSP_NAME%.yaml         %OUT_DIR%\%FSP_NAME%.pkl

@echo  Generating full yaml
python %GEN_CFG% GENYML %OUT_DIR%\%FSP_NAME%.yaml@CFLUPD_S %OUT_DIR%\%FSP_NAME%Full.yaml

@echo  Generating C header
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_T %OUT_DIR%\FsptUpd.h
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_M %OUT_DIR%\FspmUpd.h
python %GEN_CFG% GENHDR %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_S %OUT_DIR%\FspsUpd.h

@echo  Generating binary
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_T %OUT_DIR%\FsptUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_M %OUT_DIR%\FspmUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl@CFLUPD_S %OUT_DIR%\FspsUpd.bin
python %GEN_CFG% GENBIN %OUT_DIR%\%FSP_NAME%.pkl          %OUT_DIR%\FspUpd.bin

@echo  Generating delta
echo python %GEN_CFG% GENDLT %OUT_DIR%\%FSP_NAME%.pkl;%OUT_DIR%\FspUpd.bin  %OUT_DIR%\%FSP_NAME%.dlt -D FSP=1 -D FULL=1


echo.



