from urllib.parse import urlparse
from django.http import QueryDict
from django.template import Library

register = Library()


AUTH_PARAMS = ['key', 'sig', 'token', 'v']


@register.simple_tag(takes_context=True)
def authparams(context):
    request = context['request']
    response = context.get('response')

    query = QueryDict(mutable=True)
    # only auth params should be passed on
    for k, v in request.GET.items():
        if k in AUTH_PARAMS:
            query[k] = v

    # add the user token on successful login
    if request.method == 'POST' and getattr(response, 'data', None) and 'token' in response.data:
        query['token'] = response.data['token']

    return '?' + query.urlencode() if query else ''


@register.simple_tag
def url_path(url):
    return urlparse(url).path
