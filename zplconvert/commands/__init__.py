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
    
    # Start/end / comments / common no-ops
    noop = lambda params, state, label: None
    registry.register('XA', noop)
    registry.register('XZ', noop)
    registry.register('FX', noop)
    registry.register('CI', noop)  # Change international font/encoding
    registry.register('PQ', noop)  # Print quantity
    registry.register('LH', noop)  # Label home
    registry.register('LS', noop)  # Label shift
    registry.register('LT', noop)  # Label top
    registry.register('PR', noop)  # Print rate
    registry.register('MD', noop)  # Media darkness
    registry.register('MM', noop)  # Media mode
    registry.register('PO', noop)  # Print orientation
    registry.register('JZ', noop)

    return registry

__all__ = ['create_command_registry', 'CommandRegistry']
