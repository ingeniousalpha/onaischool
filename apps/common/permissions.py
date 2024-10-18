from rest_framework import permissions


class BaseTokenPermission(permissions.BasePermission):
    prefix = 'Bearer'
    token = ''

    def has_permission(self, request, view):
        if not self.token:
            return False

        authorization_header = request.headers.get('Authorization', '')
        if self.prefix:
            prefix, _, token = authorization_header.partition(' ')
            if prefix != self.prefix:
                return False
        else:
            token = authorization_header

        if token == self.token:
            return True
        return False
