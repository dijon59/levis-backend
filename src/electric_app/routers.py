import re
from collections import OrderedDict
from itertools import groupby
from rest_framework import routers
from rest_framework.renderers import TemplateHTMLRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import Route
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin
from django.urls import path 


class NoReverseMatch(Exception):
    pass


def get_regex_pattern(urlpattern):
    """
    Get the raw regex out of the urlpattern's RegexPattern or RoutePattern.
    This is always a regular expression.
    """
    if hasattr(urlpattern, 'pattern'):
        # Django 2.0
        return urlpattern.pattern.regex.pattern
    else:
        # Django < 2.0
        return urlpattern.regex.pattern


def camel_to(name, sep):
    a = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
    return a.sub(r'%s\1' % sep, name).lower()


def is_indexed(router_url):
    """
    Check if the View/Viewset should be displayed in the API index/root
    """
    view = router_url.callback

    # Exclude format suffix urls from index view
    if hasattr(router_url, 'pattern') and hasattr(router_url.pattern, 'regex'):
        # Django <2.0
        # noinspection PyProtectedMember
        regex_raw = router_url.pattern.regex.pattern
        # print(regex_raw)
    else:
        # Django >=2.0
        # noinspection PyProtectedMember
        regex_raw = router_url._regex
    if '<format>' in regex_raw:
        return False

    if hasattr(view, 'indexed'):
        return view.indexed
    elif hasattr(view, 'cls') and hasattr(view.cls, 'indexed'):
        return view.cls.indexed
    else:
        return getattr(router_url, '_router_kwargs', {}).get('indexed', True)


def url_is_simple(urlpattern):
    return bool(re.match(r'^[\w-]+$', urlpattern))


class BasicRouter(routers.DefaultRouter):
    """
    Router with auto base-name for views.
    Also removes the "-list" suffix from list Route names
    """
    # remove the ugly "-list" suffix from url names
    routes = [Route(
        url=r'^{prefix}{trailing_slash}$',
        mapping={
            'get': 'list',
            'post': 'create'
        },
        name='{basename}',
        initkwargs={'suffix': ''},
        # Route field compat (Django<1.11, DRF<3.7):
        **{'detail': False} if 'detail' in Route._fields else {}
    )] + routers.DefaultRouter.routes[1:]

    include_root_view = True
    include_format_suffixes = True
    view_suffix_pattern = re.compile(r'view(set)?$', re.IGNORECASE)

    def get_default_basename(self, viewset):
        base_name = getattr(viewset, 'base_name', None)
        cleaned_view_name = re.sub(self.view_suffix_pattern, '', viewset.__name__)
        view_name = camel_to(cleaned_view_name, '-')
        return base_name or view_name


class APIRootView(APIView):
    _ignore_model_permissions = True
    schema = None  # exclude from schema
    exclude_from_schema = True  # exclude from schema (old DRF?)
    # custom:
    router = None
    indexed = False
    # permission_classes = [WhitelistedIP]
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rest_framework/api_root_flexi_router.html'

    LOOKUP_FIELD_REGEX = re.compile(r'\(\?P<(\w+)>')

    def get_detail_url(self, url_name, _url):
        match = self.LOOKUP_FIELD_REGEX.search(get_regex_pattern(_url))
        if match:
            lookup_field = match.group(1)
            return reverse(url_name, kwargs={lookup_field: lookup_field.upper()})
        return None

    def get(self, request, *args, **kwargs):
        # Return a plain json response
        modules = OrderedDict()
        namespace = request.resolver_match.namespace
        for module, _urls in groupby(self.router.index_urls, key=lambda x: x.module):
            module_urls = OrderedDict()
            for _url in _urls:
                if namespace:
                    url_name = namespace + ':' + _url.name
                else:
                    url_name = _url.name

                # handle detail routes
                detail_url = self.get_detail_url(url_name, _url)
                if detail_url:
                    module_urls[url_name] = detail_url
                    continue

                # handle list routes
                try:
                    module_urls[url_name] = reverse(
                        url_name,
                        args=args,
                        kwargs=kwargs,
                        request=request,
                        format=kwargs.get('format', None)
                    )
                except NoReverseMatch:
                    continue
            modules[module] = module_urls
        return Response({'modules': modules})


