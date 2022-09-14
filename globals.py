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
        self.mathjax = data.get('mathjax', False)
        self.disqus = data.get('disqus', False)

        self.domain = ''
        if 'domain' in data:
            self.domain = data['domain'].rstrip('/')


class _PanBlogBuildClass:
    def __init__(self):
        self._temp = TemporaryDirectory()
        self.location = Path(self._temp.name)

    @contextmanager
    def write(self, relative, encoding, like):
        output = self.location / relative
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

    def deploy(self, to):
        moved = set()

        def move(relative):
            (to / relative).parent.mkdir(parents=True, exist_ok=True)
            (self.location / relative).rename(to / relative)
            moved.add(relative)

        for file in self.location.glob('**/*'):
            if not file.is_file():
                continue
            file = file.relative_to(self.location)

            if not (to / file).exists():
                move(file)
                continue

            changed = False
            with open(self.location / file, 'rb') as src, open(to / file, 'rb') as dst:
                while True:
                    src_data = src.read(65536)
                    dst_data = dst.read(65536)
                    if src_data != dst_data:
                        changed = True
                        break
                    if not src_data or not dst_data:
                        break

            if changed:
                (to / file).unlink()
                move(file)

        for file in to.glob('**/*'):
            if not file.is_file():
                continue
            file = file.relative_to(to)

            if file not in moved and not (self.location / file).exists():
                (to / file).unlink()

        (to / 'index.html').symlink_to(to / '1' / 'index.html')

        for folder in reversed(list(to.glob('**'))):
            if not next(folder.iterdir(), False):
                folder.rmdir()


PanBlogPackage = Path(__file__).parent
PanBlogConfig = _PanBlogConfigClass()
PanBlogTemplates = Environment(loader=FileSystemLoader(PanBlogPackage / 'templates'))
PanBlogBuild = _PanBlogBuildClass()

add_template_global('author', PanBlogConfig.author)
add_template_global('mathjax', PanBlogConfig.mathjax)
add_template_global('disqus', PanBlogConfig.disqus)
