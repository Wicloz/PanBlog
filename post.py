from globals import PanBlogConfig, render, write
from datetime import date
from slugify import slugify
import pypandoc


class PanBlogPost:
    def __init__(self, year, month, day, file):
        self.input = PanBlogConfig.posts / year / month / day / file
        self.created = date(int(year), int(month), int(day))
        self.title = file.split('.', 1)[0]
        self.link = f'/posts/{year}/{month}/{day}/{slugify(self.title)}/'
        self.output = PanBlogConfig.output / self.link[1:]

    def process(self):
        html = pypandoc.convert_file(
            source_file=str(self.input),
            to='html5',
            extra_args=['--mathjax'],
        )
        created = self.created.strftime('%B %d, %Y')

        page = render('post.html', document=html, title=self.title, date=created)
        write(page, self.output / 'index.html')

        return render('preview.html', document=html, title=self.title, date=created, link=self.link)
