from django.utils import translation


class LanguageHeaderMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Language'] = 'ru'
        response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Language'
        return response

    def process_request(self, request):
        language = request.META.get('HTTP_LANGUAGE')
        if language and language not in ['ru', 'kk'] or not language:
            language = 'ru'
        try:
            translation.activate(language)
        except:
            pass #TODO check language for ISO
        setattr(request, 'language', language)
        response = self.get_response(request)
        return response