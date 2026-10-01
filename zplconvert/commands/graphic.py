"""Graphic-related ZPL command handlers."""

from ..elements.graphic import BoxElement, ImageElement, LineElement
import logging

logger = logging.getLogger(__name__)


def handle_gb(params, state, label):
    """Handle GB (Graphic Box) command."""
    if len(params) < 3:
        logger.warning("Insufficient parameters for GB command")
        return

    try:
        width = int(params[0]) if params[0].strip() else 0
        height = int(params[1]) if params[1].strip() else 0
        thickness = int(params[2]) if params[2].strip() else 1
    except ValueError:
        logger.warning(f"Invalid GB parameters: {params}")
        return

    color = params[3].strip().upper() if len(params) >= 4 and params[3].strip() else 'B'
    width = max(width, thickness)
    height = max(height, thickness)
    rgb_color = (0, 0, 0) if color == 'B' else (255, 255, 255)

    x, y = state['current_x'], state['current_y']

    # Zero width or height → line of given thickness
    if height == 0 or width == 0:
        element = LineElement(
            x,
            y,
            width if width else thickness,
            height if height else thickness,
            thickness,
            line_color=rgb_color,
            reverse=state.get('reverse_field', False),
        )
        # For horizontal line (height=0), width spans, thickness is line weight
        if height == 0:
            element.width = width
            element.height = 0
        else:
            element.width = 0
            element.height = height
        label.add_element(element)
        logger.info(f"Added line: {width}x{height} t={thickness} at ({x}, {y})")
    else:
        # Filled when thickness covers half the smaller dimension
        fill = rgb_color if thickness >= min(width, height) / 2 else None
        element = BoxElement(
            x,
            y,
            width,
            height,
            thickness,
            line_color=rgb_color,
            fill_color=fill,
            reverse=state.get('reverse_field', False),
        )
        label.add_element(element)
        logger.info(f"Added box: {width}x{height} t={thickness} at ({x}, {y})")

    state['reverse_field'] = False


def handle_gf(params, state, label):
    """Handle GF (Graphic Field) command."""
    if len(params) < 5:
        logger.warning("Insufficient parameters for GF command")
        return

    format_type, total, total_bytes, bytes_per_row, *data_parts = params
    full_data = ','.join(data_parts)

    bytes_per_row_int = int(bytes_per_row)
    width = bytes_per_row_int * 8
    height = int(total) // bytes_per_row_int

    element = ImageElement(
        state['current_x'],
        state['current_y'],
        width,
        height,
        full_data,
        format_type,
    )
    label.add_element(element)
    logger.info(f"Added image: {width}x{height} at ({state['current_x']}, {state['current_y']})")


def handle_pw(params, state, label):
    """Handle PW (Print Width) command."""
    if params and params[0].strip().isdigit():
        width = int(params[0])
        label.width = width
        state['print_width'] = width


def handle_ll(params, state, label):
    """Handle LL (Label Length) command."""
    if params and params[0].strip().isdigit():
        height = int(params[0])
        label.height = height
        state['label_length'] = height


def register_graphic_commands(registry):
    """Register all graphic-related command handlers."""
    registry.register('GB', handle_gb)
    registry.register('GF', handle_gf)
    registry.register('PW', handle_pw)
    registry.register('LL', handle_ll)
