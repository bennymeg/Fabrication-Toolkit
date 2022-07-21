try:
    from .plugin import Plugin
    plugin = Plugin()
    plugin.register()
except Exception as e:
    import logging
    logger = logging.getLogger()
    logger.debug(repr(e))
