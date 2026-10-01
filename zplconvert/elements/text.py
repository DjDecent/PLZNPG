import os
from PIL import Image, ImageFont, ImageDraw
from .base import BaseElement


class TextElement(BaseElement):
    """Element for rendering text on labels."""

    def __init__(
        self,
        x,
        y,
        text,
        font_size=12,
        bold=False,
        reverse=False,
        rotation=0,
        origin_mode='FO',
        font_width=None,
        font_name='0',
    ):
        super().__init__(x, y)
        self.text = text
        self.font_size = font_size
        self.font_width = font_width or font_size
        self.font_name = font_name
        self.bold = bold
        self.reverse = reverse
        self.rotation = rotation
        self.origin_mode = origin_mode  # FO = top-left, FT = baseline
        self.font_path = self._get_font_path()
        self._cache = None

    def _get_font_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_name = "RobotoCondensed-Bold.ttf" if self.bold else "RobotoCondensed-Regular.ttf"
        if self.font_name == 'A':
            font_name = 'LiberationMono-Regular.ttf'
        return os.path.join(base_dir, "fonts", font_name)

    def draw(self, draw):
        if not self.text:
            return

        if self._cache is not None:
            paste_x, paste_y, cached = self._cache
            draw._image.paste(cached, (paste_x, paste_y), cached if cached.mode == 'RGBA' else None)
            return

        try:
            # Bitmap font A snaps to integer multiples of its 9-dot cell.
            render_size = max(10, round(self.font_size / 9) * 10) if self.font_name == 'A' else self.font_size
            font = ImageFont.truetype(self.font_path, render_size)
            text_color = (255, 255, 255) if self.reverse else (0, 0, 0)

            bbox = font.getbbox(self.text)
            text_width = max(1, bbox[2] - bbox[0])
            text_height = max(1, bbox[3] - bbox[1])
            padding = 2

            # Render text onto a transparent image, then rotate if needed
            temp_img = Image.new(
                'RGBA',
                (text_width + padding * 2, text_height + padding * 2),
                (0, 0, 0, 0),
            )
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text(
                (padding - bbox[0], padding - bbox[1]),
                self.text,
                font=font,
                fill=text_color + (255,),
            )

            if self.font_name == '0' and self.font_width != self.font_size:
                temp_img = temp_img.resize((max(1, round(temp_img.width * self.font_width / self.font_size)), temp_img.height), Image.Resampling.NEAREST)

            if self.rotation == 90:
                rotated = temp_img.rotate(270, expand=True, resample=Image.NEAREST)
            elif self.rotation == 180:
                rotated = temp_img.rotate(180, expand=True, resample=Image.NEAREST)
            elif self.rotation == 270:
                rotated = temp_img.rotate(90, expand=True, resample=Image.NEAREST)
            else:
                rotated = temp_img

            # Positioning: FO = top-left of text box; FT = baseline (bottom of unrotated text)
            if self.origin_mode == 'FT' and self.rotation == 0:
                paste_x = self.x
                paste_y = self.y - rotated.height + padding
            elif self.rotation == 90:
                # Zebra R: text reads bottom-to-top along increasing Y from origin
                paste_x = self.x + round(self.font_size * 0.2) - padding
                paste_y = self.y - padding
            else:
                paste_x = self.x - padding
                paste_y = self.y - padding

            draw._image.paste(rotated, (paste_x, paste_y), rotated)
            self._cache = (paste_x, paste_y, rotated)
        except Exception:
            import traceback
            traceback.print_exc()
