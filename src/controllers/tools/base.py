from .csv import ToolsCsv


class Tools:
    def csv(self, **kwargs) -> ToolsCsv:
        return ToolsCsv(kwargs)
