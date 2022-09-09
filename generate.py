from shutil import rmtree, copytree
from globals import PanBlogConfig, PanBlogPackage, write, render, add_template_global
import sass
from hashlib import sha384
from post import PanBlogPost

if __name__ == '__main__':
    css = {}
    for path in (PanBlogPackage / 'resources/bootstrap.scss', PanBlogPackage / 'resources/custom.scss'):
        data = sass.compile(filename=str(path), output_style='compressed')
        checksum = sha384(data.encode('UTF8')).hexdigest()
        write(data, PanBlogConfig.build / (checksum + '.css'))
        css[path.stem] = checksum + '.css'
    add_template_global('css', css)

    history = []
    count = 1


    def process():
        page = render('index.html', title='Recent Posts', posts=history, current=count)
        write(page, PanBlogConfig.build / str(count) / 'index.html')


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

    if PanBlogConfig.output.exists():
        rmtree(PanBlogConfig.output)
    copytree(PanBlogConfig.build, PanBlogConfig.output)
