"""ZPL parser module."""

from .label import Label
from .commands import create_command_registry

def parse_zpl(zpl_data, width=850, height=1200, dpi=203):
    """Parse ZPL data and return a Label object.
    
    Args:
        zpl_data (str): ZPL commands as text
        width (int): Width of the label in pixels
        height (int): Height of the label in pixels
        dpi (int): Dots per inch resolution
        
    Returns:
        Label: The populated label object
    """
    # Create a new label
    label = Label(width, height, dpi)
    
    # Create a command registry
    registry = create_command_registry()
    
    # Initialize state
    state = {
        'current_x': 0,
        'current_y': 0,
        'current_font_size': 12,
        'reverse_field': False,
        'current_font_bold': False,
        'current_rotation': 0,
        'expecting_barcode': False,
        'barcode_type': None,
        'barcode_height': None,
        'barcode_width': None,
        'barcode_width_ratio': 3.0,
    }
    
    # Parse ZPL commands
    commands = zpl_data.strip().split('^')
    for command in commands:
        if not command or command.startswith('XZ'):  # Empty or end of file
            continue
            
        # Extract command and parameters
        cmd = command[:2]
        params = []
        
        if cmd == 'FD':
            # For FD command, keep everything after 'FD' as a single string
            params = [command[2:]]
        else:
            # For other commands, split by comma
            params = command[2:].split(',')
        
        # Special handling for FD command when expecting a barcode
        if cmd == 'FD' and state.get('expecting_barcode'):
            registry.handle('FD_BARCODE', params, state, label)
        else:
            # Handle the command
            if not registry.handle(cmd, params, state, label):
                print(f"Unknown or unhandled command: {cmd}")
    
    return label
