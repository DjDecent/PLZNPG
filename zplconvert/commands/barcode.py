"""Barcode-related ZPL command handlers."""

from ..elements.barcode import BarcodeElement
from ..elements.text import TextElement

def handle_bc(params, state, label):
    """Handle BC (Barcode Code 128) command."""
    state['expecting_barcode'] = True
    state['barcode_type'] = 'code128'
    
    # Set default values that work even with empty params
    state['barcode_height'] = 100  # Default height
    state['barcode_width'] = 300  # Default width
    
    if params and len(params) > 0:
        # Parse parameters if available
        if len(params) > 1 and params[1].strip().isdigit():
            state['barcode_height'] = int(params[1])

def handle_bx(params, state, label):
    """Handle BX (Barcode DataMatrix) command."""
    state['expecting_barcode'] = True
    state['barcode_type'] = 'datamatrix'
    
    # Set default values
    state['barcode_height'] = 100
    state['barcode_width'] = 100
    state['barcode_quality'] = 200
    
    if len(params) >= 5:
        if params[1] and params[1].strip().isdigit():
            state['barcode_height'] = int(params[1])
        if params[3] and params[3].strip().isdigit():
            state['barcode_width'] = int(params[3])
        if params[4] and params[4].strip().isdigit():
            state['barcode_quality'] = int(params[4])

def handle_fd_barcode(params, state, label):
    """Handle FD (Field Data) command for barcodes."""
    if not params:
        # Create a placeholder barcode with dummy data if no data provided
        data = "SAMPLE"
    else:
        data = params[0]  # The entire field data
    
    # Always ensure we have reasonable dimensions
    if state['barcode_type'] == 'datamatrix':
        width = state.get('barcode_width', 100)
        height = state.get('barcode_height', 100)
    else:  # code128
        width = state.get('barcode_width', 300)
        height = state.get('barcode_height', 100)
    
    # Ensure width and height are at least 1 pixel
    width = max(width, 20)
    height = max(height, 20)
    
    try:
        barcode_element = BarcodeElement(
            state['current_x'],
            state['current_y'],
            data,
            width=width,
            height=height,
            barcode_type=state['barcode_type'],
            quality=state.get('barcode_quality', 200)
        )
        
        label.add_element(barcode_element)
    except Exception as e:
        # Add a fallback text element to show there was an error
        label.add_element(TextElement(
            state['current_x'],
            state['current_y'],
            f"[Barcode: {data}]",
            font_size=12
        ))
    
    # Reset barcode state regardless of success or failure
    state['expecting_barcode'] = False

def handle_by(params, state, label):
    """Handle BY (Barcode Defaults) command."""
    # Always set default values first
    state['barcode_width'] = 300
    state['barcode_width_ratio'] = 3.0
    state['barcode_height'] = 100
    
    if params and len(params) >= 3:
        try:
            # Module width in dots (1-10)
            module_width = int(params[0]) if params[0].strip().isdigit() else 2
            
            # Width ratio between wide and narrow bars (2.0-3.0)
            width_ratio = float(params[1]) if params[1].replace('.', '', 1).isdigit() else 3.0
            
            # Barcode height in dots
            barcode_height = int(params[2]) if params[2].strip().isdigit() else 10
            
            # Width calculation more directly based on the spec
            barcode_width = 300  # Reasonable width
            
            state['barcode_width'] = barcode_width
            state['barcode_width_ratio'] = width_ratio
            state['barcode_height'] = barcode_height
        except (ValueError, IndexError) as e:
            pass

def register_barcode_commands(registry):
    """Register all barcode-related command handlers."""
    registry.register('BC', handle_bc)
    registry.register('BX', handle_bx)
    registry.register('BY', handle_by)
    # Add an additional handler for FD command when in barcode mode
    registry.register('FD_BARCODE', handle_fd_barcode)
