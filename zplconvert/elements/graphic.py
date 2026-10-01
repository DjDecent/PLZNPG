"""Graphic element classes for ZPL conversion."""

import os
from PIL import Image, ImageChops, ImageDraw
from .base import BaseElement


class LineElement(BaseElement):
    """Element for rendering lines on labels."""

    def __init__(self, x, y, width, height, thickness=1, line_color=(0, 0, 0), reverse=False):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.thickness = max(1, thickness)
        self.line_color = line_color
        self.reverse = reverse

    def draw(self, draw):
        line_color = self.line_color
        if self.reverse:
            line_color = (255, 255, 255) if self.line_color == (0, 0, 0) else (0, 0, 0)

        if self.width >= self.height:
            # Horizontal line: thickness grows downward from y
            y1 = self.y + self.thickness - 1
            draw.rectangle(
                [self.x, self.y, self.x + max(self.width, 1) - 1, y1],
                fill=line_color,
            )
        else:
            # Vertical line: thickness grows rightward from x
            x1 = self.x + self.thickness - 1
            draw.rectangle(
                [self.x, self.y, x1, self.y + max(self.height, 1) - 1],
                fill=line_color,
            )

    def __str__(self):
        return (
            f"LineElement(x={self.x}, y={self.y}, width={self.width}, "
            f"height={self.height}, thickness={self.thickness})"
        )


class BoxElement(BaseElement):
    """Element for rendering boxes on labels."""

    def __init__(
        self,
        x,
        y,
        width,
        height,
        thickness=1,
        line_color=(0, 0, 0),
        fill_color=None,
        reverse=False,
    ):
        super().__init__(x, y)
        self.width = max(width, 1)
        self.height = max(height, 1)
        self.thickness = max(0, thickness)
        self.line_color = line_color
        self.fill_color = fill_color
        self.reverse = reverse

    def draw(self, draw):
        try:
            if self.reverse:
                mask = Image.new('RGB', draw._image.size, 'white')
                normal = BoxElement(self.x, self.y, self.width, self.height,
                                    self.thickness, self.line_color, self.fill_color)
                normal.draw(ImageDraw.Draw(mask))
                draw._image.paste(ImageChops.difference(draw._image, ImageChops.invert(mask)))
                return
            line_color = self.line_color
            fill_color = self.fill_color

            if self.reverse:
                line_color, fill_color = (fill_color or (255, 255, 255)), line_color

            x0, y0 = self.x, self.y
            x1, y1 = self.x + self.width - 1, self.y + self.height - 1

            # Zebra fills the box when thickness covers half the smaller side
            filled = fill_color is not None or self.thickness >= min(self.width, self.height) / 2

            if filled:
                draw.rectangle([x0, y0, x1, y1], fill=line_color if fill_color is None else fill_color)
                return

            if fill_color is not None:
                draw.rectangle([x0, y0, x1, y1], fill=fill_color)

            t = min(self.thickness, self.width // 2, self.height // 2)
            if t <= 0:
                return

            # Draw border as four filled rectangles for reliable thickness
            draw.rectangle([x0, y0, x1, y0 + t - 1], fill=line_color)  # top
            draw.rectangle([x0, y1 - t + 1, x1, y1], fill=line_color)  # bottom
            draw.rectangle([x0, y0, x0 + t - 1, y1], fill=line_color)  # left
            draw.rectangle([x1 - t + 1, y0, x1, y1], fill=line_color)  # right
        except Exception:
            import traceback
            traceback.print_exc()

    def __str__(self):
        return (
            f"BoxElement(x={self.x}, y={self.y}, width={self.width}, "
            f"height={self.height}, thickness={self.thickness})"
        )

    def __repr__(self):
        return self.__str__()


class LogoElement(BaseElement):
    """Element for rendering logo images on labels."""

    def __init__(self, x, y, image_path, width=None, height=None):
        super().__init__(x, y)
        self.image_path = image_path
        self.width = width if width is not None else 100
        self.height = height if height is not None else 100

    def draw(self, draw):
        try:
            if os.path.exists(self.image_path):
                logo = Image.open(self.image_path)
                logo = logo.resize((self.width, self.height))
                draw._image.paste(logo, (self.x, self.y))
            else:
                draw.rectangle(
                    [self.x, self.y, self.x + self.width, self.y + self.height],
                    outline="black",
                )
                draw.text((self.x + 5, self.y + self.height // 2), "Logo", fill="black")
        except Exception:
            draw.rectangle(
                [self.x, self.y, self.x + self.width, self.y + self.height],
                outline="red",
            )
            draw.text((self.x + 5, self.y + self.height // 2), "Error", fill="red")


class ImageElement(BaseElement):
    """Element for rendering bitmap images on labels."""

    def __init__(self, x, y, width, height, image_data, format='A'):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.image_data = image_data
        self.format = format
        self.widthBytes = (width + 7) // 8
        self.total = self.widthBytes * height
        self.mapCode = self.initialize_map_code()
        self._cache = None

    @staticmethod
    def initialize_map_code():
        map_code = {}
        for i in range(1, 20):
            map_code[i] = chr(ord('G') + i - 1)
        for i in range(20, 401, 20):
            map_code[i] = chr(ord('g') + (i // 20) - 1)
        return map_code

    def gfa_to_image(self):
        hex_data = self.ascii_to_hex(self.image_data)
        binary_data = self.hex_to_binary(hex_data)
        image = Image.new('1', (self.width, self.height), 1)
        pixels = image.load()

        for y in range(self.height):
            for x in range(self.width):
                byte_index = (y * self.widthBytes) + (x // 8)
                bit_index = 7 - (x % 8)
                if byte_index < len(binary_data):
                    pixel = (binary_data[byte_index] >> bit_index) & 1
                    pixels[x, y] = 0 if pixel else 255  # 1 = black in ZPL

        return image

    def ascii_to_hex(self, ascii_data):
        hex_lines = []
        current_line = ""
        previous_line = ""
        reverse_values = {v: k for k, v in self.mapCode.items()}
        count = 0
        row_length = self.widthBytes * 2
        for char in ascii_data:
            if char in '0123456789ABCDEF':
                current_line += char * (count or 1)
                count = 0
            elif char in reverse_values:
                count += reverse_values[char]
            elif char in ',!':
                current_line = current_line.ljust(row_length, '0' if char == ',' else 'F')
                count = 0
            elif char == ':':
                if previous_line:
                    hex_lines.append(previous_line)
            while len(current_line) >= row_length:
                previous_line = current_line[:row_length]
                hex_lines.append(previous_line)
                current_line = current_line[row_length:]

        if current_line:
            padded_line = self.pad_line(current_line)
            if padded_line:
                hex_lines.append(padded_line)

        return '\n'.join(hex_lines)

    def pad_line(self, line):
        full_line_length = self.widthBytes * 2
        if len(line) > full_line_length:
            return line[:full_line_length]
        if len(line) < full_line_length:
            return line.ljust(full_line_length, '0')
        return line

    def hex_to_binary(self, hex_data):
        binary_data = bytearray()
        for line in hex_data.split('\n'):
            for i in range(0, len(line), 2):
                if i + 1 < len(line):
                    binary_data.append(int(line[i:i + 2], 16))
                else:
                    binary_data.append(int(line[i] + '0', 16))
        return binary_data

    def draw(self, draw):
        if self._cache is not None:
            draw._image.paste(self._cache, (self.x, self.y))
            return

        if self.format == 'A':
            try:
                image = self.gfa_to_image().convert('RGB')
                draw._image.paste(image, (self.x, self.y))
                self._cache = image
            except Exception:
                import traceback
                traceback.print_exc()
