"""Field-block layout, measured using the same font as the text renderer."""

import re
from PIL import Image, ImageDraw, ImageFont
from .text import TextElement


class FieldBlockElement(TextElement):
    def __init__(self, *args, block, **kwargs):
        super().__init__(*args, **kwargs)
        self.block = dict(block)

    def layout(self):
        """Return (text, x, y) runs in unrotated block coordinates."""
        width = self.block['width']
        if width < self.font_width:
            return []
        size = max(10, round(self.font_size / 9) * 10) if self.font_name == 'A' else self.font_size
        font = ImageFont.truetype(self.font_path, size)
        scale = self.font_width / self.font_size if self.font_name == '0' else 1
        measure = lambda value: font.getlength(value) * scale
        # ZPL discards formatting newlines; explicit \& starts a new line.
        paragraphs = self.text.replace('\r', '').replace('\n', '').split('\\&')
        lines = []
        indent = self.block['indent']
        for paragraph in paragraphs:
            words = re.findall(r'\S+', paragraph)
            line = ''
            while words:
                available = width - (indent if lines else 0)
                if available < self.font_width:
                    break
                word = words.pop(0)
                candidate = line + (' ' if line else '') + word
                if measure(candidate) <= available:
                    line = candidate
                    continue
                if line:
                    lines.append(line)
                    line = ''
                    words.insert(0, word)
                    continue
                cut = 1
                while cut < len(word) and measure(word[:cut+1] + '-') <= available:
                    cut += 1
                lines.append(word[:cut] + ('-' if cut < len(word) else ''))
                if cut < len(word):
                    words.insert(0, word[cut:])
            lines.append(line)

        runs = []
        step = self.font_size + self.block['line_spacing']
        for index, line in enumerate(lines):
            left = indent if index else 0
            available = width - left
            # Include a terminal word space when measuring block justification.
            occupied = measure(line + ' ')
            alignment = self.block['alignment']
            x = left
            if alignment == 'C':
                x += (available - occupied) / 2
            elif alignment == 'R':
                x += available - occupied
            y = min(index, self.block['max_lines'] - 1) * step
            words = line.split(' ')
            if alignment == 'J' and index < len(lines) - 1 and len(words) > 1:
                gap = (available - sum(measure(word) for word in words)) / (len(words)-1)
                for word in words:
                    runs.append((word, round(x), y))
                    x += measure(word) + gap
            elif line:
                runs.append((line, round(x), y))
        return runs

    def draw(self, draw):
        runs = self.layout()
        if not runs:
            return
        top = self.y
        if self.origin_mode == 'FT':
            top -= (self.block['max_lines'] - 1) * (self.font_size + self.block['line_spacing'])
        if self.rotation:
            height = max(y for _, _, y in runs) + self.font_size * 2
            surface = Image.new('RGBA', (self.block['width'], max(1, height)), (0, 0, 0, 0))
            target = ImageDraw.Draw(surface)
        else:
            target = draw
        for text, x, y in runs:
            element = TextElement(
                x if self.rotation else self.x+x,
                y if self.rotation else top+y,
                text, self.font_size, self.bold, self.reverse,
                origin_mode='FO' if self.rotation else self.origin_mode,
                font_width=self.font_width, font_name=self.font_name,
            )
            element.draw(target)
        if self.rotation:
            surface = surface.rotate(-self.rotation, expand=True)
            draw._image.paste(surface, (self.x, top), surface)
