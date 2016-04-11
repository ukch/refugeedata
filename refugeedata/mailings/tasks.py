from django_rq import job

from .. import utils


@job
def send_sms(to, body):
    utils.send_sms(to=to, body=body)
