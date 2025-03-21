"""ZPL command handlers."""

from .registry import CommandRegistry
from .text import register_text_commands
from .barcode import register_barcode_commands
from .graphic import register_graphic_commands

def create_command_registry():
    """Create and initialize a command registry with all handlers."""
    registry = CommandRegistry()
    register_text_commands(registry)
    register_barcode_commands(registry)
    register_graphic_commands(registry)
    
    # Register special commands (start/end label, comments)
    registry.register('XA', lambda params, state, label: print("Start of ZPL data"))
    registry.register('XZ', lambda params, state, label: print("End of ZPL data"))
    registry.register('FX', lambda params, state, label: print("Comment: " + (params[0] if params else "")))
    
    return registry

__all__ = ['create_command_registry', 'CommandRegistry']
