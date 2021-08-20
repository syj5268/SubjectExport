from django import template


register = template.Library()

@register.filter
def split(value):
    tags=value.split(',')
    taglist=str('')

    for tag in tags:
        taglist+= '#'+str(tag)+str(' ')

    return taglist

