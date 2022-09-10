from globals import PanBlogConfig, PanBlogPackage, render, add_template_global, PanBlogBuild
import sass
from hashlib import sha384
from post import PanBlogPost

if __name__ == '__main__':
    css = {}
    for path in (PanBlogPackage / 'resources/bootstrap.scss', PanBlogPackage / 'resources/custom.scss'):
        data = sass.compile(filename=str(path), output_style='compressed')
        checksum = sha384(data.encode('UTF8')).hexdigest()
        with PanBlogBuild.write(f'{checksum}.css', 'UTF8', None) as fp:
            fp.write(data)
        css[path.stem] = checksum + '.css'
    add_template_global('css', css)

    history = []
    count = 1


    def process():
        page = render('index.html', title='Recent Posts', posts=history, current=count)
        with PanBlogBuild.write(f'{count}/index.html', 'UTF8', None) as fp:
            fp.write(page)


    for file in reversed(list(PanBlogConfig.posts.glob('*/*/*/*'))):
        if not file.is_file():
            continue

        parts = file.parts
        post = PanBlogPost(parts[-4], parts[-3], parts[-2], parts[-1])
        preview = post.process()

        if count < 10:
            history.append(preview)

        if len(history) == 5:
            process()
            history = []
            count += 1

    if history:
        process()
    del history

    PanBlogBuild.deploy(PanBlogConfig.output)
