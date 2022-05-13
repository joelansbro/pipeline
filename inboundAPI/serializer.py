# serializer to take in the API POST and convert it into JSON

import json

class Article:
    def __init__(self, title, author, project, date_published, lead_image_url, content, next_page_url, url, domain, excerpt, word_count, direction, total_pages, rendered_pages):
        self.title = title
        self.author = author
        self.project = project
        self.date_published = date_published
        self.lead_image_url = lead_image_url
        self.content = content
        self.next_page_url = next_page_url
        self.url = url
        self.domain = domain
        self.excerpt = excerpt
        self.word_count = word_count
        self.direction = direction
        self.total_pages = total_pages
        self.rendered_pages = rendered_pages


# will need a serializer method to convert the custom object that is taken in by the inbound API and into a JSON object for storage
# see if you can reuse this somewhere else

class ArticleSerializer:
    def serialize(self, article, format):
        if format == 'JSON': #can pass a POST header here?
            articleSerial = {
                "title": article.title,
                "author": article.author,
                "project": article.project,
                "date_published": article.date_published,
                "lead_image_url": article.lead_image_url,
                "content": article.content,
                "next_page_url": article.next_page_url,
                "url": article.url,
                "domain": article.domain,
                "excerpt": article.excerpt,
                "word_count":article.word_count,
                "direction":article.direction,
                "total_pages":article.total_pages,
                "rendered_pages":article.rendered_pages
        }
            return json.dumps(articleSerial)
        else:
            raise ValueError(format)

