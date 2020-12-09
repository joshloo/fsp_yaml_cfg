#Name
**FspGenCfgData.py** The python script that generates include file (**.INC**) file
for code compilation with UPD as input, and generates Pickle file (**.PKL**), include
file (**.INC**), Updateable Product Data, UPD binary (**.BIN**), Boot Settings File
(**.BSF**), Delta file (**.DLT**), Platform Description File (**.DSC**) and header
file (**.H**), all from an EDK II Platform Description (**DSC**) file.

#Synopsis
```
FspGenCfgData  GENINC  BinFile/DscFile[;DltFile]  IncOutFile   [-D Macros]
FspGenCfgData  GENPKL  DscFile                    PklOutFile   [-D Macros]
FspGenCfgData  GENBIN  DscFile[;DltFile]          BinOutFile   [-D Macros]
FspGenCfgData  GENBSF  DscFile[;DltFile]          BsfOutFile   [-D Macros]
FspGenCfgData  GENDLT  DscFile[;AbsfFile]         DltOutFile   [-D Macros]
FspGenCfgData  GENDSC  DscFile                    DscOutFile   [-D Macros]
FspGenCfgData  GENHDR  DscFile[;DltFile]          HdrOutFile[;ComHdrOutFile]   [-D Macros]
```

#Description
**FspGenCfgData.py** is a script that generates configuration options from an
**EDK II Platform Description (DSC)** file. These configuration options can
either be consumed by the FSP build process or runtime. Files like **UPD binary**
and **Delta file** can also be loaded into **Config Editor** that provides
a graphical user interface for manipulating settings in the regions.

The following sections explain the use cases.

## 1. FspGenCfgData  GENINC
The **GENINC** option takes the **UPD binary** or **DSC description file** as input and 
creates a include file describing the content of the configuration data blob.
This file generated has C syntax and can be included during compilation.

```
FspGenCfgData  GENINC  BinFile/DscFile[;DltFile]  IncOutFile  [-D Macros]
```

**BinFile** is be the location of the UPD binary file.

**DscFile** is be the location of the DSC description file.

**IncOutFile** is the location where the include binary will be stored.

## 2. FspGenCfgData  GENPKL
The **GENPKL** option takes the DSC file of a project and creates a Pickle file from the
content of the description file. It constructs the pickle object that contains the
configuration data so that it can be consumed by other Python scripts.

```
FspGenCfgData  GENPKL  DscFile  PklOutFile  [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**PklOutFile** is the location where the Pickle output file will be stored.

## 3. FspGenCfgData  GENBIN
The **GENBIN** option takes the DSC file of a project and creates a UPD binary file
describing the content of the configuration data.

```
FspGenCfgData  GENBIN  DscFile[;DltFile]  BinOutFile   [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**BinOutFile** is the location where the UPD binary output file will be stored.


## 4. FspGenCfgData  GENBSF
The **GENBSF** option takes the DSC file of a project and creates a boot settings
file describing the content of the configuration data.

```
FspGenCfgData  GENBSF  DscFile[;DltFile]  BsfOutFile   [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**BsfOutFile** is the location where the boot settings file will be stored.

## 5. FspGenCfgData  GENDLT
The **GENDLT** option takes the DSC file of a project and creates a delta file describing
the changes of configuration data.

```
FspGenCfgData  GENDLT  DscFile[;AbsfFile]  DltOutFile   [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**DltOutFile** is the location where the delta file will be stored.

## 6. FspGenCfgData  GENDSC
The **GENDSC** option creates a simplified version of DSC file describing the configuration
data from another complete DSC file of a project

```
FspGenCfgData  GENDSC  DscFile  DscOutFile   [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**DscOutFile** is the location where the simplified DSC description file will be stored.

## 7. FspGenCfgData  GENHDR
The **GENHDR** option takes the DSC description file with BSF syntax and creates a header file
describing the configuration data.

```
FspGenCfgData  GENHDR  DscFile[;DltFile]  HdrOutFile[;ComHdrOutFile]   [-D Macros]
```

**DscFile** is be the location of the DSC description file.

**HdrOutFile** is the location where the header file will be stored.
