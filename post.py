from globals import PanBlogConfig, render, PanBlogBuild
from datetime import date
from slugify import slugify
from subprocess import run, PIPE
from shutil import copyfileobj
from bs4 import BeautifulSoup
from pathlib import PurePath


class PanBlogPost:
    def __init__(self, year, month, day, file):
        self.input = PanBlogConfig.posts / year / month / day / file
        self.created = date(int(year), int(month), int(day))
        self.title = file.split('.', 1)[0]
        self.pid = f'{year}/{month}/{day}/{slugify(self.title)}'
        self.link = f'/posts/{self.pid}/'
        self.output = PurePath(self.link).relative_to('/')

    def process(self):
        created = self.created.strftime('%B %d, %Y')
        canonical = PanBlogConfig.domain + self.link

        soup = str(BeautifulSoup(run(
            ('pandoc', '--mathml', '--to=html', self.input), stdout=PIPE,
        ).stdout, 'lxml'))

        extra = self.input.parent / self.title
        for file in extra.glob('**/*'):
            if not file.is_file():
                continue
            with open(file, 'rb') as src:
                with PanBlogBuild.write(self.output / file.relative_to(extra), None, file) as dst:
                    copyfileobj(src, dst)

        page = render('post.html', document=soup, title=self.title, date=created, pid=self.pid, canonical=canonical)
        with PanBlogBuild.write(self.output / 'index.html', 'UTF8', self.input) as fp:
            fp.write(page)

        water = str(BeautifulSoup(soup[:10000], 'lxml'))
        return render('preview.html', document=water, title=self.title, date=created, link=self.link)
