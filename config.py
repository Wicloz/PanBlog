from ruamel.yaml import YAML
from pathlib import Path


class PanBlogConfig:
    def __init__(self):
        data = YAML(typ='safe').load(Path('config.yml'))

        self.posts = Path(data.get('posts', 'posts'))
        self.output = Path(data.get('output', 'output'))
        self.author = data.get('author', '')
        self.development = not data.get('production', True)
