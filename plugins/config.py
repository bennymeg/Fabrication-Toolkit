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