class FlexiRouter(BasicRouter):
    """
    Router that can be used with both API Views and ViewSets
    """
    APIRootView = APIRootView

    def __init__(self, *args, **kwargs):
        self.namespace = kwargs.pop('namespace', None)
        self.root_view_name = kwargs.pop('root_view_name', 'api-root')
        self.root_view_api_name = kwargs.pop('root_view_api_name', None)
        super(FlexiRouter, self).__init__(*args, **kwargs)
        self._simple_urls = OrderedDict()
        self.modules = {}  # group urls into modules for display in root/index view
        self.trailing_slash = r'/?'  # make the trailing slash optional

    def url(self, pattern):
        if not pattern.startswith('^') and not pattern.endswith('$'):
            return pattern
        if pattern.startswith('^'):
            pattern = pattern.lstrip('^')
        if pattern.endswith('$'):
            pattern = pattern.rstrip('$')
        return pattern

    def add(self, urlpattern, view, name=None, **kwargs):
        # simple url/prefix like 'user-create' can be used for name:
        name = name or (urlpattern if url_is_simple(urlpattern) else None)

        if isinstance(view, type):  # view param is a class
            if issubclass(view, ViewSetMixin):
                basename_args = ('basename', 'base_name')
                basename = {k: v for k, v in kwargs.items() if k in basename_args}
                self.register(urlpattern, view, **basename)
            elif issubclass(view, APIView) or hasattr(view, 'as_view'):
                self.simple(path(self.url(urlpattern), view.as_view(), name=name), **kwargs)
            else:
                raise TypeError('Invalid view type {}'.format(view))
        else:
            self.simple(path(self.url(urlpattern), view, name=name), **kwargs)

    def include(self, apis, module=None, prefix=None):
        """
        Adds a list of apis/urls to the router.
        :param prefix: prefix added to urls
        :param module: optional module/group name
        :type module: str
        :type apis: list
        """
        for a in apis:
            if hasattr(a, 'pattern') and hasattr(a.pattern, '_route'):
                # noinspection PyProtectedMember
                pattern = a.pattern._route
                view = a.callback
                kw = {'name': a.name}
            else:
                view = a['view']
                pattern = a['pattern']
                kw = a['kwargs']
            if module:
                self.modules.setdefault(module, [])
                self.modules[module].append(view)
            if prefix:
                pattern = '{}/{}'.format(prefix, pattern.strip('^'))
            self.add(pattern, view, **kw)

    def get_module(self, view):
        """
        Views can be grouped into modules.
        Finds the module name for a view (key in `self.modules`)
        :return: module name or empty string
        :rtype: str
        """
        return next((k for k, views_list in self.modules.items()
                     if view.__name__ in (v.__name__ for v in views_list)), '')

    def simple(self, urldef, **kwargs):
        """Add simple (non-viewset) urls"""
        urldef._router_kwargs = kwargs
        self._simple_urls[get_regex_pattern(urldef)] = urldef

    def get_urls(self):
        urls = []
        urls.extend(self._simple_urls.values())
        urls.extend(super(FlexiRouter, self).get_urls())
        for u in urls:
            u.namespace = self.namespace
            u.module = self.get_module(u.callback)
        return sorted(urls, key=lambda x: x.module)

    @property
    def index_urls(self):
        """
        The urls that should be shown in the human readable API index page.
        Just excludes the root/index view.
        """
        return [u for u in self.urls if is_indexed(u)]

    def get_api_root_view(self, api_urls=None, **kwargs):
        """
        Replace the default api-root
        """
        return self.APIRootView.as_view(router=self)


class ApiRoute:
    """
    Simple holder of api url/view data
    """

    __slots__ = ('pattern', 'view', 'kwargs')

    def __init__(self, pattern, view_or_viewset, **kwargs) -> None:
        self.pattern = pattern
        self.view = view_or_viewset
        self.kwargs = kwargs

    def __getitem__(self, item):
        return getattr(self, item)


api = ApiRoute
