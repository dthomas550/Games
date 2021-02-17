import os, sys
from game_files.functions import *

__version__ = "4.0 Alpha"
__author__ = "D Thomas"
__email__ = "dt01@pm.me"
__license__ = "GPL 3"
__status__ = "Development"


def help_page():
    print("""
    -h      --  This help page.
    -f      --  Fast mode, goes through storyline actions as quick as possible. Also disables text crawl and ascii art.
    -t      --  Disable text crawl effect.
    -a      --  Hides ASCII art.
    -hud    --  Hide game HUD.
    -hard   --  Enable Hardcore mode.
    -hints  --  Hide game hints.
    -slime  --  Same as: -t -a
    """)
    exit(0)


if __name__ == '__main__':
    if '-h' in sys.argv: help_page()

    save_path = os.path.dirname(os.path.abspath(__file__)) + '/game.save'

    # Loads game save and updates rimuru object in game_functions alongside debug variable, and shows start banner.
    rimuru = update_rimuru(game_load(save_path))

    if get_any(sys.argv, ['-f', '-fast', '-fastmode']): rimuru.fast_mode = True
    if get_any(sys.argv, ['-t', '-text', '-textcrawl']): rimuru.textcrawl = False
    if get_any(sys.argv, ['-a', '-art', '-hideart']): rimuru.show_art = False
    if get_any(sys.argv, ['-hud', '-hidehud']): rimuru.show_hud = True
    if '-hard' in sys.argv: rimuru.hardcore = True
    if '-hints' in sys.argv: rimuru.show_hints = False
    if '-slime' in sys.argv:
        rimuru.textcrawl = rimuru.show_hud = rimuru.show_art = False
        rimuru.show_hints = True

    # Text output is slowed and looks like it's being typed out character by character. For dramatic effect.
    if rimuru.textcrawl is None:
        print("\nEnable Text Crawl? (Recommended for easier reading)")
        if str(input("No / Yes or Enter > ")).lower() in ['n', 'no']:
            print("\n    < Text Crawl Deactivated >\n")
            rimuru.textcrawl = False
        else:
            rimuru.textcrawl = True
            print()
            siprint("< Text Crawl Activated >\n\n")

    if rimuru.show_hints is None:
        print("\nShow game hints? Suggest leave enabled if first time playing.")
        if str(input("No / Yes or Enter > ")).lower() in ['n', 'no']:
            print("\n    < Hints: Enabled >\n")
            rimuru.show_hints = False
        else:
            rimuru.show_hints = True
            siprint("\n < Hints: Disabled >\n")

    show_start_banner()
    rimuru.current_location_object(rimuru)
