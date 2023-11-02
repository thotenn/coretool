from django.conf import settings
from django.contrib.auth.models import Group


def in_admin_group(user):
    if not user.is_superuser:
        groups = Group.objects.filter(name__in=settings.ADMINS_GROUPS)
        usergroups = user.groups.all()
        return any(n in usergroups for n in groups)
    return True


class UserController():
    def __init__(self, user):
        self.user = user

    def in_admin_group(self, user=None):
        if user is None:
            if self.user is None:
                return False
            user = self.user
        if not user.is_superuser:
            groups = Group.objects.filter(name__in=settings.ADMINS_GROUPS)
            usergroups = user.groups.all()
            return any(n in usergroups for n in groups)
        return True
