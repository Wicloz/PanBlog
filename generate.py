from shutil import rmtree
import pypandoc
from slugify import slugify
from globals import PanBlogConfig, PanBlogPackage, write, render, add_template_global
import sass
from hashlib import sha384
from datetime import date

if __name__ == '__main__':
    config = PanBlogConfig

    if config.output.exists():
        rmtree(config.output)
    config.output.mkdir()

    css = {}
    for path in (PanBlogPackage / 'resources/bootstrap.scss', PanBlogPackage / 'resources/custom.scss'):
        data = sass.compile(filename=str(path), output_style='compressed')
        checksum = sha384(data.encode('UTF8')).hexdigest()
        write(data, config.output / (checksum + '.css'))
        css[path.stem] = checksum + '.css'
    add_template_global('css', css)

    with open(PanBlogPackage / 'resources/mathjax/es5/tex-svg.js', 'r') as fp:
        data = fp.read()
    checksum = sha384(data.encode('UTF8')).hexdigest()
    write(data, config.output / (checksum + '.js'))
    js = {'mathjax': checksum + '.js'}
    add_template_global('js', js)

    history = []
    count = 1


    def process():
        page = render('index.html', title='Recent Posts', posts=history, current=count)
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

        if len(history) == 5:
            process()
            history = []
            count += 1

    if history:
        process()
    del history
