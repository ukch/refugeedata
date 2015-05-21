import django.contrib.auth as auth


class DistributionUser(object):

    def __init__(self, dist_hash, orig_user):
        self._dist_hash = dist_hash
        self._orig_user = orig_user

    def __getattr__(self, attr):
        return getattr(self._orig_user, attr)

    def _has_dist_perm(self, obj):
        if obj is None:
            return False
        return obj.check_hash(self._dist_hash)

    def has_perm(self, name, obj=None, *args, **kwargs):
        if self._orig_user.has_perm(name, obj=obj, *args, **kwargs):
            return True
        if name == DistributionUserMiddleware.permission_name:
            return self._has_dist_perm(obj)
        return False


class DistributionUserMiddleware(object):

    permission_name = "distribution"
    hash_name = "distribution_hash"

    def process_request(self, request):
        if self.hash_name in request.session:
            request.user = DistributionUser(
                request.session[self.hash_name], request.user)


def _remove_hash_from_session(request, **kwargs):
    request.session.pop(DistributionUserMiddleware.hash_name)
    request.session.save()


auth.signals.user_logged_in.connect(_remove_hash_from_session)
auth.signals.user_logged_out.connect(_remove_hash_from_session)
