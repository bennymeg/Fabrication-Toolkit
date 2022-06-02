try:
    from .plugin import Plugin
    plugin = Plugin()
    plugin.register()
except Exception as e:
    import logging
    root = logging.getLogger()
    root.debug(repr(e))
