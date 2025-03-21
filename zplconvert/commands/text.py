"""Text-related ZPL command handlers."""

from ..elements.text import TextElement

def handle_fd(params, state, label):
    """Handle FD (Field Data) command for text."""
    if not params:
        print("No field data provided for FD command")
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
        reverse=state.get('reverse_field', False)
    )
    label.add_element(text_element)
    print(f"Added text: '{data}' at ({state['current_x']}, {state['current_y']})")

def handle_fo(params, state, label):
    """Handle FO (Field Origin) command."""
    if len(params) == 2:
        state['current_x'], state['current_y'] = map(int, params)
        print(f"Set position to ({state['current_x']}, {state['current_y']})")

def handle_ft(params, state, label):
    """Handle FT (Field Typeset) command."""
    if len(params) == 2:
        state['current_x'], state['current_y'] = map(int, params)
        print(f"Set position to ({state['current_x']}, {state['current_y']}) using FT")

def handle_fs(params, state, label):
    """Handle FS (Field Separator) command."""
    state['reverse_field'] = False  # Reset reverse field after each field

def handle_fr(params, state, label):
    """Handle FR (Field Reverse) command."""
    state['reverse_field'] = True
    print("Reverse Field mode activated")

def handle_a0(params, state, label):
    """Handle A0 (Font) command."""
    if len(params) >= 3:
        font_name, font_width, font_height = params[:3]
        
        # Determine if the font should be bold
        is_bold = font_name in ['0', '2', '4', '6', '8']
        
        # Use original font size calculation that worked previously
        font_size = max(int(font_height), 12)  # Ensure minimum font size of 12
        
        state['current_font_size'] = font_size
        state['current_font_bold'] = is_bold
        
        print(f"Font set: size={font_size}, bold={is_bold}")

def handle_cf(params, state, label):
    """Handle CF (Change Font) command."""
    if len(params) >= 2:
        state['current_font_size'] = int(params[1])
        print(f"Changed font size to {state['current_font_size']}")

def register_text_commands(registry):
    """Register all text-related command handlers."""
    registry.register('FD', handle_fd)
    registry.register('FO', handle_fo)
    registry.register('FT', handle_ft)
    registry.register('FS', handle_fs)
    registry.register('FR', handle_fr)
    registry.register('A0', handle_a0)
    registry.register('CF', handle_cf)