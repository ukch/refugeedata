from django.contrib.auth.decorators import permission_required


register_permission_required = permission_required(
    "refugeedata.add_person", raise_exception=True)

# TODO add a special permission for this
register_or_qr_permission_required = register_permission_required
