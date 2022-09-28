#!/usr/bin/env python3

from globals import PanBlogConfig, PanBlogPackage, render, add_template_global, PanBlogBuild
from subprocess import run, PIPE
from hashlib import sha384
from post import PanBlogPost
from math import ceil
from shutil import copyfileobj

if __name__ == '__main__':
    data = run(('sass', '--style=compressed', PanBlogPackage / 'resources' / 'combined.scss'),
               stdout=PIPE).stdout.decode('UTF8')
    checksum = sha384(data.encode('UTF8')).hexdigest()
    with PanBlogBuild.write(f'{checksum}.css', 'UTF8', None) as fp:
        fp.write(data)
    add_template_global('stylesheet', f'/{checksum}.css')

    for file in (PanBlogPackage / 'resources' / 'fonts').glob('*'):
        with open(file, 'rb') as src:
            with PanBlogBuild.write(f'fonts/{file.name}', None, file) as dst:
                copyfileobj(src, dst)

    if PanBlogConfig.favicon.exists():
        with open(PanBlogConfig.favicon, 'rb') as src:
            with PanBlogBuild.write('favicon.ico', None, PanBlogConfig.favicon) as dst:
                copyfileobj(src, dst)

    posts = []
    for file in sorted(PanBlogConfig.posts.glob('*/*/*/*')):
        if not file.is_file():
            continue
        parts = file.parts
        posts.append(PanBlogPost(parts[-4], parts[-3], parts[-2], parts[-1]))

    pages = max(1, min(ceil(len(posts) / 5), 9))

    for page in range(1, pages + 1):
        previews = []
        for _ in range(min(len(posts), 5)):
            previews.append(posts.pop().process())

        with PanBlogBuild.write(f'{page}/index.html', 'UTF8', None) as fp:
            fp.write(render(
                page='index.html',
                title='Recent Posts',
                previews=previews,
                current=page,
                total=pages,
                canonical=f'{PanBlogConfig.domain}/{page}/',
            ))

    while posts:
        posts.pop().process()

    PanBlogBuild.deploy(PanBlogConfig.output)
