# INFEXION The Game

*Specifications*: Please read the project specs (in documents directory).<br>
*Authors*: The Duy Nguyen and Ramon Javier L. Felipe VI.<br>
*Acknowledgement*: `referee` source code is originally written by the
University of Melbourne, COMP30024, Semester 1, 2024; modified and tweaked by the authors.
You can also play the game here: 
https://comp30024.pages.gitlab.unimelb.edu.au/2023s1/infexion-playground/


Basic run
------------

### Overview
* To run:
  ```bash
  $ python3 referee agent agent
  ```
* Recommended run:
  ```bash
  $ python3 referee agent agent -s -t -u -c
  ```
  where the tags, respectively, represent: space and time limit allowed, unicode-allowed, and 
  ansi-color allowed.

### Windows ansi-format
Windows does not support ansi formatting by default, so to enable it, do as follows:
* Open **Registry Editor**
* Go to **HKEY_CURRENT_USER** folder
* Double-click on **Console** folder
* Select **Edit**, **New**, **DWORD**
* Name it *VirtualTerminalLevel*, and choose **Modify**
* Fill in **Value Data** *10* in Hexadecimal
* Save

### Pycharm run
* Choose **Edit Configuration** at Run
* Click "**+**", or New, **Python**
* Choose **Module name** (instead of *Script path*)
* Parameters: `agent agent -s -t -c -u` (the last 2 tags are optional, as discussed)
* Environment Variable: `PYTHONUNBUFFERED=1`
* Choose a Python Interpreter (must be Python 3.10 or newer)
* Working directory: "**../AI-part-B**"
* In Execution, tick **Emulate terminal in output console**


Advanced run
------------

### Agent parameters
Advanced running will concern mostly with agent parameters. These are the 4 ways you could call
your agent in the program command:

1. The most conventional way is to specify your agent class as `Agent` in an un-capitalized
   package name (i.e. `agent`, `greedy`, etc.). With this, the command should be:
   ```bash
   $ python3 referee agent greedy
   ```

2. The second conventional way is to specify your package as `agent` (again, the casing of
   packages and classes are very important). Doing this, likewise, allows you to name your
   agent class anything, as long as its first character is capitalized (i.e. `GreedyAgent`,
   `MinimaxAgent`, etc.). With this, the command should be:
   ```bash
   $ python3 referee GreedyAgent MinimaxAgent
   ```

3. If specified by agent (the second way), then there are specific abbreviations that may be
   of convenience to use:
   * `A` for `Agent`
   * If the word `R` (in any casing) is included, it will represent `RandomAgent`
   * If the word `G` (in any casing) is included, it will represent `GreedyAgent`
   * If `MC` (in any casing) is included, it will represent `MonteCarloAgent`
   * If `MS` (in any casing) is included, it will represent `MinimaxShallowAgent`
   * If `NG` (in any casing) is included, it will represent `NegaScoutAgent`
   
   Example: The following will run GreedyAgent and RandomAgent specifically in the `agent` package:
   ```bash
   $ python3 referee GA R
   ```
   Note that abbreviations, for the sake of convenience, to be triggered, the agent's parameters
   in the command must have *length of less than 5*. Otherwise, the program will simply consider
   the input as **verbose**.<br><br>

4. The final way is **verbose**, meaning to specify the entire directory for the agent. The user
   should enter the agent in this format: `package/path/to/Agent`.<br>
   Note that the deliminator `/` may be replaced with `\` or `.` instead, but everything must be
   uniformed. An example is you put your `NegamaxAgent` agent in a script named `agents`. The path to
   that script is: `my_agent/minimax/agents`, where `my_agent` is top-level package, same level as
   `referee`. Then the command would be like this:
   ```bash
   $ python3 referee agent my_agent/minimax/agents/NegamaxAgent
   ```
