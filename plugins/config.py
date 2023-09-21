import pcbnew  # type: ignore

baseUrl = 'https://www.jlcpcb.com'

netlistFileName = 'netlist.ipc'
designatorsFileName = 'designators.csv'
placementFileName = 'positions.csv'
bomFileName = 'bom.csv'
gerberArchiveName = 'gerbers.zip'
outputFolder = 'production'

plotPlan = [
    ("F.Cu", pcbnew.F_Cu, "Top Layer"),
    ("B.Cu", pcbnew.B_Cu, "Bottom Layer"),
    ("In1.Cu", pcbnew.In1_Cu, "Internal plane 1"),
    ("In2.Cu", pcbnew.In2_Cu, "Internal plane 2"),
    ("In3.Cu", pcbnew.In3_Cu, "Internal plane 3"),
    ("In4.Cu", pcbnew.In4_Cu, "Internal plane 4"),
    ("In5.Cu", pcbnew.In5_Cu, "Internal plane 5"),
    ("In6.Cu", pcbnew.In6_Cu, "Internal plane 6"),
    ("In7.Cu", pcbnew.In7_Cu, "Internal plane 7"),
    ("In8.Cu", pcbnew.In8_Cu, "Internal plane 8"),
    ("In9.Cu", pcbnew.In9_Cu, "Internal plane 9"),
    ("In10.Cu", pcbnew.In10_Cu, "Internal plane 10"),
    ("In11.Cu", pcbnew.In11_Cu, "Internal plane 11"),
    ("In12.Cu", pcbnew.In12_Cu, "Internal plane 12"),
    ("In13.Cu", pcbnew.In13_Cu, "Internal plane 13"),
    ("In14.Cu", pcbnew.In14_Cu, "Internal plane 14"),
    ("In15.Cu", pcbnew.In15_Cu, "Internal plane 15"),
    ("In16.Cu", pcbnew.In16_Cu, "Internal plane 16"),
    ("In17.Cu", pcbnew.In17_Cu, "Internal plane 17"),
    ("In18.Cu", pcbnew.In18_Cu, "Internal plane 18"),
    ("In19.Cu", pcbnew.In19_Cu, "Internal plane 19"),
    ("In20.Cu", pcbnew.In20_Cu, "Internal plane 20"),
    ("In21.Cu", pcbnew.In21_Cu, "Internal plane 21"),
    ("In22.Cu", pcbnew.In22_Cu, "Internal plane 22"),
    ("In23.Cu", pcbnew.In23_Cu, "Internal plane 23"),
    ("In24.Cu", pcbnew.In24_Cu, "Internal plane 24"),
    ("In25.Cu", pcbnew.In25_Cu, "Internal plane 25"),
    ("In26.Cu", pcbnew.In26_Cu, "Internal plane 26"),
    ("In27.Cu", pcbnew.In27_Cu, "Internal plane 27"),
    ("In28.Cu", pcbnew.In28_Cu, "Internal plane 28"),
    ("In29.Cu", pcbnew.In29_Cu, "Internal plane 29"),
    ("In30.Cu", pcbnew.In30_Cu, "Internal plane 30"),
    ("F.SilkS", pcbnew.F_SilkS, "Top Silkscreen"),
    ("B.SilkS", pcbnew.B_SilkS, "Bottom Silkscreen"),
    ("F.Mask", pcbnew.F_Mask, "Top Soldermask"),
    ("B.Mask", pcbnew.B_Mask, "Bottom Soldermask"),
    ("F.Paste", pcbnew.F_Paste, "Top Paste (Stencil)"),
    ("B.Paste", pcbnew.B_Paste, "Bottom Paste (Stencil)"),
    ("Edge.Cuts", pcbnew.Edge_Cuts, "Board Outline"),
    ("User.Comments", pcbnew.Cmts_User, "User Comments")
]
