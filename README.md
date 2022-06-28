# JLC PCB Plug-in for KiCad (Fabrication Toolkit)

## Features
1.	Generates gerber files in correct format for production
2.	Generates BOM file in correct format for production
3.	Generates Pick and Place file in correct format for assembly
4.	Generates IPC netlist file

## Installation

### Official Installation
Open the "Plugin and Content Manager" from the KiCad main menu an install the "Fabrication Toolkit" plugin from the selection list.

### Manual installation
Download the latest ZIP file from https://github.com/bennymeg/JLC-Plugin-for-KiCad. Open the "Plugin and Content Manager" from the KiCads main window and install the ZIP file via "Install from File".

## Options

### Include Component Part Number in Production Files
Add an 'MPN'* field with the LCSC component part number to the footprint component options.

#### Similar Fields*:
|'mpn' | 'Mpn' | 'MPN' | 'JLC_MPN' | 'LCSC_MPN' | 'LCSC Part #' | 'JLC' | 'LCSC'|
| --- | --- | --- | --- | --- | --- | --- | --- |

### Ignore Footprint in Production Files
Select 'Exclude from position files' or 'Exclude from BOM' in the footprint component options in order to ignore the footprint from the relevant file.

## Author

Benny Megidish
