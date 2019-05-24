
class CouldNotGenerateImprovementException(Exception):
    pass

class AbstractStratagy():
    def generate_improvement(self, settings):
        raise NotImplementedError()
