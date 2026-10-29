# SHADOW STRIKE: Last Survivor

A 2D side-view action platform shooter built with **Python** and **Pygame**. Survive incoming enemy waves, eliminate hostiles, collect coins, and chase your high score.

## Features

- Custom-drawn player character and enemies — no external image assets required.
- Side-view movement, jumping, and a platform/ground.
- Enemies approach from the left and right.
- Standard enemies and tougher ranged enemies that shoot back.
- Shooting effects, muzzle flash, particles, hit feedback, and camera shake.
- Health bar, score, ammo, reserve ammo, kill count, wave counter, coins, and timer.
- Reloading, health recovery from coins, and wave-based difficulty.
- Main menu, pause menu, mission-failed screen, and restart flow.
- Fullscreen toggle.
- Personal-best score tracked while the game is running.

## Requirements

- Python 3.10 or newer recommended.
- Pygame 2.x.
- Windows, macOS, or Linux with a graphical desktop.

## Installation

### 1. Install Python

If Python is not installed, download it from [python.org](https://www.python.org/downloads/). On Windows, enable **Add Python to PATH** during installation if that option is shown.

### 2. Install Pygame

Open Command Prompt or PowerShell in Windows, or a terminal on macOS/Linux, and run:

```bash
python -m pip install pygame
```

On Windows, you can also use:

```bash
py -m pip install pygame
```

### 3. Download the game

Download `shadow_strike.py` and place it in a folder, for example:

```text
ShadowStrike/
└── shadow_strike.py
```

### 4. Run the game

Open a terminal in that folder and run:

```bash
python shadow_strike.py
```

On Windows, if `python` is not recognized, try:

```bash
py shadow_strike.py
```

## Controls

| Input | Action |
|---|---|
| `A` / `D` or `←` / `→` | Move left / right |
| `W`, `↑`, or `Space` | Jump |
| Left mouse button or `J` | Shoot |
| `R` | Reload |
| `P` or `Esc` | Pause / resume |
| `Enter` | Start or restart |
| `F` | Toggle fullscreen |

The weapon fires in the direction the player is facing.

## Gameplay

1. Start the mission with **Enter**.
2. Keep moving and jump to avoid enemies.
3. Shoot approaching enemies before they reach you.
4. Watch your health and ammunition. Press **R** to reload.
5. Collect dropped coins by moving close to them. Coins add score and restore a small amount of health.
6. Survive for as long as possible. Enemy waves become more challenging over time.

## Project structure

```text
ShadowStrike/
├── shadow_strike.py   # Game code and custom-drawn visuals
└── README.md          # Project documentation
```

The game draws its characters, interface, background, projectiles, and effects directly with Pygame. No separate assets folder is needed.

## Troubleshooting

### `ModuleNotFoundError: No module named 'pygame'`

Install Pygame with the same Python interpreter used to run the game:

```bash
python -m pip install pygame
```

On Windows, try:

```bash
py -m pip install pygame
```

### `python` or `py` is not recognized

Reinstall Python from [python.org](https://www.python.org/downloads/) and enable the PATH option, or run the game using the full path to your Python executable.

### The game window opens and closes immediately

Run the game from a terminal so the error message remains visible:

```bash
python shadow_strike.py
```

Read the error printed in the terminal.

### No sound

The current version is designed to run without an audio device and does not include sound effects yet.

## Current limitations

- The player and enemies are drawn procedurally rather than animated from sprite sheets.
- The current version does not include sound effects or background music.
- The best score is kept in memory only and resets when the application closes.
- The game uses a single main platform rather than multiple platforming levels.

## Ideas for future improvements

- Sprite-sheet animations for running, jumping, shooting, reloading, and taking damage.
- Sound effects and background music with volume controls.
- Multiple weapons, weapon upgrades, and collectible power-ups.
- Boss fights, more enemy types, and varied environments.
- Persistent high scores and settings saved to a local file.
- Multiple levels, platforms, and a proper scrolling world.
- Gamepad support and a settings screen.

## Technology

- **Language:** Python
- **Library:** Pygame
- **Rendering:** Pygame drawing primitives
- **Game loop:** Event handling, update, collision detection, and rendering

## License

No license has been specified yet. Add a `LICENSE` file before redistributing the project if you want to grant others explicit reuse permissions.
