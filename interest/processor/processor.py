import asyncio
from aiohttp.web import StreamResponse
from .middleware import Middleware


class Processor:

    # Public

    def __init__(self, service):
        self.__service = service
        self.__middlewares = []

    @property
    def service(self):
        return self.__service

    @property
    def middlewares(self):
        return self.__middlewares

    def add_middleware(self, *middlewares, source=None):
        for middleware in middlewares:
            middleware = middleware(self.service)
            self.middlewares.append(middleware)
        if source is not None:
            for middleware in vars(source).values():
                if isinstance(middleware, type):
                    if issubclass(middleware, Middleware):
                        self.add_middleware(middleware)

    @asyncio.coroutine
    def process_request(self, request):
        for middleware in self.middlewares:
            if hasattr(middleware, 'process_request'):
                request = yield from middleware.process_request(request)
        return request

    @asyncio.coroutine
    def process_result(self, result):
        for middleware in self.middlewares:
            if isinstance(result, StreamResponse):
                break
            if hasattr(middleware, 'process_data'):
                result = yield from middleware.process_data(result)
        if not isinstance(result, StreamResponse):
            raise RuntimeError(
                'Middlewares have not properly converted data to response')
        return result

    @asyncio.coroutine
    def process_response(self, response):
        for middleware in reversed(self.middlewares):
            if hasattr(middleware, 'process_response'):
                response = yield from middleware.process_response(response)
        return response

    @asyncio.coroutine
    def process_exception(self, exception):
        for middleware in reversed(self.middlewares):
            if hasattr(middleware, 'process_exception'):
                exception = yield from middleware.process_exception(exception)
        return exception