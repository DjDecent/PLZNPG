from PIL import Image, ImageDraw
from zpl.elements import LineElement, BoxElement, TextElement, BarcodeElement, ImageElement  # Add missing imports

class Label:
    def __init__(self, width=400, height=600):  # Adjust default size as needed
        self.width = width
        self.height = height
        self.elements = []

    def add_element(self, element):
        self.elements.append(element)

    def render(self):
        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)
        for element in self.elements:
            try:
                element.draw(draw)
            except Exception as e:
                print(f"Error drawing element {type(element).__name__}: {str(e)}")
        return image
