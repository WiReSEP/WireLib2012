def user_context(request):
    return add_fullpath(request)


def add_fullpath(request):
    return {'fullpath': request.get_full_path(),
            }
