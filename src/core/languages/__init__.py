from core.languages.base import Plugin, CardT
from core.languages.en_ru import En2RuPlugin
from core.languages.ru_cn import Ru2CnPlugin

PLUGINS: list[type[Plugin]] = Plugin.__subclasses__()

__all__ = ["CardT", "Plugin", "En2RuPlugin", "Ru2CnPlugin", "PLUGINS"]
