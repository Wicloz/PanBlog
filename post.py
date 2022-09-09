from globals import PanBlogConfig, render, write
from datetime import date
from slugify import slugify
from subprocess import run
from shutil import copytree


class PanBlogPost:
    def __init__(self, year, month, day, file):
        self.input = PanBlogConfig.posts / year / month / day / file
        self.created = date(int(year), int(month), int(day))
        self.title = file.split('.', 1)[0]
        self.link = f'/posts/{year}/{month}/{day}/{slugify(self.title)}/'
        self.output = PanBlogConfig.output / self.link[1:]

    def process(self):
        created = self.created.strftime('%B %d, %Y')
        html = run(
            ('pandoc', '--mathml', '--to=html', self.input),
            capture_output=True, universal_newlines=True, encoding='UTF8',
        ).stdout

        if (self.input.parent / self.input.stem).is_dir():
            copytree(self.input.parent / self.input.stem, self.output)

        page = render('post.html', document=html, title=self.title, date=created)
        write(page, self.output / 'index.html')

        return render('preview.html', document=html, title=self.title, date=created, link=self.link)
