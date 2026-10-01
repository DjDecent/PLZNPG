"""Text-related ZPL command handlers."""

from ..elements.text import TextElement
from ..elements.field_block import FieldBlockElement


def handle_fd(params, state, label):
    """Handle FD (Field Data) command for text."""
    if not params:
        return

    data = params[0]

    if state.get('expecting_barcode'):
        return

    block = state.get('field_block')
    element_class = FieldBlockElement if block is not None else TextElement
    text_element = element_class(
        state['current_x'],
        state['current_y'],
        data,
        font_size=state.get('current_font_size', 12),
        font_width=state.get('current_font_width'),
        bold=state.get('current_font_bold', False),
        reverse=state.get('reverse_field', False),
        rotation=state.get('current_rotation', 0),
        origin_mode=state.get('origin_mode', 'FO'),
        font_name=state.get('current_font', '0'),
        **({'block': block} if block is not None else {}),
    )
    label.add_element(text_element)


def handle_fo(params, state, label):
    """Handle FO (Field Origin) command — top-left origin."""
    if len(params) >= 2:
        try:
            state['current_x'] = int(params[0])
            state['current_y'] = int(params[1])
            state['origin_mode'] = 'FO'
        except ValueError:
            pass


def handle_ft(params, state, label):
    """Handle FT (Field Typeset) command — baseline / bottom origin."""
    if len(params) >= 2:
        try:
            state['current_x'] = int(params[0])
            state['current_y'] = int(params[1])
            state['origin_mode'] = 'FT'
        except ValueError:
            pass


def handle_fs(params, state, label):
    """Handle FS (Field Separator) command."""
    state['reverse_field'] = False
    state['expecting_barcode'] = False
    state.pop('field_block', None)


def handle_fr(params, state, label):
    """Handle FR (Field Reverse) command."""
    state['reverse_field'] = True


def handle_a0(params, state, label):
    """Handle A0 (Scalable Font) command.

    ^A0o,h,w  or orientation may be in params[0] as N/R/I/B
    """
    if not params:
        return

    orientation = 'N'
    height = None
    width = None

    # Forms: params = ['N', '48', '48'] or ['48', '48'] after A0N split oddly
    if params[0].strip().upper() in ('N', 'R', 'I', 'B'):
        orientation = params[0].strip().upper()
        if len(params) > 1 and params[1].strip().isdigit():
            height = int(params[1])
        if len(params) > 2 and params[2].strip().isdigit():
            width = int(params[2])
    else:
        if params[0].strip().isdigit():
            height = int(params[0])
        if len(params) > 1 and params[1].strip().isdigit():
            width = int(params[1])

    rotation_map = {'N': 0, 'R': 90, 'I': 180, 'B': 270}
    state['current_rotation'] = rotation_map.get(orientation, 0)

    # Font 0 is the default scalable font; treat as bold condensed for label look
    state['current_font_bold'] = True
    state['current_font'] = '0'

    if height is not None:
        state['current_font_size'] = max(height, 8)
        if width is None or width == 0:
            state['current_font_width'] = max(height, 8)
    if width is not None:
        state['current_font_width'] = max(width or state['current_font_size'], 8)


def handle_cf(params, state, label):
    """Handle CF (Change Font) command."""
    if params and params[0].strip():
        state['current_font'] = params[0].strip()
    if len(params) >= 2 and params[1].strip().isdigit():
        state['current_font_size'] = int(params[1])
        state['current_font_width'] = int(params[1])
    if len(params) >= 3 and params[2].strip().isdigit():
        state['current_font_width'] = int(params[2])


def handle_fb(params, state, label):
    """Configure wrapping and alignment for the current field only."""
    def number(index, default, minimum, maximum):
        try:
            value = int(params[index].strip())
        except (ValueError, IndexError):
            value = default
        return max(minimum, min(maximum, value))

    alignment = params[3].strip().upper() if len(params) > 3 else 'L'
    state['field_block'] = {
        'width': number(0, 0, 0, label.width),
        'max_lines': number(1, 1, 1, 9999),
        'line_spacing': number(2, 0, -9999, 9999),
        'alignment': alignment if alignment in ('L', 'C', 'R', 'J') else 'L',
        'indent': number(4, 0, 0, 9999),
    }


def register_text_commands(registry):
    """Register all text-related command handlers."""
    registry.register('FD', handle_fd)
    registry.register('FO', handle_fo)
    registry.register('FT', handle_ft)
    registry.register('FS', handle_fs)
    registry.register('FR', handle_fr)
    registry.register('A0', handle_a0)
    registry.register('CF', handle_cf)
    registry.register('FB', handle_fb)
