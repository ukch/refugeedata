from django_rq import job

from .. import utils


@job
def send_sms(to, body):
    for number in to:
        send_single_sms.delay([number], body)


@job
def send_single_sms(to, body):
    utils.send_sms(to=to, body=body)
