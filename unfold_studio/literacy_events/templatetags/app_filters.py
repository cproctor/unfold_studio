from django import template
import arrow

register = template.Library()

@register.filter(name="humanize")
def humanize(time):
    return arrow.get(time).humanize()
