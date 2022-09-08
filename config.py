from ruamel.yaml import YAML
from pathlib import Path


class PanBlogConfig:
    def __init__(self):
        self.data = YAML().load(Path('config.yml'))

    @property
    def posts(self):
        return Path(self.data['posts'])

    @property
    def output(self):
        return Path(self.data['output'])

    @property
    def author(self):
        return Path(self.data['author'])

    @property
    def development(self):
        return not self.data['production']
