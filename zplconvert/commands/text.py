"""Text-related ZPL command handlers."""

from ..elements.text import TextElement

def handle_fd(params, state, label):
    """Handle FD (Field Data) command for text."""
    if not params:
        return
        
    data = params[0]  # The entire field data
    
    if state.get('expecting_barcode'):
        return  # Let barcode handler deal with this
        
    text_element = TextElement(
        state['current_x'],
        state['current_y'],
        data,
        font_size=state.get('current_font_size', 12),
        bold=state.get('current_font_bold', False),
        reverse=state.get('reverse_field', False),
        rotation=state.get('current_rotation', 0)  # Pass the current rotation
    )
    label.add_element(text_element)

def handle_fo(params, state, label):
    """Handle FO (Field Origin) command."""
    if len(params) == 2:
        state['current_x'], state['current_y'] = map(int, params)

def handle_ft(params, state, label):
    """Handle FT (Field Typeset) command."""
    if len(params) == 2:
        state['current_x'], state['current_y'] = map(int, params)

def handle_fs(params, state, label):
    """Handle FS (Field Separator) command."""
    state['reverse_field'] = False  # Reset reverse field after each field

def handle_fr(params, state, label):
    """Handle FR (Field Reverse) command."""
    state['reverse_field'] = True

def handle_a0(params, state, label):
    """Handle A0 (Font) command."""
    if len(params) >= 3:
        # Parse the font specifier which may include orientation
        font_specifier = params[0]
        font_width, font_height = params[1:3]
        
        # Extract the orientation code (N, R, I, B) from the font specifier
        orientation = 'N'  # Default to normal orientation
        if len(font_specifier) > 0:
            orientation = font_specifier[-1]  # Last character is orientation
        
        # Set rotation based on orientation
        if orientation == 'N':
            state['current_rotation'] = 0  # Normal
        elif orientation == 'R':
            state['current_rotation'] = 90  # Rotated 90° clockwise
        elif orientation == 'I':
            state['current_rotation'] = 180  # Inverted (180°)
        elif orientation == 'B':
            state['current_rotation'] = 270  # Bottom up (270°)
        
        # Determine if the font should be bold (based on the font number)
        is_bold = False
        if len(font_specifier) > 0 and font_specifier[0] in ['0', '2', '4', '6', '8']:
            is_bold = True
        
        # Set font size (ensure minimum font size of 12)
        font_size = max(int(font_height), 12)
        
        state['current_font_size'] = font_size
        state['current_font_bold'] = is_bold

def handle_cf(params, state, label):
    """Handle CF (Change Font) command."""
    if len(params) >= 2:
        state['current_font_size'] = int(params[1])

def register_text_commands(registry):
    """Register all text-related command handlers."""
    registry.register('FD', handle_fd)
    registry.register('FO', handle_fo)
    registry.register('FT', handle_ft)
    registry.register('FS', handle_fs)
    registry.register('FR', handle_fr)
    registry.register('A0', handle_a0)
    registry.register('CF', handle_cf)
