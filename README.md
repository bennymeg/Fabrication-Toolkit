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

**⊛** Ensure your board is syncronized before invoking this addon [**F8**].

**⊛** The `User_1` layer in internally defined as a **V-Cuts** layer, please avoid using it for anything else. <span style="text-color: light-grey !important;">_(since v3.0.0)_.</span>

## Options

Options can be set in the dialog that appears when the plugin is invoked. They are saved in a file called `fabrication-toolkit-options.json` in the project directory so that they are remembered between invocations of the plugin.

### ① Include Component Part Number in Production Files
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

---

### ② Ignore Footprint in Production Files
Select 'Exclude from board' or 'Exclude from BOM' in the symbol's attributes property in order to ignore the footprint from the relevant file.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/attributes.png?raw=true" height=420>

Select 'Exclude from position files' or 'Exclude from BOM' in the footprint's fabrication attributes property in order to ignore the footprint from the relevant file.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/fabrication.png?raw=true" height=505>

---

### ③ Offset Component Rotation
The rotation of components in KiCad Footprints does not always match the orientation in the JLC library because KiCad and JLC PCB used different variation of the same standard. Most of the rotations may be corrected by the `rotations.cf` definitions. To the exception cases: add an 'JLCPCB Rotation Offset' field - with positive values indicating counter-clockwise orientation offset in degrees.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/rotation-jlc.png?raw=true" height=164>

If the JLC preview shows a footprint like this, enter a rotation offset of -90 to rotate pin 1 to the lower right corner.

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/rotation.png?raw=true" height=420>

As the rotation offset is entered in the Schematic Editor, make sure to update your PCB with the changes made to the schematic before generating a new set of production files, otherwise your changes won't be reflected.

#### Primary Fields*:
| 'JLCPCB Rotation Offset' |
| --- |

_The fields will be queried in the order denoted above._

#### Fallback Fields*:
| 'JlcRotOffset' | 'JLCRotOffset' |
| --- | --- |

_The fields will be queried in the order denoted above._

---

### ④ Offset Component Position
The position of components in KiCad Footprints does not always match the orientation in the JLC library because KiCad and JLCPB used different variation of the same standard. To the exception cases: add an 'JLCPCB Position Offset' field with an comma separated x,y position offset to correct it. 

Use following table to quickly find out to which coordinate enter the correction based on JLC arrows clicks - depending on footprint rotation in Kicad PCB Editor status bar:
|Kicad footprint deg | x | y|
|----|----|----|
|0deg, Front | right arrow | up arrow |
|0deg, Back | left arrow | down arrow |
|180deg, Front | left arrow | down arrow |
|180deg, Back | right arrow | up arrow |
|90deg, Front or Back | up arrow | left arrow |
|-90deg, Front or Back | down arrow | right arrow |

For custom angles it's best to place also a temporary straight symbol to perform alignment.
Single arrow press in JLC is about 0.07mm shift (8 clicks is about 0.5mm).

<img src="https://github.com/bennymeg/JLC-Plugin-for-KiCad/blob/master/assets/position.png?raw=true" height=420>

As the position offset is entered in the Schematic Editor, make sure to update your PCB with the changes made to the schematic before generating a new set of production files, otherwise your changes won't be reflected.

#### Primary Fields*:
| 'JLCPCB Position Offset' |
| --- |

_The fields will be queried in the order denoted above._

#### Fallback Fields*:
| 'JlcPosOffset' | 'JLCPosOffset' |
| --- | --- |

_The fields will be queried in the order denoted above._

### ⑤ Override Component Layer
Some footprints may have their components defined on the opposite layer to there actual footprints. In these instances you can override mount side by using this field.

Values can be `top`, `bottom`, `t` or `b`.

#### Primary Fields*:
        | 'JLCPCB Layer Override' |
        | --- |

_The fields will be queried in the order denoted above._

#### Fallback Fields*:
        | 'JlcLayerOverride' | 'JLCLayerOverride' |
        | --- | --- |

_The fields will be queried in the order denoted above._



## Author

Benny Megidish
