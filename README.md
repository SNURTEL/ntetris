# Welcone to ntetris!
This is my first semester Python programming project, currently in the middle of being rewritten. With that said, what you're seeing here implements only a part of original functionality, I will be adding more step-by-step.

Initially, this was a [Tetris](https://pl.wikipedia.org/wiki/Tetris) clone written in Python, designed to run purely in command line using `ncurses`. [Tetris guidelines](https://tetris.fandom.com/wiki/Tetris_Guideline) were generally implemented, a simple score table and an ability to choose starting level were also added.

### Original project (before rewriting):
<p float="left">
  <img src="/images/img_1.png" width="200" />
  <img src="/images/img_2.png" width="200" /> 
</p>
<p float="left">
  <img src="/images/img_3.png" width="200" />
  <img src="/img_4.png" width="200" /> 
</p>

The source code lies buried deep in the commit history.

### Usage
Initialize a virtual environment and install dependencies (if any present). Example using Poetry with lock file:
```shell
poetry shell
poetry install
```
Then, simply:
```shell
python3 tetris.py
```
Tested to be working with kitty, XTerm and gnome-terminal.
