from jinja2 import Environment, FileSystemLoader
import gzip
from pathlib import Path
from shutil import rmtree
import pypandoc
from slugify import slugify
from config import PanBlogConfig
import sass
from hashlib import sha384
from htmlmin import minify
from datetime import date


def write(content, location):
    location = str(location)
    content = content.encode('UTF8')

    Path(location).parent.mkdir(parents=True, exist_ok=True)

    with open(location, 'wb') as fp:
        fp.write(content)
    with gzip.open(location + '.gz', 'wb') as fp:
        fp.write(content)


if __name__ == '__main__':
    templates = Environment(loader=FileSystemLoader('templates'))
    config = PanBlogConfig()

    if config.output.exists():
        rmtree(config.output)
    config.output.mkdir()

    prefix = '/'
    if config.development:
        prefix = 'file://' + str(config.output.resolve()) + '/'

    css = {}
    for path in (Path('resources/bootstrap.scss'), Path('resources/custom.scss')):
        data = sass.compile(filename=str(path), output_style='compressed')
        checksum = sha384(data.encode('UTF8')).hexdigest()
        write(data, config.output / (checksum + '.css'))
        css[path.stem] = checksum + '.css'

    with open('resources/mathjax/es5/tex-svg.js', 'r') as fp:
        data = fp.read()
    checksum = sha384(data.encode('UTF8')).hexdigest()
    write(data, config.output / (checksum + '.js'))
    js = {'mathjax': checksum + '.js'}


    def render(template, name, **kwargs):
        return minify(templates.get_template(template).render(
            name=name,
            author=config.author,
            css=css, js=js,
            prefix=prefix,
            **kwargs,
        ))


    history = []
    count = 1


    def process():
        page = render('index.html', 'Recent Posts', posts=history, page=count)
        write(page, config.output / str(count) / 'index.html')


    for post in reversed(list(config.posts.glob('*/*/*/*'))):
        parts = post.parent.parts

        html = pypandoc.convert_file(str(post), 'html5', extra_args=['--mathjax'])
        created = date(int(parts[-3]), int(parts[-2]), int(parts[-1])).strftime('%B %d, %Y')
        page = render('post.html', post.stem, document=html, title=post.stem, date=created)
        folder = '/'.join(parts[-3:]) + '/' + slugify(post.stem)
        write(page, config.output / 'posts' / folder / 'index.html')

        if count < 10:
            history.append({
                'html': html,
                'title': post.stem,
                'date': created,
                'link': 'posts/' + folder
            })

        if len(history) == 9:
            process()
            history = []
            count += 1

    if history:
        process()
    del history
