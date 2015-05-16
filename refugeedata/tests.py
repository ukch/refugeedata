from django.test import TestCase

from model_mommy import mommy

from .models import RegistrationNumber, Distribution


class DistributionTests(TestCase):

    def setUp(self):
        cards = []
        for number in xrange(1, 16):
            cards.append(mommy.prepare(RegistrationNumber, number=number))
        RegistrationNumber.objects.bulk_create(cards)

    def test_invitees(self):
        dist1 = mommy.make(Distribution, supplies_quantity=6)
        dist1_values = dist1.invitees.values_list("number", flat=True)
        self.assertEqual(dist1.finish_number, 6)
        self.assertEqual(list(dist1_values), [1, 2, 3, 4, 5, 6])

        dist2 = mommy.make(Distribution, supplies_quantity=10)
        dist2_values = dist2.invitees.values_list("number", flat=True)
        self.assertEqual(dist2.finish_number, 1)
        self.assertEqual(list(dist2_values),
                         [1, 7, 8, 9, 10, 11, 12, 13, 14, 15])
