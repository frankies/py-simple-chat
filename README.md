# py-simple-chat

A simple Pygame-based alien invasion game.
## Web UI edition

A new web-based front end has been added. Run the server with `python -m webapp.app` and open http://localhost:5000 in your browser. The game logic has been ported to JavaScript and draws on an HTML5 canvas, while Python now only serves static assets.
## Installation

Use the `uv` environment commands:

```bash
uv install          # install dependencies in the venv
```

You can also install the project globally using pip:

```bash
pip install .
```

## Running the game

Launch via the script or directly:

```bash
uv run py-simple-chat   # within the uv environment
# or
python -m main          # when installed or from project root
```

Alternatively the legacy entry point:

```bash
uv run python game.py
```

## Controls

- Arrow keys: move ship
- Space: fire bullets

Have fun!