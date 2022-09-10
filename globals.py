from ruamel.yaml import YAML
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify
import gzip
from tempfile import TemporaryDirectory
from contextlib import contextmanager
from shutil import copyfileobj, copystat


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


class _PanBlogBuildClass:
    def __init__(self):
        self._temp = TemporaryDirectory()
        self.build = Path(self._temp.name)

    @contextmanager
    def write(self, relative, encoding, like):
        output = self.build / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output = str(output)

        mode = 'w'
        if encoding is None:
            mode += 'b'

        with open(output, mode=mode, encoding=encoding) as fp:
            yield fp

        with open(output, 'rb') as src, gzip.open(output + '.gz', 'wb') as dst:
            copyfileobj(src, dst)

        if like is not None:
            copystat(like, output)
            copystat(like, output + '.gz')


PanBlogPackage = Path(__file__).parent
PanBlogConfig = _PanBlogConfigClass()
PanBlogTemplates = Environment(loader=FileSystemLoader(PanBlogPackage / 'templates'))
add_template_global('author', PanBlogConfig.author)
PanBlogBuild = _PanBlogBuildClass()
