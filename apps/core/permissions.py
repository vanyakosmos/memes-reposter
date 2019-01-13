from functools import wraps

from graphql import ResolveInfo
from graphql_jwt.exceptions import PermissionDenied


def is_authenticated(info: ResolveInfo):
    user = info.context.user
    return user.is_authenticated


def is_staff(info: ResolveInfo):
    user = info.context.user
    return user.is_staff


def is_admin(info: ResolveInfo):
    user = info.context.user
    return user.is_superuser


def check_permissions(ps, info, raise_exception=True):
    for permission in ps:
        passed = permission(info)
        if not passed:
            if raise_exception:
                raise PermissionDenied()
            return False
    return True


def permissions(*ps):
    def wrapper(resolver):
        @wraps(resolver)
        def decorator(obj, info, *args, **kwargs):
            check_permissions(ps, info)
            return resolver(obj, info, *args, **kwargs)

        return decorator

    return wrapper
