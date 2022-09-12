#!/usr/bin/env python3

from globals import PanBlogConfig, PanBlogPackage, render, add_template_global, PanBlogBuild
import sass
from hashlib import sha384
from post import PanBlogPost
from math import ceil
from shutil import copyfileobj

if __name__ == '__main__':
    data = sass.compile(filename=f'{PanBlogPackage}/resources/combined.scss', output_style='compressed')
    checksum = sha384(data.encode('UTF8')).hexdigest()
    with PanBlogBuild.write(f'{checksum}.css', 'UTF8', None) as fp:
        fp.write(data)
    add_template_global('stylesheet', f'/{checksum}.css')

    for file in (PanBlogPackage / 'resources' / 'fonts').glob('*'):
        with open(file, 'rb') as src:
            with PanBlogBuild.write(f'fonts/{file.name}', None, file) as dst:
                copyfileobj(src, dst)

    posts = []
    for file in sorted(PanBlogConfig.posts.glob('*/*/*/*')):
        if not file.is_file():
            continue
        parts = file.parts
        posts.append(PanBlogPost(parts[-4], parts[-3], parts[-2], parts[-1]))

    pages = min(ceil(len(posts) / 5), 9)

    for page in range(1, pages + 1):
        previews = []
        for _ in range(min(len(posts), 5)):
            previews.append(posts.pop().process())

        with PanBlogBuild.write(f'{page}/index.html', 'UTF8', None) as fp:
            fp.write(render('index.html', title='Recent Posts', previews=previews, current=page, total=pages))

    while posts:
        posts.pop().process()

    PanBlogBuild.deploy(PanBlogConfig.output)
