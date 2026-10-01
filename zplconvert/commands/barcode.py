"""Barcode-related ZPL command handlers."""

from ..elements.barcode import BarcodeElement
from ..elements.text import TextElement
from ..elements.qrcode import QRCodeElement


def handle_bq(params, state, label):
    """Configure a model 2 QR field without changing the ^BY defaults."""
    def value(index, default):
        return params[index].strip() if len(params) > index and params[index].strip() else default

    if value(1, '2') != '2':
        raise ValueError('Only QR model 2 is supported')
    state['expecting_barcode'] = True
    state['barcode_type'] = 'qrcode'
    state['qr_magnification'] = max(1, min(100, int(value(2, str(max(1, round(label.dpi / 100)))))))
    state['qr_error_correction'] = value(3, 'Q').upper()
    state['qr_mask'] = int(value(4, '-1'))
    if not -1 <= state['qr_mask'] <= 7:
        raise ValueError('QR mask must be between 0 and 7')


def handle_bc(params, state, label):
    """Handle BC (Barcode Code 128) command.

    ^BCo,h,f,g,e,m
    """
    state['expecting_barcode'] = True
    state['barcode_type'] = 'code128'

    # Orientation may be glued to command as BCN → params[0] is height, or first param is orientation
    height = state.get('module_height', state.get('barcode_height', 100))

    # params after stripping orientation from command text arrive as: orientation?, height, ...
    # Parser keeps orientation in params[0] when command is BCN,...
    idx = 1
    state['barcode_orientation'] = 'N'
    if params and params[0].strip() and params[0].strip().upper() in ('N', 'R', 'I', 'B'):
        state['barcode_orientation'] = params[0].strip().upper()
        idx = 1

    if len(params) > idx and params[idx].strip().isdigit():
        height = int(params[idx])

    state['barcode_height'] = height
    state['barcode_print_text'] = not (len(params) > 2 and params[2].strip().upper() == 'N')
    state['barcode_text_above'] = len(params) > 3 and params[3].strip().upper() == 'Y'
    state['barcode_mode'] = params[5].strip().upper() if len(params) > 5 else 'N'


def handle_bx(params, state, label):
    """Handle BX (Barcode DataMatrix) command.

    ^BXo,h,s,c,r,f,g
    h = individual module size in dots
    s = quality / ECC level
    """
    state['expecting_barcode'] = True
    state['barcode_type'] = 'datamatrix'

    idx = 1
    state['barcode_orientation'] = 'N'
    if params and params[0].strip() and params[0].strip().upper() in ('N', 'R', 'I', 'B', ''):
        if params[0].strip():
            state['barcode_orientation'] = params[0].strip().upper()
        idx = 1

    module_size = 10
    quality = 200

    if len(params) > idx and params[idx].strip().isdigit():
        module_size = int(params[idx])
    if len(params) > idx + 1 and params[idx + 1].strip().isdigit():
        quality = int(params[idx + 1])

    state['barcode_module_size'] = module_size
    state['barcode_quality'] = quality
    state['barcode_height'] = module_size  # used as module size downstream


def handle_fd_barcode(params, state, label):
    """Handle FD (Field Data) command for barcodes."""
    data = params[0] if params else "SAMPLE"
    barcode_type = state.get('barcode_type', 'code128')

    if barcode_type == 'qrcode':
        label.add_element(QRCodeElement(
            state['current_x'], state['current_y'], data,
            magnification=state['qr_magnification'],
            error_correction=state['qr_error_correction'],
            mask=state['qr_mask'], origin_mode=state.get('origin_mode', 'FO'),
            origin_offset=state.get('module_height', 10),
        ))
        state['expecting_barcode'] = False
        return

    if barcode_type == 'datamatrix':
        module_width = state.get('barcode_module_size', state.get('module_width', 5))
        height = module_width
        width = module_width
    else:
        module_width = state.get('module_width', 2)
        height = state.get('barcode_height', 100)
        width = state.get('barcode_width', 300)

    try:
        barcode_element = BarcodeElement(
            state['current_x'],
            state['current_y'],
            data,
            width=max(width, 1),
            height=max(height, 1),
            barcode_type=barcode_type,
            quality=state.get('barcode_quality', 200),
            module_width=module_width,
            origin_mode=state.get('origin_mode', 'FO'),
            print_text=state.get('barcode_print_text', True),
            text_above=state.get('barcode_text_above', False),
            mode=state.get('barcode_mode', 'N'),
            orientation=state.get('barcode_orientation', 'N'),
        )
        label.add_element(barcode_element)
    except Exception:
        label.add_element(
            TextElement(
                state['current_x'],
                state['current_y'],
                f"[Barcode: {data}]",
                font_size=12,
            )
        )

    state['expecting_barcode'] = False


def handle_by(params, state, label):
    """Handle BY (Barcode Defaults) command.

    ^BYw,r,h — module width, wide/narrow ratio, height
    """
    state['module_width'] = 2
    state['barcode_width_ratio'] = 3.0
    state['barcode_height'] = 100

    if not params:
        return

    try:
        if params[0].strip().isdigit():
            state['module_width'] = int(params[0])
        if len(params) > 1 and params[1].replace('.', '', 1).isdigit():
            state['barcode_width_ratio'] = float(params[1])
        if len(params) > 2 and params[2].strip().isdigit():
            state['barcode_height'] = int(params[2])
            state['module_height'] = int(params[2])
    except (ValueError, IndexError):
        pass


def register_barcode_commands(registry):
    """Register all barcode-related command handlers."""
    registry.register('BC', handle_bc)
    registry.register('BX', handle_bx)
    registry.register('BQ', handle_bq)
    registry.register('BY', handle_by)
    registry.register('FD_BARCODE', handle_fd_barcode)
