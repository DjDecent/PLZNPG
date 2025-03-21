"""Graphic-related ZPL command handlers."""

from ..elements.graphic import BoxElement, ImageElement, LineElement

def handle_gb(params, state, label):
    """Handle GB (Graphic Box) command."""
    if len(params) < 3:
        print("Insufficient parameters for GB command")
        return
        
    width, height, thickness = map(int, params[:3])
    
    # Default color is Black
    color = 'B'
    if len(params) >= 4:
        color = params[3].upper()
        
    # Default rounding is 0
    rounding = 0
    if len(params) >= 5:
        rounding = int(params[4])
    
    # Convert color to RGB
    rgb_color = (0, 0, 0) if color == 'B' else (255, 255, 255)
    
    # Create and add the box element
    element = BoxElement(
        state['current_x'],
        state['current_y'],
        width,
        height,
        thickness,
        line_color=rgb_color,
        fill_color=rgb_color if thickness == 0 else None,
        reverse=state['reverse_field']
    )
    label.add_element(element)
    print(f"Added box: {width}x{height} at ({state['current_x']}, {state['current_y']})")
    
    # Turn off reverse field after use
    state['reverse_field'] = False

def handle_gf(params, state, label):
    """Handle GF (Graphic Field) command."""
    if len(params) < 5:
        print("Insufficient parameters for GF command")
        return
        
    format_type, total, total_bytes, bytes_per_row, *data_parts = params
    
    # Join all parts to get the full data
    full_data = ','.join(data_parts)
    
    # Calculate image dimensions
    bytes_per_row_int = int(bytes_per_row)
    width = bytes_per_row_int * 8
    height = int(total) // bytes_per_row_int
    
    # Create and add the image element
    element = ImageElement(
        state['current_x'],
        state['current_y'],
        width,
        height,
        full_data,
        format_type
    )
    label.add_element(element)
    print(f"Added image: {width}x{height} at ({state['current_x']}, {state['current_y']})")

def register_graphic_commands(registry):
    """Register all graphic-related command handlers."""
    registry.register('GB', handle_gb)
    registry.register('GF', handle_gf)
