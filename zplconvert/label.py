"""Label container for ZPL elements."""

from PIL import Image, ImageDraw

class Label:
    """Container for label elements."""
    
    def __init__(self, width=800, height=1200, dpi=203):
        """Initialize a new label.
        
        Args:
            width: Width of the label in pixels
            height: Height of the label in pixels
            dpi: Dots per inch
        """
        self.width = width
        self.height = height
        self.dpi = dpi
        self.elements = []

    def add_element(self, element):
        """Add an element to the label.
        
        Args:
            element: A BaseElement subclass instance
        """
        self.elements.append(element)

    def render(self):
        """Render the label to an image.
        
        Returns:
            PIL.Image: The rendered label
        """
        image = Image.new('RGB', (self.width, self.height), color='white')
        draw = ImageDraw.Draw(image)
        
        for element in self.elements:
            try:
                element.draw(draw)
            except Exception as e:
                print(f"Error drawing element {type(element).__name__}: {str(e)}")
                
        return image