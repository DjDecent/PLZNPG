import os
import math
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageColor, ImageFilter
from barcode import Code128
from barcode.writer import ImageWriter
from barcode.charsets import code128
from pystrich.code128 import Code128Encoder
from pystrich.datamatrix import DataMatrixEncoder

class Text:
    def __init__(self, x, y, text, font_size=12, font=None):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.font = font if font else ImageFont.load_default()

    def draw(self, draw: ImageDraw.Draw):
        draw.text((self.x, self.y), self.text, font=self.font, fill="black")

class Barcode:
    def __init__(self, x, y, data, barcode_type='code128'):
        self.x = x
        self.y = y
        self.data = data
        self.barcode_type = barcode_type

    def draw(self, draw):
        # Placeholder for barcode drawing logic
        draw.rectangle([self.x, self.y, self.x + 100, self.y + 50], outline="black")
        draw.text((self.x, self.y + 60), f"Barcode: {self.data}", fill="black")

class BaseElement:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def draw(self, draw):
        pass

"""Text element classes for ZPL conversion."""

import os
from PIL import Image, ImageFont, ImageDraw
from .base import BaseElement

class TextElement(BaseElement):
    """Element for rendering text on labels."""
    
    def __init__(self, x, y, text, font_size=12, bold=False, reverse=False, rotation=0):
        super().__init__(x, y)
        self.text = text
        self.font_size = font_size
        self.bold = bold
        self.reverse = reverse
        self.rotation = rotation
        self.font_path = self._get_font_path()

    def _get_font_path(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_name = "RobotoCondensed-Bold.ttf" if self.bold else "RobotoCondensed-Regular.ttf"
        font_path = os.path.join(base_dir, "fonts", font_name)
        return font_path

    def draw(self, draw):
        try:
            font = ImageFont.truetype(self.font_path, self.font_size)
            text_color = (255, 255, 255) if self.reverse else (0, 0, 0)
            
            # Get text dimensions using textbbox
            bbox = draw.textbbox((0, 0), self.text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Draw according to rotation
            if self.rotation == 0:
                # Standard orientation
                draw.text((self.x, self.y), self.text, font=font, fill=text_color, anchor="lt")
            
            elif self.rotation == 90:
                # Rotate 90 degrees (clockwise)
                temp_img = Image.new('RGBA', (text_height + 10, text_width + 10), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                              font=font, fill=text_color, anchor="mm")
                rotated = temp_img.rotate(90, expand=True, resample=Image.BICUBIC)
                draw._image.paste(rotated, (self.x, self.y), rotated)
            
            elif self.rotation == 180:
                # Rotate 180 degrees
                temp_img = Image.new('RGBA', (text_width + 10, text_height + 10), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                              font=font, fill=text_color, anchor="mm")
                rotated = temp_img.rotate(180, expand=True, resample=Image.BICUBIC)
                draw._image.paste(rotated, (self.x - 5, self.y - 5), rotated)
            
            elif self.rotation == 270:
                # Rotate 270 degrees (counter-clockwise)
                temp_img = Image.new('RGBA', (text_height + 10, text_width + 10), (255, 255, 255, 0))
                temp_draw = ImageDraw.Draw(temp_img)
                temp_draw.text((temp_img.width // 2, temp_img.height // 2), self.text, 
                              font=font, fill=text_color, anchor="mm")
                rotated = temp_img.rotate(270, expand=True, resample=Image.BICUBIC)
                draw._image.paste(rotated, (self.x - text_height, self.y), rotated)
            
            print(f"Drew text: '{self.text}' at ({self.x}, {self.y}) with rotation {self.rotation}°")
                
        except Exception as e:
            print(f"Error drawing TextElement: {str(e)}")
            import traceback
            traceback.print_exc()

class LineElement(BaseElement):
    def __init__(self, x, y, width, height, thickness, line_color, reverse=False):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.thickness = thickness
        self.line_color = line_color
        self.reverse = reverse  # Add reverse attribute

    def draw(self, draw):
        # Apply reverse effect to line color if needed
        line_color = self.line_color
        if self.reverse:
            line_color = (255, 255, 255) if self.line_color == (0, 0, 0) else (0, 0, 0)

        if self.width > self.height:
            # Horizontal line
            for i in range(self.thickness):
                draw.line([(self.x, self.y + i), (self.x + self.width - 1, self.y + i)], fill=line_color)
        else:
            # Vertical line
            for i in range(self.thickness):
                draw.line([(self.x + i, self.y), (self.x + i, self.y + self.height - 1)], fill=line_color)

    def __str__(self):
        return f"LineElement(x={self.x}, y={self.y}, width={self.width}, height={self.height}, thickness={self.thickness}, line_color={self.line_color}, reverse={self.reverse})"

class BoxElement(BaseElement):
    def __init__(self, x, y, width, height, thickness=1, line_color=(0, 0, 0), fill_color=None, reverse=False):
        super().__init__(x, y)
        self.width = max(width, 1)  # Ensure minimum width of 1
        self.height = max(height, 1)  # Ensure minimum height of 1
        self.thickness = thickness
        self.line_color = line_color
        self.fill_color = fill_color
        self.reverse = reverse

    def draw(self, draw):
        try:
            if self.reverse:
                temp = self.line_color
                self.line_color = self.fill_color or (255, 255, 255)
                self.fill_color = temp

            if self.fill_color:
                draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], fill=self.fill_color)

            for i in range(self.thickness):
                draw.rectangle([self.x + i, self.y + i, self.x + self.width - i, self.y + self.height - i], outline=self.line_color)

            print(f"Drew BoxElement: {self}")
        except Exception as e:
            print(f"Error drawing BoxElement: {str(e)}")

    def __str__(self):
        return f"BoxElement(x={self.x}, y={self.y}, width={self.width}, height={self.height}, thickness={self.thickness}, line_color={self.line_color}, fill_color={self.fill_color}, reverse={self.reverse})"

    def __repr__(self):
        return self.__str__()

class BarcodeElement(BaseElement):
    def __init__(self, x, y, data, width, height, barcode_type='code128', quality=200):
        super().__init__(x, y)
        self.data = data
        self.width = width
        self.height = height
        self.barcode_type = barcode_type
        self.quality = quality

    # Define a set of known GS1 Application Identifiers
    GS1_AIS = {
        '00', '01', '02', '10', '11', '12', '13', '15', '17', '20', 
        '21', '22', '240', '241', '242', '250', '251', '253', '254', '255',
        '30', '310', '311', '312', '313', '314', '315', '316', '320', '321', '322', '323', '324', '325', '326', '327', '328', '329',
        '330', '331', '332', '333', '334', '335', '336', '337', '340', '341', '342', '343', '344', '345', '346', '347', '348', '349',
        '350', '351', '352', '353', '354', '355', '356', '357', '360', '361', '362', '363', '364', '365', '366', '367', '368', '369',
        '37', '390', '391', '392', '393', '394', '395', '400', '401', '402', '403',
        '410', '411', '412', '413', '414', '415', '416', '417', '420', '421', '422', '423', '424', '425', '426', '427',
        '7001', '7002', '7003', '7004', '7005', '7006', '7007', '7008', '7009', '7010',
        '7020', '7021', '7022', '7023', '7030', '7031', '7032', '7033', '7034', '7035', '7036', '7037', '7038', '7039',
        '710', '711', '712', '713', '714', '715', '723',
        '8001', '8002', '8003', '8004', '8005', '8006', '8007', '8008', '8009', '8010', '8011', '8012', '8013', '8017', '8018', '8019',
        '8020', '8026', '8110', '8111', '8112', '8200',
        '90', '91', '92', '93', '94', '95', '96', '97', '98', '99'
    }

    def _format_gs1_128_data(self, data):
        # Remove start and stop characters if present
        if data.startswith('>;') and data.endswith('>;'):
            data = data[2:-2]
        
        parts = data.split('>8')  # Split by the GS character
        formatted_parts = []
        for part in parts:
            # Split each part by '>; ' in case there are multiple AIs within a GS section
            subparts = part.split('>;')
            for subpart in subparts:
                if subpart.startswith(';'):
                    # Remove the leading semicolon
                    subpart = subpart[1:]
                    # Find the longest matching AI
                    ai = next((ai for ai in sorted(self.GS1_AIS, key=len, reverse=True) if subpart.startswith(ai)), None)
                    if ai:
                        value = subpart[len(ai):]
                        formatted_parts.append(f'({ai}){value}')
                    else:
                        print(f"Warning: Unknown AI in part: {subpart}")
                        formatted_parts.append(subpart)
                elif subpart:  # Only add non-empty subparts
                    formatted_parts.append(subpart)
        
        # Join all parts with the FNC1 character (ASCII 29) between them
        return '\xf1' + '\xf1'.join(formatted_parts)

    def draw(self, draw):
        try:
            if self.barcode_type == 'datamatrix':
                img = self._generate_datamatrix()
                adjusted_y = self.y + self.height - img.height
                draw._image.paste(img, (self.x, adjusted_y))
            else:
                # Existing logic for other barcode types
                actual_type = 'gs1-128' if self.data.startswith('>;') and self.data.endswith('>;') else self.barcode_type
                
                if (actual_type == 'gs1-128'):
                    barcode_image = self._generate_gs1_128()
                elif (actual_type == 'datamatrix'):
                    barcode_image = self._generate_datamatrix()
                else:  # Default to Code 128
                    barcode_image = self._generate_code_128()

                # Resize the barcode image
                barcode_image = barcode_image.resize((self.width, self.height), Image.NEAREST)

                # Paste the barcode onto the label
                draw._image.paste(barcode_image, (self.x, self.y))

            print(f"Drew barcode: {self.data} at ({self.x}, {self.y}) with size {self.width}x{self.height}")
        except Exception as e:
            print(f"Error drawing BarcodeElement: {str(e)}")
            import traceback
            traceback.print_exc()

    def _generate_code_128(self):
        encoder = Code128Encoder(self.data, options={'show_label': False})
        return self._encoder_to_image(encoder)

    def _generate_gs1_128(self):
        formatted_data = self._format_gs1_128_data(self.data)
        print("Raw data sent to encoder:")
        print(' '.join(f'{ord(c):02X}' for c in formatted_data))  # Print hex values
        print(''.join(c if ord(c) >= 32 and ord(c) <= 126 else '.' for c in formatted_data))  # Print ASCII
        encoder = Code128Encoder(formatted_data, options={'mode': 'C', 'show_label': False})
        return self._encoder_to_image(encoder)

    def _generate_datamatrix(self):
        try:
            if self.data.startswith('_1'):
                # Remove the '_1' prefix before formatting
                data_without_prefix = self.data[2:]
                # Replace internal '_1' with FNC1 character (ASCII 29)
                data_without_prefix = data_without_prefix.replace('_1', chr(29))
                formatted_data = self._format_gs1_128_data(data_without_prefix)
                # Remove the FNC1 character that _format_gs1_128_data adds at the start
                formatted_data = formatted_data[1:]
                # Add the GS1 FNC1 character (ASCII 232) at the start
                gs1_data = chr(231) + formatted_data
            else:
                gs1_data = self.data
            print(f"GS1 Data: {gs1_data}")
            encoder = DataMatrixEncoder(gs1_data)
            # Calculate the module size based on the quality (DPI)
            module_size = math.ceil(self.quality / 25.4)  # Convert DPI to modules per mm
            return self._encoder_to_image(encoder)
        except Exception as e:
            print(f"Error generating GS1 DataMatrix: {str(e)}")
            # Return a blank image in case of error
            return Image.new('RGB', (100, 100), color=(255, 255, 255))

    def _encoder_to_image(self, encoder):
        # Get the PNG data as bytes
        png_data = encoder.get_imagedata()
        # Create a PIL Image from the PNG data
        return Image.open(BytesIO(png_data))

class LogoElement(BaseElement):
    def __init__(self, x, y, image_path, width=None, height=None):
        super().__init__(x, y)
        self.image_path = image_path
        self.width = width if width is not None else 100  # Default width
        self.height = height if height is not None else 100  # Default height

    def draw(self, draw):
        try:
            if os.path.exists(self.image_path):
                logo = Image.open(self.image_path)
                logo = logo.resize((self.width, self.height))
                draw._image.paste(logo, (self.x, self.y))
            else:
                print(f"Warning: Logo file not found: {self.image_path}")
                # Draw a placeholder
                draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], outline="black")
                draw.text((self.x + 5, self.y + self.height // 2), "Logo", fill="black")
        except Exception as e:
            print(f"Error drawing logo: {str(e)}")
            # Draw an error placeholder
            draw.rectangle([self.x, self.y, self.x + self.width, self.y + self.height], outline="red")
            draw.text((self.x + 5, self.y + self.height // 2), "Error", fill="red")

class ImageElement:
    def __init__(self, x, y, width, height, image_data, format):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image_data = image_data
        self.format = format
        self.widthBytes = (width + 7) // 8
        self.total = self.widthBytes * height
        self.mapCode = self.initialize_map_code()

    @staticmethod
    def initialize_map_code():
        mapCode = {}
        for i in range(1, 20):
            mapCode[i] = chr(ord('G') + i - 1)
        for i in range(20, 401, 20):
            mapCode[i] = chr(ord('g') + (i // 20) - 1)
        return mapCode

    def gfa_to_image(self):
        hex_data = self.ascii_to_hex(self.image_data)
        print(f"Hex data:\n{hex_data}")
        binary_data = self.hex_to_binary(hex_data)
        print(f"Binary data length: {len(binary_data)}")
        image = Image.new('1', (self.width, self.height))
        pixels = image.load()

        for y in range(self.height):
            for x in range(self.width):
                byte_index = (y * self.widthBytes) + (x // 8)
                bit_index = 7 - (x % 8)
                if byte_index < len(binary_data):
                    pixel = (binary_data[byte_index] >> bit_index) & 1
                    pixels[x, y] = 255 if pixel == 0 else 0  # 0 for black, 255 for white

        return image

    def ascii_to_hex(self, ascii_data):
        hex_lines = []
        current_line = ""
        previous_line = ""
        
        for char in ascii_data:
            if char in '0123456789ABCDEF':
                current_line += char
            elif char in self.mapCode.values():
                count = next(key for key, value in self.mapCode.items() if value == char)
                current_line += '0' * count
            elif char == ',':
                # Pad the current line to the full width before adding it
                padded_line = self.pad_line(current_line)
                if padded_line:
                    hex_lines.append(padded_line)
                    previous_line = padded_line
                current_line = ""
            elif char == ':':
                if previous_line:
                    hex_lines.append(previous_line)
            # Ignore other characters

        # Don't forget to add the last line if there's no trailing comma
        if current_line:
            padded_line = self.pad_line(current_line)
            if padded_line:
                hex_lines.append(padded_line)

        print(f"ASCII to Hex conversion result:\n{hex_lines}")
        return '\n'.join(hex_lines)

    def pad_line(self, line):
        # Calculate how many hex characters we need for a full line
        full_line_length = self.widthBytes * 2
        if len(line) > full_line_length:
            # If the line is too long, truncate it
            padded_line = line[:full_line_length]
            print(f"Truncated line: {padded_line}")
            return padded_line
        elif len(line) < full_line_length:
            # If the line is too short, pad it with '0's
            padded_line = line.ljust(full_line_length, '0')
            print(f"Padded line: {padded_line}")
            return padded_line
        else:
            # If the line is exactly the right length, return it as is
            print(f"Exact length line: {line}")
            return line

    def hex_to_binary(self, hex_data):
        binary_data = bytearray()
        for line in hex_data.split('\n'):
            for i in range(0, len(line), 2):
                if i + 1 < len(line):
                    binary_data.append(int(line[i:i+2], 16))
                else:
                    binary_data.append(int(line[i] + '0', 16))
        return binary_data

    def draw(self, draw):
        print(f"Attempting to draw image: format={self.format}, width={self.width}, height={self.height}")
        print(f"Image data length: {len(self.image_data)}")
        
        if self.format == 'A':  # ASCII format
            try:
                image = self.gfa_to_image()
                draw._image.paste(image, (self.x, self.y))
                print(f"Successfully drew image at ({self.x}, {self.y}), size {self.width}x{self.height}")
                
                # Save the image for debugging
                image.save("debug_image.png")
                print("Saved debug image as 'debug_image.png'")
            except Exception as e:
                print(f"Error drawing ImageElement: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Unsupported image format: {self.format}")