#Name
**FspDscBsf2Yaml.py** The python script that generates YAML file for
the Boot Settings from an EDK II Platform Description (**DSC**) file
or from a Boot Settings File (**BSF**).

#Synopsis
```
FspDscBsf2Yaml DscFile|BsfFile  YamlFile
```

#Description
**FspDscBsf2Yaml.py** is a script that generates configuration options from an
**EDK II Platform Description (DSC)** file. It generates a **YAML file**
that can be used by the **Config Editor** to provide a graphical user interface
for manipulating settings in the UPD regions.

Below is an example of how a YAML file looks like

![YAML example](https://slimbootloader.github.io/_images/ConfigDefYaml.PNG)

The following sections explain the use case.

## 1. FspDscBsf2Yaml.py DscFile YamlFile
The **DscFile** option generates a YAML from the UPD entries in a package's DSC
file. It does this by parsing the DSC file and match the keywords for the data.

The command signature for **DscFile** is

```FspDscBsf2Yaml DscFile YamlFile```

In this case, the **YamlFile** parameter is required; it should be the
relative path to where the YAML should be stored.

Every BSF command in the DSC file begins with **!BSF** or **@Bsf**. The
following table summarizes the options that come after **!BSF** or **@Bsf**:

# BSF Commands Description
###PAGES
**PAGES** maps abbreviations to friendly-text descriptions of the pages in a BSF.

#####Example:
```!BSF PAGES:{PG1:?Page 1?, PG2:?Page 2?}``` or

```@Bsf PAGES:{PG1:?Page 1?, PG2:?Page 2?}```

###PAGE
This marks the beginning of a page. Use the abbreviation specified in **PAGES**
command.

#####Example:
```!BSF PAGE:{PG1}``` or

```@Bsf PAGE:{PG1}```

All the entries that come after this command are assumed to be on that page,
until the next **PAGE** command

The **PAGES** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF PAGES:{VAL:"FSP Validation Settings", MEM:"FSP MemoryInit Settings", SIL:"FSP SiliconInit Settings"```

Output:

```page         : VAL::"FSP Validation Settings", MEM::"FSP MemoryInit Settings", SIL::"FSP SiliconInit Settings"```

###FIND
FIND maps to the BSF **Find** command. It will be placed in the **StructDef**
region of the BSF and should come at the beginning of the UPD sections of the
DSC, immediately before the signatures that mark the beginning of these
sections. The content should be the plain-text equivalent of the signature. The
signature is usually 8 characters.

#####Example:
```!BSF FIND:{PROJSIG1}``` or

```@Bsf FIND:{PROJSIG1}```


The **FIND** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF FIND:{QEMUPD_T}```

Output:

```find         : QEMUPD_T```

###BLOCK
The BLOCK command maps to the **BeginInfoBlock** section of the BSF. There are
two elements: a version number and a plain-text description.

#####Example:
```!BSF BLOCK:{NAME:"My platform name", VER:"0.1"}``` or

```@Bsf BLOCK:{NAME:"My platform name", VER:"0.1"}```

The **BLOCK** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF BLOCK:{NAME:"QEMU Platform", VER:"0.1"}```

Output:

```PLATFORM_VERSION               : 0.1```

###NAME
**NAME** gives a plain-text for a variable. This is the text label that will
appear next to the control in **BCT**.

#####Example:
```!BSF NAME:{Variable 0}``` or

```@Bsf NAME:{Variable 0}```

If the **!BSF NAME**  or **@Bsf NAME** command does not appear before an entry
in the UPD region of the DSC file, then that entry will not appear in the BSF.

The **NAME** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF NAME:{FsptUpdRevision}```

Output:

```name         : FsptUpdRevision```

###TYPE
The **TYPE** command is used either by itself or with the **NAME** command. It
is usually used by itself when defining an **EditNum** field for the BSF. You
specify the type of data in the second parameter and the range of valid values
in the third.

#####Example:
```!BSF TYPE:{EditNum, HEX, (0x00,0xFF)}``` or

```@Bsf TYPE:{EditNum, HEX, (0x00,0xFF)}```

**TYPE** appears on the same line as the **NAME** command when using a combo-box.

#####Example:
```!BSF NAME:{Variable 1} TYPE:{Combo}``` or
```@Bsf NAME:{Variable 1} TYPE:{Combo}```

There is a special **None** type that puts the variable in the **StructDef**
region of the BSF, but doesn't put it in any **Page** section. This makes the
variable visible to BCT, but not to the end user.

The **TYPE** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF TYPE:{EditNum, HEX, (0x00000000,0xFFFFFFFF)}```

Output:

```type         : EditNum, HEX, (0x00000000,0xFFFFFFFF)```

###HELP
The **HELP** command defines what will appear in the help text for each control
in BCT.

#####Example:
```!BSF HELP:{Enable/disable LAN controller.}``` or

```@Bsf HELP:{Enable/disable LAN controller.}```

The **HELP** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF HELP:{Stack base for FSP use. Default: 0xFEF16000}```

Output:

```help         : >   Stack base for FSP use. Default- 0xFEF16000```

###OPTION
The **OPTION** command allows you to custom-define combo boxes and map integer
or hex values to friendly-text options.

#####Example:
```!BSF OPTION:{0:IDE, 1:AHCI, 2:RAID}```

```!BSF OPTION:{0x00:0 MB, 0x01:32 MB, 0x02:64 MB}```

or

```@Bsf OPTION:{0:IDE, 1:AHCI, 2:RAID}```

```@Bsf OPTION:{0x00:0 MB, 0x01:32 MB, 0x02:64 MB}```

The **OPTION** output in **YAML** format looks like this with QEMU FSP example

Input:

```!BSF OPTION:{0:NONE, 1:I/O, 2:MMIO}```

Output:

```option       : 0:NONE, 1:I/O, 2:MMIO```

###FIELD
The **FIELD** command can be used to define a section of a consolidated PCD
such that the PCD will be displayed in several fields via BCT interface instead
of one long entry.

#####Example:
```!BSF FIELD:{PcdDRAMSpeed:1}``` or

```@Bsf FIELD:{PcdDRAMSpeed:1}```

###ORDER
The **ORDER** command can be used to adjust the display order for the BSF items.
By default the order value for a BSF item is assigned to be the UPD item
```(Offset * 256)```. It can be overridden by declaring **ORDER** command using
format ORDER: ```{HexMajor.HexMinor}```. In this case the order value will be
```(HexMajor*256+HexMinor)```. The item order value will be used as the sort key
during the BSF item display.

#####Example:
```!BSF ORDER:{0x0040.01}``` or

```@Bsf ORDER:{0x0040.01}```

For **OPTION** and **HELP** commands, it allows to split the contents into
multiple lines by adding multiple **OPTION** and **HELP** command lines. The
lines except for the very first line need to start with **+** in the content to
tell the tool to append this string to the previous one.

For example, the statement

```!BSF OPTION:{0x00:0 MB, 0x01:32 MB, 0x02:64 MB}```

is equivalent to:

```!BSF OPTION:{0x00:0 MB, 0x01:32 MB,}```

```!BSF OPTION:{+ 0x02:64 MB}```

or

```@Bsf OPTION:{0x00:0 MB, 0x01:32 MB, 0x02:64 MB}```

is equivalent to:

```@Bsf OPTION:{0x00:0 MB, 0x01:32 MB,}```

```@Bsf OPTION:{+ 0x02:64 MB}```

The **NAME**, **OPTION**, **TYPE**, and **HELP** commands can all appear on the
same line following the **!BSF** or **@Bsf** keyword or they may appear on
separate lines to improve readability.

There are four alternative ways to replace current BSF commands.
### 1. ```# @Prompt```
An alternative way replacing **NAME** gives a plain-text for a
variable. This is the text label that will appear next to the control in BCT.

#####Example:
```# @Prompt Variable 0```

The above example can replace the two methods as below.

```!BSF NAME:{Variable 0}``` or

```@Bsf NAME:{Variable 0}```

If the ```# @Prompt``` command does not appear before an entry in the UPD region
of the DSC file, then that entry will not appear in the BSF.

### 2. ```##```
An alternative way replacing **HELP** command defines what will appear in the
help text for each control in BCT.

#####Example:
```## Enable/disable LAN controller.```

The above example can replace the two methods as below.

```!BSF HELP:{Enable/disable LAN controller.}``` or

```@Bsf HELP:{Enable/disable LAN controller.}```

### 3. ```# @ValidList```
An alternative way replacing **OPTION** command allows you to custom-define
combo boxes and map integer or hex values to friendly-text options.

#####Example:
``` # @ValidList 0x80000003 | 0, 1, 2 | IDE, AHCI, RAID
                   Error Code | Options | Descriptions
```

The above example can replace the two methods as below.

```!BSF OPTION:{0:IDE, 1:AHCI, 2:RAID}``` or

```@Bsf OPTION:{0:IDE, 1:AHCI, 2:RAID}```

### 4. ```# @ValidRange```
An alternative way replace **EditNum** field for the BSF.

#####Example:
```# @ValidRange 0x80000001 | 0x0 ? 0xFF
                    Error Code | Range
```

The above example can replace the two methods as below.

```!BSF TYPE:{EditNum, HEX, (0x00,0xFF)}``` or

```@Bsf TYPE:{EditNum, HEX, (0x00,0xFF)}```



## 2. FspDscBsf2Yaml.py BsfFile YamlFile

WIP

