"""Command registry for ZPL commands."""

class CommandRegistry:
    """Registry of ZPL command handlers."""
    
    def __init__(self):
        self.handlers = {}
    
    def register(self, command, handler):
        """Register a handler for a ZPL command.
        
        Args:
            command: ZPL command code (e.g., 'FO', 'BC')
            handler: Function that processes the command parameters
        """
        self.handlers[command] = handler
    
    def handle(self, command, params, state, label):
        """Handle a ZPL command.
        
        Args:
            command: ZPL command code
            params: List of command parameters
            state: Current state dictionary
            label: Label object
            
        Returns:
            bool: True if command was handled, False otherwise
        """
        if command in self.handlers:
            self.handlers[command](params, state, label)
            return True
        return False