# INFEXION The Game

*Specifications*: Please read it in the specs.<br>
*Authors*: The Duy Nguyen and Ramon Javier L. Felipe VI.
*Acknowledgement*: `referee` source code is originally written by the
University of Melbourne, COMP30024, Semester 1, 2024; modified and tweaked by the authors.

### Instructions:

To run the game:
* To run: `python3 referee agent agent`
* Recommended run: `python3 referee agent agent -s -t -u -c` where the tags, respectively,
  represent: space and time limit allowed, unicode-allowed, and ansi-color allowed.

If using Windows, which would not support ansi formats by default, do as follows:
* Open **Registry Editor**
* Go to **HKEY_CURRENT_USER** folder
* Double-click on **Console** folder
* Select **Edit**, **New**, **DWORD**
* Name it *VirtualTerminalLevel*, and choose **Modify**
* Fill in **Value Data** *10* in Hexadecimal
* Save

To run the game in Pycharm, do as follows:
* Choose **Edit Configuration** at Run
* Click "**+**", or New, **Python**
* Choose **Module name** (instead of *Script path*)
* Parameters: `agent agent -s -t -c -u` (the last 2 tags are optional, as discussed)
* Environment Variable: `PYTHONUNBUFFERED=1`
* Choose a Python Interpreter (must be Python 3.10 or newer)
* Working directory: "**../AI-part-B**"
* In Execution, tick **Emulate terminal in output console**

Agent parameters when running the game:
* ...
