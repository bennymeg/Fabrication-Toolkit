import sys

# Check if 'pcbnew' is already loaded in a way that suggests a GUI context
# Or check if we are running in a standalone interpreter
is_standalone = 'pcbnew' not in sys.modules or __name__ == "__main__"

if not is_standalone:
    try:
        from .plugin import Plugin
        plugin = Plugin()
        plugin.register()
    except Exception as e:
        import logging
        logger = logging.getLogger()
        logger.debug(repr(e))
