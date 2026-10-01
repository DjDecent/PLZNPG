"""Render Code 128 and ECC 200 at integer printer-dot dimensions."""
import re
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from pystrich.code128.textencoder import TextEncoder
from pystrich.datamatrix import DataMatrixEncoder, FNC1, DataMatrixData
from .base import BaseElement


class BarcodeElement(BaseElement):
    def __init__(self, x, y, data, width=300, height=100, barcode_type='code128',
                 quality=200, width_ratio=3.0, module_width=2, origin_mode='FO',
                 print_text=True, text_above=False, mode='N', orientation='N'):
        super().__init__(x, y)
        self.data, self.width, self.height = data, width, height
        self.barcode_type, self.quality = barcode_type, quality
        self.module_width = max(1, module_width)
        self.origin_mode = origin_mode
        self.print_text, self.text_above = print_text, text_above
        self.mode, self.orientation = mode, orientation

    def _codewords(self):
        # ZPL defaults to subset B. Invocation codes explicitly select a subset.
        data = self.data
        subset = 'B'
        codes = [104]
        starts = {'9': ('A', 103), ':': ('B', 104), ';': ('C', 105)}
        if data[:1] == '>' and data[1:2] in starts:
            subset, start = starts[data[1]]
            codes, data = [start], data[2:]
        i = 0
        while i < len(data):
            if data[i:i+1] == '>' and i + 1 < len(data):
                invocation = data[i+1]
                if invocation in starts:
                    # Start invocations inside a field do not encode another start.
                    i += 2
                    continue
                if invocation == '8':
                    codes.append(102)
                    i += 2
                    continue
                if invocation in '567':
                    subset, code = {'5': ('C', 99), '6': ('B', 100), '7': ('A', 101)}[invocation]
                    codes.append(code)
                    i += 2
                    continue
            if self.mode == 'A':
                match = re.match(r'[0-9]+', data[i:])
                run = len(match[0]) if match else 0
                if subset != 'C' and run >= 4 and run % 2 == 0:
                    if i == 0:
                        codes[0] = 105
                    else:
                        codes.append(99)
                    subset = 'C'
                elif subset == 'C' and run < 2:
                    codes.append(100)
                    subset = 'B'
            if subset == 'C':
                pair = data[i:i+2]
                if len(pair) == 2 and pair.isascii() and pair.isdigit():
                    codes.append(int(pair))
                    i += 2
                else:
                    i += 1
            else:
                value = ord(data[i])
                codes.append(value - 32 if value >= 32 else value + 64)
                i += 1
        return codes

    def _generate_code_128(self):
        codes = self._codewords()
        checksum = (codes[0] + sum(i*c for i,c in enumerate(codes[1:], 1))) % 103
        bars = TextEncoder.get_bars(codes, checksum)
        image = Image.new('RGB', (len(bars)*self.module_width, self.height), 'white')
        draw = ImageDraw.Draw(image)
        for i, bit in enumerate(bars):
            if bit == '1':
                draw.rectangle((i*self.module_width, 0, (i+1)*self.module_width-1, self.height-1), fill='black')
        return image

    def _generate_datamatrix(self):
        parts = self.data.split('_1')
        payload = DataMatrixData(parts[0], encoding='ascii')
        for part in parts[1:]:
            payload = payload + FNC1 + part
        encoder = DataMatrixEncoder(payload, quiet_zone=0)
        image = Image.open(BytesIO(encoder.get_imagedata())).convert('RGB')
        # Renderer defaults to 5 pixels/module. No quiet zone belongs in FO/FT.
        return image.resize((image.width // 5 * self.module_width,
                             image.height // 5 * self.module_width), Image.Resampling.NEAREST)

    def draw(self, draw):
        image = self._generate_datamatrix() if self.barcode_type == 'datamatrix' else self._generate_code_128()
        if self.barcode_type != 'datamatrix' and self.print_text:
            text = re.sub(r'>.', '', self.data)
            font = ImageFont.truetype(str(Path(__file__).resolve().parents[2] / 'fonts/LiberationMono-Regular.ttf'), 10 * self.module_width)
            bbox = font.getbbox(text)
            caption_height = bbox[3] - bbox[1]
            combined = Image.new('RGB', (image.width, image.height + caption_height + 12), 'white')
            bar_y = caption_height + 12 if self.text_above else 0
            combined.paste(image, (0, bar_y))
            caption_y = 0 if self.text_above else image.height + 5
            ImageDraw.Draw(combined).text(((image.width-font.getlength(text))/2, caption_y-bbox[1]), text, font=font, fill='black')
            image = combined
        rotation = {'N': 0, 'R': 270, 'I': 180, 'B': 90}[self.orientation]
        image = image.rotate(rotation, expand=True)
        y = self.y - (self.height if self.barcode_type != 'datamatrix' else image.height) if self.origin_mode == 'FT' else self.y
        # Paste only ink; white modules must not erase earlier fields.
        mask = image.convert('L').point(lambda value: 255-value)
        draw._image.paste('black', (self.x, y, self.x+image.width, y+image.height), mask)
