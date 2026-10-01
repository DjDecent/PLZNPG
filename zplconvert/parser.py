"""ZPL parser module."""

from .label import Label
from .commands import create_command_registry
from .optimizer import optimize_zpl


def parse_zpl(zpl_data, width=812, height=1218, dpi=203):
    """Parse ZPL data and return a Label object."""
    zpl_data = optimize_zpl(zpl_data)

    label = Label(width, height, dpi)
    registry = create_command_registry()

    state = {
        'current_x': 0,
        'current_y': 0,
        'current_font_size': 12,
        'current_font_width': 12,
        'reverse_field': False,
        'current_font_bold': True,
        'current_rotation': 0,
        'origin_mode': 'FO',
        'expecting_barcode': False,
        'barcode_type': None,
        'barcode_height': 100,
        'barcode_width': 300,
        'barcode_width_ratio': 3.0,
        'module_width': 2,
        'barcode_module_size': 10,
        'barcode_quality': 200,
        'print_width': width,
        'label_length': height,
    }

    commands = zpl_data.strip().split('^')
    for command in commands:
        if not command or command.startswith('XZ'):
            continue

        cmd = command[:2]
        if cmd == 'FD':
            params = [command[2:]]
        else:
            params = command[2:].split(',')

        if cmd == 'FD' and state.get('expecting_barcode'):
            registry.handle('FD_BARCODE', params, state, label)
        else:
            if not registry.handle(cmd, params, state, label):
                # Silently ignore known no-ops; warn on others
                if cmd not in ('CI', 'PQ', 'LH', 'LT', 'LS', 'PR', 'MD', 'MM', 'JZ', 'PO'):
                    print(f"Unknown or unhandled command: {cmd}")

    # Media dimensions belong to the requested canvas. Fields outside it clip.
    label.width, label.height = width, height

    return label
