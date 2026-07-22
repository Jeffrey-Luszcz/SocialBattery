from badgeware import screen, brushes, io, Image, PixelFont
import sys

# Social Battery for the GitHub Universe 2025 badge
# https://github.com/Jeffrey-Luszcz/SocialBattery
# # SPDX-License-Identifier: MIT

# ---------------------------------------------------------------------------
# Optional name override: enter a value here to display a custom name in the
# bottom bar instead of your GitHub handle. Leave "" to only use the handle.
NAME = ""
# ---------------------------------------------------------------------------

# Gray slider bar (framebuffer coords): x 4..156, vertical center ~83
DIAMOND = 24
BAR_Y_CENTER = 83
DIAMOND_Y = BAR_Y_CENTER - DIAMOND // 2  # top-left y

# Bottom black bar (framebuffer rows ~101..119) where the name is shown
NAME_BAR_Y = 110

# Target top-left x positions and movement limits
STEP = 1                             # pixels moved per momentary A/C press
HOLD_START = 0.5                     # starting speed (px/frame) when a button is first held
HOLD_MAX = 3.0                       # top speed (px/frame) after ramping up
HOLD_RAMP = 0.04                     # how much speed increases each frame while held
EASE = 0.18                          # lower = smoother/slower glide toward target
POS_MIN = -6                         # let the diamond reach past the left edge
POS_MAX = 160 - DIAMOND + 6          # and past the right edge (140)
POS_CENTER = (160 - DIAMOND) // 2    # 68

# Loaded in init(); animated position state
background = None
diamond = None
small_font = None
state = {"x": float(POS_CENTER), "target": POS_CENTER}
# Manually tracked "currently down" flags (avoids relying on io.held)
down = {"a": False, "c": False}
# Current ramped hold speed (px/frame)
hold_speed = HOLD_START

# Name display: cycle order is handle -> none -> name (name only if NAME is set)
handle = None            # GitHub handle read from /secrets.py
name_modes = []          # list of modes available this run
name_index = 0           # current mode


def _load_handle():
    """Read GITHUB_USERNAME from a secrets.py at the badge filesystem root."""
    sys.path.insert(0, "/")
    try:
        from secrets import GITHUB_USERNAME
        return GITHUB_USERNAME
    except Exception:
        return None
    finally:
        try:
            sys.path.pop(0)
        except Exception:
            pass


def _build_name_modes():
    """Default is the handle, then none, then the optional source name."""
    modes = ["handle", "none"]
    if NAME:
        modes.append("name")
    return modes


def init():
    global background, diamond, small_font, hold_speed
    global handle, name_modes, name_index
    # Load resources once the app is launched (assets/ is on the path here)
    background = Image.load("assets/background.png")
    diamond = Image.load("assets/diamond.png")
    try:
        small_font = PixelFont.load("/system/assets/fonts/ark.ppf")
    except Exception:
        small_font = None
    state["x"] = float(POS_CENTER)
    state["target"] = POS_CENTER
    down["a"] = False
    down["c"] = False
    hold_speed = HOLD_START
    handle = _load_handle()
    name_modes = _build_name_modes()
    name_index = 0


def _current_name_text():
    """Text to draw in the bottom bar for the active mode ('' means nothing)."""
    if not name_modes:
        return ""
    mode = name_modes[name_index]
    if mode == "handle":
        return ("@" + handle) if handle else ""
    if mode == "name":
        return NAME
    return ""  # "none"


def _draw_name():
    text = _current_name_text()
    if not text:
        return
    if small_font is not None:
        screen.font = small_font
    screen.brush = brushes.color(255, 255, 255)
    try:
        w, h = screen.measure_text(text)
    except Exception:
        w, h = len(text) * 6, 8
    screen.text(text, int(80 - w / 2), int(NAME_BAR_Y - h / 2))


def update():
    # Lazily load in case init() was not called
    global background, diamond, hold_speed, name_index
    global handle, name_modes, small_font
    if background is None:
        background = Image.load("assets/background.png")
        diamond = Image.load("assets/diamond.png")
        try:
            small_font = PixelFont.load("/system/assets/fonts/ark.ppf")
        except Exception:
            small_font = None
        handle = _load_handle()
        name_modes = _build_name_modes()
        name_index = 0

    # UP / DOWN cycle the name display mode (handle -> none -> name)
    if name_modes:
        if io.BUTTON_UP in io.pressed:
            name_index = (name_index + 1) % len(name_modes)
        if io.BUTTON_DOWN in io.pressed:
            name_index = (name_index - 1) % len(name_modes)

    # Track A/C down-state from press/release events
    if io.BUTTON_A in io.pressed:
        down["a"] = True
    if io.BUTTON_A in io.released:
        down["a"] = False
    if io.BUTTON_C in io.pressed:
        down["c"] = True
    if io.BUTTON_C in io.released:
        down["c"] = False

    # A -> nudge left, C -> nudge right (small steps), B -> recenter
    if io.BUTTON_A in io.pressed:
        state["target"] = max(POS_MIN, state["target"] - STEP)
    if io.BUTTON_B in io.pressed:
        state["target"] = POS_CENTER
    if io.BUTTON_C in io.pressed:
        state["target"] = min(POS_MAX, state["target"] + STEP)

    # While A or C is held, ramp the speed up slowly and keep sliding
    if down["a"] or down["c"]:
        hold_speed = min(HOLD_MAX, hold_speed + HOLD_RAMP)
        if down["a"]:
            state["target"] = max(POS_MIN, state["target"] - hold_speed)
        if down["c"]:
            state["target"] = min(POS_MAX, state["target"] + hold_speed)
    else:
        # Reset the ramp once both buttons are released
        hold_speed = HOLD_START

    # Ease the diamond toward its target for a smooth slide
    state["x"] += (state["target"] - state["x"]) * EASE
    if abs(state["target"] - state["x"]) < 0.5:
        state["x"] = float(state["target"])

    # Draw background then the diamond on the slider bar
    screen.blit(background, 0, 0)
    screen.blit(diamond, int(round(state["x"])), DIAMOND_Y)

    # Draw the name/handle in the bottom black bar for the active mode
    _draw_name()
