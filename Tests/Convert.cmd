@echo off

set WORK_DIR=%~dp0..
set FSP_DIR=%WORK_DIR%\IntelFsp
set OUT_DIR=%WORK_DIR%\Output
set BSF2YAML=%WORK_DIR%\Tools\FspBsf2Yaml.py
set SOC_NAME=%WORK_DIR%\Tools\ExtractName.py
set GEN_CFG=%WORK_DIR%\Tools\GenCfgData.py
set BSF_LIST=%FSP_DIR%\ApolloLakeFspBinPkg\FspBin\Fsp.bsf^
             %FSP_DIR%\CoffeeLakeFspBinPkg\Fsp.bsf

if not exist %OUT_DIR% (
  mkdir %OUT_DIR%
)

setlocal enabledelayedexpansion
for %%A in (%BSF_LIST%) do (
  for /f "delims=" %%B in ('python %SOC_NAME%  %%A') do @set FSP_NAME=%%B
  python %BSF2YAML% %%A   %OUT_DIR%\!FSP_NAME!.yaml
  if not "!ERRORLEVEL!" == "0" goto :EOF
  python %GEN_CFG% GENHDR %OUT_DIR%\!FSP_NAME!.yaml %OUT_DIR%\!FSP_NAME!.h
  if not "!ERRORLEVEL!" == "0" goto :EOF
)
endlocal

echo.



