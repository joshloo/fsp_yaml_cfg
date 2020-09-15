FSP Configuration Tool
======================

FSP Configuration Tool is a set of open sourced tools to support FSP binary
configuration.

The intention is to migrate to use standard YAML format for FSP configuration.
The current FSP BSF format can only be supported by Intel BCT binary tool
(closed source). By moving to YAML format, it allows open sourced tools, such
as Slim Bootloader ConfigEditor, to be used for FSP configuration.  Moreover,
it allows more flexible extention for FSP UPD structure, such as defining bit
fields, nested strctures, etc.

The current tool supports the following features:
 - Convert FSP BSF file into YAML format
 - Convert FSP DSC file into YAML format
 - Configure FSP UPD option for FSP binary
 - Generate FSP UPD C header files
 - Generate FSP UPD default binary files
 - Patch FSP UPD binary
 - Generate FSP UPD delta





