import asyncio
from .middleware import Middleware


class SystemMiddleware(Middleware):
    """Adapter for aiohttp.web midleware factories.
    """

    # Public

    def __init__(self, *args, factory, **kwargs):
        self.__factory = factory
        super.__init__(*args, **kwargs)

    @asyncio.coroutine
    def process(self, request):
        handler = yield from self.factory(None, self.next)
        return (yield from handler(request))
