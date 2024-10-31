import argparse as ap

from .thread import ProcessThread
from .options import AUTO_FILL_OPT, AUTO_TRANSLATE_OPT, EXCLUDE_DNP_OPT, EXTEND_EDGE_CUT_OPT, ALTERNATIVE_EDGE_CUT_OPT, EXTRA_LAYERS
   

if __name__ == '__main__':
    parser = ap.ArgumentParser(prog="Fabrication Toolkit",
                            description="Generates JLCPCB production files from a KiCAD board file")

    parser.add_argument("--path",               "-p",  type=str, help="Path to KiCAD board file", required=True)
    parser.add_argument("--additionalLayers",   "-aL", type=str, help="Additional layers(comma-separated)")
    parser.add_argument("--user1VCut",          "-u1", action="store_true", help="Set User.1 as V-Cut layer")
    parser.add_argument("--user2AltVCut",       "-u2", action="store_true", help="Use User.2 for alternative Edge-Cut layer")
    parser.add_argument("--autoTransitions",    "-t",  action="store_true", help="Apply automatic position/rotation translations")
    parser.add_argument("--autoFill",           "-f",  action="store_true", help="Apply automatic fill for all zones")
    parser.add_argument("--excludeDNP",         "-e",  action="store_true", help="Exclude DNP components from BOM")
    parser.add_argument("--openBrowser",        "-b",  action="store_true", help="Open webbrowser with directory file overview after generation")
    args = parser.parse_args()

    options = dict()
    options[EXTRA_LAYERS] = args.additionalLayers
    options[EXTEND_EDGE_CUT_OPT] = args.user1VCut
    options[ALTERNATIVE_EDGE_CUT_OPT] = args.user2AltVCut
    options[AUTO_TRANSLATE_OPT] = args.autoTransitions
    options[AUTO_FILL_OPT] = args.autoFill
    options[EXCLUDE_DNP_OPT] = args.excludeDNP
    openBrowser = args.openBrowser


    path = args.path

    ProcessThread(wx=None, cli=path, options=options, openBrowser=openBrowser)