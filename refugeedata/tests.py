from django.core.management import call_command
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from model_mommy import mommy

from .middleware import EnforceCurrentSiteMiddleware
from .models import RegistrationNumber, Distribution


class DistributionTests(TestCase):

    def setUp(self):
        cards = []
        for number in xrange(1, 16):
            cards.append(mommy.prepare(RegistrationNumber, number=number,
                                       active=True))
        RegistrationNumber.objects.bulk_create(cards)

    def test_invitees(self):
        dist1 = mommy.make(Distribution, supplies_quantity=6)
        dist1_values = dist1.invitees.values_list("number", flat=True)
        self.assertEqual(list(dist1_values), [1, 2, 3, 4, 5, 6])
        self.assertEqual(dist1.finish_number, 6)

        dist2 = mommy.make(Distribution, supplies_quantity=10)
        dist2_values = dist2.invitees.values_list("number", flat=True)
        self.assertEqual(list(dist2_values),
                         [1, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        self.assertEqual(dist2.finish_number, 1)

    def test_only_active_invitees(self):
        RegistrationNumber.objects.filter(number=3).update(active=False)
        dist = mommy.make(Distribution, supplies_quantity=5)
        dist_values = dist.invitees.values_list("number", flat=True)
        self.assertEqual(list(dist_values), [1, 2, 4, 5, 6])
        self.assertEqual(dist.finish_number, 6)


@override_settings(INSTALLED_APPS=("django.contrib.sites", ))
class MiddlewareTest(TestCase):

    def setUp(self):
        call_command("migrate", "sites", verbosity=0)
        self.middleware = EnforceCurrentSiteMiddleware()
        self.rf = RequestFactory()

    def test_simple(self):
        request = self.rf.get("/foo")
        response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "//example.com/foo")

    def test_with_site_id(self):
        request = self.rf.get("/foo")
        with self.settings(SITE_ID=1):
            response = self.middleware.process_request(request)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "//example.com/foo")

    def test_without_sites(self):
        request = self.rf.get("/foo")
        with self.settings(INSTALLED_APPS=()):
            response = self.middleware.process_request(request)
        self.assertIsNone(response)
        self.assertEqual(type(request.site).__name__, "RequestSite")
