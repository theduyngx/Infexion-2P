"""
Module:
    ``constants.py``

Purpose:
    Constants used globally by referee.

Notes:
    From COMP30024 Artificial Intelligence, Semester 1 2023, Project Part B: Game Playing Agent
    referee pre-completed package. Title screen is designed by The Duy Nguyen (1100548).
"""

# Define global game settings/constants
TITLE_SCREEN = r"""
\      /        \      /        \      /        \      /        \      /       
 )----(          )----(          )----(          )----(          )----(        
/      \        /      \        /      \        /      \        /      \       
        ██╗███╗/  ██╗███████╗███████╗██╗\ ██╗██╗ ██████╗ ███╗  /██╗     \      
        ██║████╗  ██║██╔════╝██╔════╝╚██╗██╔╝██║██╔═══██╗████╗( ██║      )----(
        ██║██╔██╗ ██║█████╗  █████╗    ███╔╝ ██║██║   ██║██╔██╗\██║     /      
\      /██║██║╚██╗██║██╔══╝  ██╔══╝   ██╔██╗ ██║██║   ██║██║╚██╗██║    /       
 )----( ██║██║ ╚████║██║     ███████╗██╔╝ ██╗██║╚██████╔╝██║-╚████║---(        
/      \╚═╝╚═╝  /═══╝╚═\     ╚══/═══╝╚═\  ╚═╝╚═╝/╚═════╝ ╚═╝  ╚═/═╝    \       
        \      /        \      /        \      /        \      /        \      
         )----(          )----(          )----(          )----(          )----(
        /      \        /      \        /      \        /      \        /      
"""

GAME_NAME       = "Infexion"
NUM_PLAYERS     = 2
BOARD_N         = 7
MAX_TOTAL_POWER = BOARD_N * BOARD_N
MAX_CELL_POWER  = BOARD_N - 1
MAX_TURNS       = BOARD_N * BOARD_N * BOARD_N
WIN_POWER_DIFF  = 2
