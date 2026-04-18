# G3 Assignment: Invasion Spacers Game - Release Candidate


## Game Description

Invasion Spacers is a 2D arcade shooter built in Python with Pygame using an ECS architecture. The player controls a ship at the bottom of the screen, clears enemy waves, survives boss-style leader encounters, and progresses through three levels with increasing pressure. 

## How to Run

Run in the terminal
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py

```

## Controls

### Gameplay
- A / D or Left / Right: move
- Space: fire
- P or Esc: pause/resume
- M: mute
- -: volume down
- = or keypad +: volume up
- F: reduced flash
- F1: debug
### Menus
- Up / Down or W / S: move selection
- Enter or Space: confirm
- Q: quit
### Controls screen
- Esc, Backspace, Enter, or Space: return

## Accessibility Options

### Alternate movement controls:
- A / D
- Left / Right
### Alternate menu navigation controls:
- W / S
- Up / Down
- Mute with M
- Volume control with - and = / keypad +
- Reduced flash mode with F

## Features:
- 3 levels
- 3 waves per level
- 1 leader fight per level
- Enemy formations and movement variation
- Enemy firing and leader firing
- Leader defense line phase

- Powerups:
    - extra life
    - rapid fire
    - shield

- HUD, boss bar, and transition cues
- Audio system with music, ambience, and sound effects
- Debug panel

## Known Issues

- The game still uses simple placeholder-style visuals instead of final sprite art.
- Late game guard phases may feel a little harder than intended.
- Powerup drop frequency may still need a little more balancing.

## Credits
- Sounds
    - https://app.envato.com
    - https://pixabay.com/sound-effects/
    - https://opengameart.org/content/space-sounds
- Graphics:
    - https://opengameart.org/content/graphic-fx
    - https://pngtree.com
    - https://www.freepik.com