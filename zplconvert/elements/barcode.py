"""Barcode element classes for ZPL conversion."""

import math
from io import BytesIO
from PIL import Image
from pystrich.code128 import Code128Encoder
from pystrich.datamatrix import DataMatrixEncoder
from .base import BaseElement

class BarcodeElement(BaseElement):
    """Element for rendering barcodes on labels."""
    
    def __init__(self, x, y, data, width=300, height=100, barcode_type='code128', quality=200, width_ratio=3.0):
        super().__init__(x, y)
        self.data = data
        self.width = width
        self.height = height
        self.barcode_type = barcode_type
        self.quality = quality
        self.width_ratio = width_ratio

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
                
                if actual_type == 'gs1-128':
                    barcode_image = self._generate_gs1_128()
                elif actual_type == 'datamatrix':
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