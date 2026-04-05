from plugins.base_plugin import Plugin, CardT
from plugins.en_2_ru import En2RuPlugin
from plugins.ru_2_cn import Ru2CnPlugin

PLUGINS: list[type[Plugin]] = Plugin.__subclasses__()

__all__ = ['CardT','Plugin', 'En2RuPlugin', 'Ru2CnPlugin', 'PLUGINS']
