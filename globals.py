from ruamel.yaml import YAML
from pathlib import Path
from jinja2 import Environment, FileSystemLoader


class _PanBlogConfigClass:
    def __init__(self):
        data = YAML(typ='safe').load(Path('config.yml'))

        self.posts = Path(data.get('posts', 'posts'))
        self.output = Path(data.get('output', 'output'))
        self.author = data.get('author', '')
        self.development = not data.get('production', True)


PanBlogPackage = Path(__file__).parent
PanBlogConfig = _PanBlogConfigClass()
PanBlogTemplates = Environment(loader=FileSystemLoader(PanBlogPackage / 'templates'))
