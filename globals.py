from ruamel.yaml import YAML
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify
import gzip
from tempfile import TemporaryDirectory


def write(content, location):
    location = Path(location)
    content = content.encode('UTF8')

    location.parent.mkdir(parents=True, exist_ok=True)

    with open(location, 'wb') as fp:
        fp.write(content)
    with gzip.open(str(location) + '.gz', 'wb') as fp:
        fp.write(content)


def render(page, **kwargs):
    return minify(PanBlogTemplates.get_template(page).render(**kwargs))


def add_template_global(key, value):
    PanBlogTemplates.globals[key] = value


class _PanBlogConfigClass:
    def __init__(self):
        data = YAML(typ='safe').load(Path('config.yml'))

        self.posts = Path(data.get('posts', 'posts'))
        self.output = Path(data.get('output', 'output'))
        self.author = data.get('author', 'Wicloz')

        self._temp = TemporaryDirectory()
        self.build = Path(self._temp.name)


PanBlogPackage = Path(__file__).parent
PanBlogConfig = _PanBlogConfigClass()
PanBlogTemplates = Environment(loader=FileSystemLoader(PanBlogPackage / 'templates'))
add_template_global('author', PanBlogConfig.author)
