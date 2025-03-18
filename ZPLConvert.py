from zpl.elements import TextElement, BarcodeElement, LogoElement, LineElement, BoxElement, ImageElement
from zpl.label import Label
import os
from PIL import Image
import traceback

print("Script started")

def parse_zpl(zpl_data):
    label = Label(850, 1200)  # Adjust size as needed
    state = {
        'current_x': 0,
        'current_y': 0,
        'current_font_size': 12,
        'reverse_field': False,
        'current_font_bold': False,
        'expecting_barcode': False,
        'barcode_type': None,
        'barcode_height': None,
        'barcode_width': None,
    }

    def handle_bc(parts):
        print(f"Handling BC command with parts: {parts}")
        state['expecting_barcode'] = True
        state['barcode_type'] = 'code128'
        if parts:
            state['barcode_height'] = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 10
            state['barcode_width'] = 700  # Default width, adjust as needed
        print(f"Expecting barcode: type={state['barcode_type']}, height={state['barcode_height']}")

    def handle_bx(parts):
        print(f"Handling BX command with parts: {parts}")
        state['expecting_barcode'] = True
        state['barcode_type'] = 'datamatrix'
        if len(parts) >= 5:
            state['barcode_height'] = int(parts[1]) if parts[1] else 10
            state['barcode_width'] = int(parts[3]) if parts[3] else 10
            state['barcode_quality'] = int(parts[4]) if parts[4] else 200
        print(f"Expecting DataMatrix: height={state['barcode_height']}, width={state['barcode_width']}, quality={state['barcode_quality']}")

    def handle_fd(parts):
        print(f"Handling FD command with text: {parts}")
        if parts:
            data = parts[0]  # The entire field data, including any commas
            if state['expecting_barcode']:
                if state['barcode_type'] == 'datamatrix':
                    width = state['barcode_width']
                    height = state['barcode_height']
                else:
                    width = state.get('barcode_width', 100)
                    height = state.get('barcode_height', 100)
                
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
                print(f"Added barcode element: {barcode_element}")
                state['expecting_barcode'] = False
            else:
                text_element = TextElement(
                    state['current_x'],
                    state['current_y'],
                    data,
                    font_size=state.get('current_font_size', 12),
                    bold=state.get('current_font_bold', False),
                    reverse=state.get('reverse_field', False)
                )
                label.add_element(text_element)
                print(f"Added text element: {text_element}")
        else:
            print("No field data provided for FD command")

    def handle_fo(parts):
        if len(parts) == 2:
            state['current_x'], state['current_y'] = map(int, parts)
            print(f"Set position to ({state['current_x']}, {state['current_y']})")

    def handle_ft(parts):
        if len(parts) == 2:
            state['current_x'], state['current_y'] = map(int, parts)
            print(f"Set position to ({state['current_x']}, {state['current_y']}) using FT")

    def handle_gb(parts):
        print("GB command received")
        print(f"Received parts: {parts}")
        print(f"Current reverse_field state: {state['reverse_field']}")
        
        if len(parts) >= 3:
            width, height, thickness = map(int, parts[:3])
            color = 'B'  # Default color is Black
            if len(parts) >= 4:
                color = parts[3].upper()  # Get the color parameter if provided
            rounding = 0  # Default rounding
            if len(parts) >= 5:
                rounding = int(parts[4])  # Get the rounding parameter if provided
            
            print(f"GB command: width={width}, height={height}, thickness={thickness}, color={color}, rounding={rounding}")
            
            # Convert color to RGB
            rgb_color = (0, 0, 0) if color == 'B' else (255, 255, 255)
            
            # Ensure height is at least 1 pixel
            height = max(height, 1)
            
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
            print(f"Added element: {element}")
            
            # Turn off reverse field after use
            state['reverse_field'] = False
            print("Reverse field turned off after element creation")
        else:
            print(f"Insufficient parameters for GB command. Expected at least 3, got {len(parts)}")

    def handle_by(parts):
        if parts and parts[0] == '7':
            state['current_barcode_type'] = 'gs1-128'
            print("Set barcode type to GS1-128")
        else:
            state['current_barcode_type'] = 'code128'
            print("Set barcode type to Code 128")

    def handle_cf(parts):
        if len(parts) >= 2:
            state['current_font_size'] = int(parts[1])
            print(f"Changed font size to {state['current_font_size']}")

    def handle_gf(parts):
        print(f"Handling GF command")
        print(f"Number of parts: {len(parts)}")
        if len(parts) >= 5:
            format, total, total_bytes, bytes_per_row, *data_parts = parts
            
            print(f"GF command parts:")
            print(f"  format: {format}")
            print(f"  total: {total}")
            print(f"  total_bytes: {total_bytes}")
            print(f"  bytes_per_row: {bytes_per_row}")
            print(f"  data_parts length: {len(data_parts)}")
            
            full_data = ','.join(data_parts)  # Use ''.join instead of ','.join
            
            # Calculate image dimensions
            bytes_per_row = int(bytes_per_row)
            width = bytes_per_row * 8
            height = int(total) // bytes_per_row

            print(f"Calculated dimensions: {width}x{height}")
            
            image_element = ImageElement(
                state['current_x'],
                state['current_y'],
                width,
                height,
                full_data,
                format
            )
            label.add_element(image_element)
            print(f"Adding image at position ({state['current_x']}, {state['current_y']}) with size {width}x{height}")
        else:
            print("Insufficient parameters for GF command")
            print(f"Received parts: {parts}")

    def handle_fs(parts):
        print("FS command received - Field Separator")
        state['reverse_field'] = False  # Reset reverse field after each field

    def handle_fr(parts):
        print("FR command received - Reverse Field mode activated")
        state['reverse_field'] = True

    def handle_a0(parts):
        if len(parts) >= 3:
            font_name, font_width, font_height = parts[:3]
            
            # Determine if the font should be bold
            is_bold = font_name in ['0', '2', '4', '6', '8']
            
            # Set font size (you may need to adjust this calculation)
            font_size = max(int(font_height), 12)  # Ensure minimum font size of 12
            
            state['current_font_size'] = font_size
            state['current_font_bold'] = is_bold
            
            print(f"Font set: size={font_size}, bold={is_bold}")
        else:
            print("Insufficient parameters for A0 command")

    def handle_pw(parts):
        if parts:
            width = parts[0].strip()  # Remove leading/trailing whitespace and newlines
            try:
                width = int(width)
                print(f"Setting label width to: {width}")
                state['label_width'] = width
            except ValueError:
                print(f"Invalid width value for PW command: {width}")
        else:
            print("Insufficient parameters for PW command")

    def handle_ci(parts):
        if parts:
            code_page = parts[0]
            print(f"Setting code page to: {code_page}")
            # You might need to implement code page handling if necessary
        else:
            print("Insufficient parameters for CI command")

    def split_command(command):
        cmd = command[:2]
        if cmd == 'FD':
            # For FD command, keep everything after 'FD' as a single string
            return [cmd, command[2:]]
        else:
            # For other commands, split by comma as before
            return [cmd] + command[2:].split(',')

    command_handlers = {
        'FO': handle_fo,  # Field Origin - Sets the position for subsequent fields
        'FT': handle_ft,  # Field Typeset - Sets the field position
        'GB': handle_gb,  # Graphic Box - Draws lines or boxes
        'BY': handle_by,  # Bar Code Field Default - Sets default barcode parameters
        'BC': handle_bc,  # Bar Code - Specifies a barcode type (e.g., Code 128)
        'FD': handle_fd,  # Field Data - Specifies the data for text or barcode fields
        'CF': handle_cf,  # Change Alphanumeric Font - Changes the font or font size
        'GF': handle_gf,
        'FS': handle_fs,  # Graphic Field - Adds an image or logo to the label
        'FR': handle_fr,
        'A0': handle_a0,
        'PW': handle_pw,
        'CI': handle_ci,
        'BX': handle_bx   # DataMatrix 
    }

    commands = zpl_data.strip().split('^')
    for command in commands:
        if not command:
            continue
        if command.startswith('XZ'):
            break  # End of ZPL data
        
        parts = split_command(command)
        cmd = parts[0]
        
        if cmd in command_handlers:
            command_handlers[cmd](parts[1:])
        else:
            print(f"Unknown or unhandled command: {cmd}")

    return label

def read_zpl_data(filename):
    with open(filename, 'r') as file:
        return file.read()

def main():
    try:
        print("Script started")
        print("Entering main function")
        
        filename = "zpl_data.txt"
        print(f"Reading ZPL data from file: {filename}")
        
        zpl_data = read_zpl_data(filename)
        print("ZPL data read successfully:", zpl_data[:100] + "...")
        
        print("Parsing ZPL data")
        label = parse_zpl(zpl_data)
        
        # After processing all commands and drawing elements
        output_directory = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        
        output_file = os.path.join(output_directory, 'output.png')
        
        # Assuming 'label' is your Label object
        image = label.render()
        image.save(output_file)
        print(f"Label saved successfully as: {output_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()

    print("Script finished")

if __name__ == "__main__":
    main()

    

