import functools


def cache_control(seconds, view_func=None):
    if view_func is None:
        return functools.partial(cache_control, seconds)

    @functools.wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # _cache_control_max_age is parsed by MaxAgeMiddleware
        request._cache_control_max_age = seconds
        return view_func(request, *args, **kwargs)

    return wrapper
