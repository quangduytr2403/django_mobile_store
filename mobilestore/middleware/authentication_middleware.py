import re

from django.shortcuts import redirect
from django.urls import reverse


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_requests = [
            '/login',
            '/register',
            '/detail',
            '/about-us',
            '.js',
            '.css',
            '.jpg',
            '.jpeg',
            '.png',
        ]

    def __call__(self, request):
        session = request.session
        logged_in = session is not None and session.get('user_login') is not None
        user_request = request.path_info

        if logged_in or self.is_valid_request(user_request):
            response = self.get_response(request)
        else:
            if user_request.endswith('store/') or user_request.endswith('store') or user_request == '/':
                return redirect(reverse('product_list', args=['1']))
            else:
                return redirect('login')

        return response

    def is_valid_request(self, request_path):
        for excluded_request in self.excluded_requests:
            if request_path.endswith(excluded_request):
                return True

        if re.match("^.*/store/\\d+$", request_path) or re.match("^.*/search/\\d*$", request_path):
            return True

        return False
