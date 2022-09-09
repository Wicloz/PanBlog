from globals import PanBlogConfig, render, write
from datetime import date
from slugify import slugify
from subprocess import run
from shutil import copytree
from bs4 import BeautifulSoup


class PanBlogPost:
    def __init__(self, year, month, day, file):
        self.input = PanBlogConfig.posts / year / month / day / file
        self.created = date(int(year), int(month), int(day))
        self.title = file.split('.', 1)[0]
        self.link = f'/posts/{year}/{month}/{day}/{slugify(self.title)}/'
        self.output = PanBlogConfig.build / self.link[1:]

    def process(self):
        created = self.created.strftime('%B %d, %Y')
        soup = str(BeautifulSoup(run(
            ('pandoc', '--mathml', '--to=html', self.input), capture_output=True,
        ).stdout, 'lxml'))

        if (self.input.parent / self.input.stem).is_dir():
            copytree(self.input.parent / self.input.stem, self.output)

        page = render('post.html', document=soup, title=self.title, date=created)
        write(page, self.output / 'index.html')

        water = str(BeautifulSoup(soup[:10000], 'lxml'))
        return render('preview.html', document=water, title=self.title, date=created, link=self.link)
