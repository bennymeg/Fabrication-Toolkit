import pcbnew  # type: ignore

baseUrl = 'https://www.jlcpcb.com'

netlistFileName = 'netlist.ipc'
designatorsFileName = 'designators.csv'
placementFileName = 'positions.csv'
bomFileName = 'bom.csv'
gerberArchiveName = 'gerbers.zip'
outputFolder = 'production'
bomRowLimit = 200

optionsFileName = 'fabrication-toolkit-options.json'

standardLayers = [ pcbnew.F_Cu, pcbnew.B_Cu,
                   pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.In3_Cu, pcbnew.In4_Cu, pcbnew.In5_Cu,
                   pcbnew.In6_Cu, pcbnew.In7_Cu, pcbnew.In8_Cu, pcbnew.In9_Cu, pcbnew.In10_Cu,
                   pcbnew.In11_Cu, pcbnew.In12_Cu, pcbnew.In13_Cu, pcbnew.In14_Cu, pcbnew.In15_Cu,
                   pcbnew.In16_Cu, pcbnew.In17_Cu, pcbnew.In18_Cu, pcbnew.In19_Cu, pcbnew.In20_Cu,
                   pcbnew.In21_Cu, pcbnew.In22_Cu, pcbnew.In23_Cu, pcbnew.In24_Cu, pcbnew.In25_Cu,
                   pcbnew.In26_Cu, pcbnew.In27_Cu, pcbnew.In28_Cu, pcbnew.In29_Cu, pcbnew.In30_Cu,
                   pcbnew.F_SilkS, pcbnew.B_SilkS,
                   pcbnew.F_Mask, pcbnew.B_Mask,
                   pcbnew.F_Paste, pcbnew.B_Paste,
                   pcbnew.Edge_Cuts
                   ]
