<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/logo.svg?raw=true" 
    style="display:block margin-left: auto; margin-right: auto;" alt="JLC PCB Plug-in for KiCad">
    
<div align="center">

| **JLC PCB Plug-in for KiCad** |
|:-----:|

[![Sponsor](https://img.shields.io/static/v1?label=Sponsor&message=%E2%9D%A4&logo=GitHub&color=%23fe8e86)](https://github.com/sponsors/bennymeg)

</div>

## Features
1.	Generates gerber files in correct format for production
2.	Generates BOM file in correct format for production
3.	Generates Pick and Place file in correct format for assembly
4.	Generates IPC netlist file

## Installation

### Official Installation
Fabrication Toolkit is distributed with the official releases of KiCad 6+. Open the "Plugin and Content Manager" from the KiCad main menu and install the "<ins>Fabrication Toolkit</ins>" plugin from the selection list.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/manager.png?raw=true" height=275>

### Manual installation
Download the [latest release](https://github.com/bennymeg/JLC-Plugin-for-KiCad/releases) ZIP file. Open the "Plugin and Content Manager" from the KiCads main window and install the ZIP file via "Install from File".

## Usage
Click on the Fabrication Toolkit <img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/resources/icon.png?raw=true" style="magin-bottom: 8px;" alt="Logo" height=24> button on the top tool box inside KiCad pcb editor (pcbnew).

## Options

### Include Component Part Number in Production Files
Add an 'LCSC Part #'* field with the LCSC component part number to the symbol's fields property.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/mpn.png?raw=true" height=420>

#### Primary Fields*:
| 'LCSC Part #' | 'JLCPCB Part #' |
| --- | --- |

_The fields will be query in the order denoted above._

#### Fallback Fields*:
| 'JLC Part' | 'LCSC Part' | 'LCSC' | 'JLC' | 'MPN' | 'Mpn' | 'mpn' |
| --- | --- | --- | --- | --- | --- | --- |

_The fields will be query in the order denoted above._

### Ignore Footprint in Production Files
Select 'Exclude from board' or 'Exclude from BOM' in the symbol's attributes property in order to ignore the footprint from the relevant file.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/attributes.png?raw=true" height=420>

Select 'Exclude from position files' or 'Exclude from BOM' in the footprint's fabrication attributes property in order to ignore the footprint from the relevant file.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/fabrication.png?raw=true" height=505>

### Offset Component Rotation
The rotation of components in KiCad Footprints does not always match the orientation in the JLC library because KiCad and JLC PCB used different variation of the same standard. Most of the rotations may be corrected by the `rotations.cf` definitions. To the exception cases: add an 'JLC Rotation Offset' field with an counter-clockwise orientation offset in degrees to correct this.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/rotation-jlc.png?raw=true" height=164>

If the JLC preview shows a footprint like this, enter a rotation offset of -90 to rotate pin 1 to the lower right corner.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/rotation.png?raw=true" height=420>

#### Primary Fields*:
| 'JLCPCB Rotation Offset' |
| --- |

_The fields will be queried in the order denoted above._

#### Fallback Fields*:
| 'JlcRotOffset' | 'JLCRotOffset' |
| --- | --- |

_The fields will be queried in the order denoted above._

### Offset Component Position
The position of components in KiCad Footprints does not always match the orientation in the JLC library because KiCad and JLCPB used different variation of the same standard. To the exception cases: add an 'JLC Position Offset' field with an comma seperated x,y position offset to correct it.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/position.png?raw=true" height=420>

#### Primary Fields*:
| 'JLCPCB Position Offset' |
| --- |

_The fields will be queried in the order denoted above._

#### Fallback Fields*:
| 'JlcPosOffset' | 'JLCPosOffset' |
| --- | --- |

_The fields will be queried in the order denoted above._

## Author

Benny Megidish
