import argparse as ap

from .thread import ProcessThread
from .options import *
   

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog="Fabrication Toolkit",
                            description="Generates JLCPCB production files from a KiCAD board file")

    parser.add_argument("--path",               "-p",  type=str, help="Path to KiCAD board file", required=True)
    parser.add_argument("--additionalLayers",   "-aL", type=str, help="Additional layers(comma-separated)")
    parser.add_argument("--user1VCut",          "-u1", action="store_true", help="Set User.1 as V-Cut layer")
    parser.add_argument("--user2AltVCut",       "-u2", action="store_true", help="Use User.2 for alternative Edge-Cut layer")
    parser.add_argument("--autoTranslate",      "-t",  action="store_true", help="Apply automatic position/rotation translations")
    parser.add_argument("--autoFill",           "-f",  action="store_true", help="Apply automatic fill for all zones")
    parser.add_argument("--excludeDNP",         "-e",  action="store_true", help="Exclude DNP components from BOM")
    parser.add_argument("--allActiveLayers",    "-aaL",action="store_true", help="Export all active layers instead of only commonly used ones")
    parser.add_argument("--openBrowser",        "-b",  action="store_true", help="Open webbrowser with directory file overview after generation")
    args = parser.parse_args()

    options = dict()
    options[AUTO_TRANSLATE_OPT] = args.autoTranslate
    options[AUTO_FILL_OPT] = args.autoFill
    options[EXCLUDE_DNP_OPT] = args.excludeDNP
    options[EXTEND_EDGE_CUT_OPT] = args.user1VCut
    options[ALTERNATIVE_EDGE_CUT_OPT] = args.user2AltVCut
    options[ALL_ACTIVE_LAYERS_OPT] = args.allActiveLayers
    options[EXTRA_LAYERS] = args.additionalLayers

    openBrowser = args.openBrowser


    path = args.path

    ProcessThread(wx=None, cli=path, options=options, openBrowser=openBrowser)