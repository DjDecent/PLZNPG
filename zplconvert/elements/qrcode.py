"""QR model 2 fields, rendered directly at integer module sizes."""

from PIL import Image, ImageDraw
from qrcodegen import QrCode, QrSegment
from .base import BaseElement


class QRCodeElement(BaseElement):
    def __init__(self, x, y, data, magnification=2, error_correction='Q',
                 mask=-1, origin_mode='FO', origin_offset=10):
        super().__init__(x, y)
        self.magnification = magnification
        self.origin_mode = origin_mode
        self.origin_offset = origin_offset
        levels = {'L': QrCode.Ecc.LOW, 'M': QrCode.Ecc.MEDIUM,
                  'Q': QrCode.Ecc.QUARTILE, 'H': QrCode.Ecc.HIGH}
        # Consume two switch characters, including a blank prefix.
        # Preserve payload whitespace.
        level = levels.get(data[:1], levels.get(error_correction, QrCode.Ecc.MEDIUM))
        self.payload = data[2:]
        if self.payload.startswith(','):
            self.payload = self.payload[1:]
        if data[1:2] == 'M':
            mode, payload = self.payload[:1], self.payload[1:]
            if mode == 'N':
                segments = [QrSegment.make_numeric(payload)]
            elif mode == 'A':
                segments = [QrSegment.make_alphanumeric(payload)]
            elif mode == 'B' and payload[:4].isdigit():
                count = int(payload[:4])
                raw = payload[4:].encode('utf-8')
                if len(raw) != count:
                    raise ValueError('QR manual byte count does not match payload length')
                segments = [QrSegment.make_bytes(raw)]
            else:
                raise ValueError('Unsupported QR manual character mode')
        else:
            segments = QrSegment.make_segments(self.payload)
        self.symbol = QrCode.encode_segments(segments, level, mask=mask)

    def draw(self, draw):
        module = self.magnification
        size = self.symbol.get_size() * module
        ink = Image.new('L', (size, size), 0)
        painter = ImageDraw.Draw(ink)
        for y in range(self.symbol.get_size()):
            for x in range(self.symbol.get_size()):
                if self.symbol.get_module(x, y):
                    painter.rectangle((x*module, y*module, (x+1)*module-1,
                                       (y+1)*module-1), fill=255)
        top = self.y - size if self.origin_mode == 'FT' else self.y + self.origin_offset
        draw._image.paste('black', (self.x, top, self.x+size, top+size), ink)
