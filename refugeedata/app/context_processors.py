from django.conf import settings


def languages(request):
    """This data is used to populate the language dropdown."""

    for code, name in settings.LANGUAGES:
        code_path = "/{}/".format(code)
        if code_path in request.path:
            current_lang = code
            current_lang_name = name
            break
    else:
        return {"multilanguage": False}

    language_urls = [(name, request.path.replace(current_lang, code))
                     for code, name in settings.LANGUAGES
                     if code != current_lang]
    return {
        "multilanguage": True,
        "current_lang": current_lang,
        "current_lang_name": current_lang_name,
        "language_urls": language_urls,
    }
