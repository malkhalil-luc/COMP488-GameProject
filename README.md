# Invasion Spacers

Invasion Spacers is a 2D arcade shooter built in Python with Pygame using an ECS architecture. The player controls a ship at the bottom of the screen, clears enemy waves, survives boss-style leader encounters, and progresses through three levels with increasing pressure. 

## Setup
Requires Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
# .venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

#### Build Target

- OS: macOS
- Python version: Python 3.10 or newer
- Dependencies: listed in `requirements.txt`
- Main dependency: `pygame`

#### Platforms Tested

- macOS development machine
- macOS second laptop dry run
---

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
- `Esc`, `Backspace`, `Enter`, or `Space`: return


## Known Issues
- Late-game guard phases may still feel slightly harder than the rest of the game.
- Powerup drop balance may still need small tuning.
- The title screen only shows the top 5 saved scores to keep the menu readable.

## Credits
- Sounds
    - https://app.envato.com
    - https://pixabay.com/sound-effects/
    - https://opengameart.org/content/space-sounds
- Graphics:
    - https://opengameart.org/content/graphic-fx
    - https://pngtree.com
    - https://www.freepik.com


## Contributions to G4

- Armando Hernandez:
    - Worked on accessibility options, controls documentation, and final playtesting.
    - Helped tune level progression, wave difficulty, leader encounters, and guard phases.
    - Helped prepare the README, postmortem, demo plan, and final submission materials.

- Asad Tirmizi:
    - Helped split and clean the codebase into a clearer `src/` structure for the final package.
    - Helped with debugging, packaging checks, and making sure the game runs from `main.py`.
    - Worked on test gameplay balance and fix bugs found during playtesting.

- Mahran Alkhalil
    - Worked on audio, sound effects, ambience, volume control, mute, and scene-based audio behavior.
    - Worked on visuals and presentation, including sprites, backgrounds, HUD polish, menus, and screen readability.
    - Prepared the README, postmortem, demo plan, and final submission materials.
- Malec  Tarabein

