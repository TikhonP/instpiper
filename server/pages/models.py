from django.db import models
from markdown import markdown

class Page(models.Model):
    name = models.CharField(max_length = 50)
    markdown_field = models.TextField()
    html_field = models.TextField(editable = False)

    def __unicode__(self):
        return self.name

    def save(self):
        self.html_field = markdown(self.markdown_field)
        super(Page, self).save()
