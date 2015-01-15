# -*- coding: utf-8 -*-
from alm_vcard.models import VCard
from django.test import TestCase
import os
pj = os.path.join

CURRENT_MODULE = os.path.dirname(os.path.dirname(__file__))


def get(obj, accessor):
    _parts = accessor.split('__')
    if len(_parts) == 1:
        return getattr(obj, _parts[0])
    rv = obj
    for _part in _parts:
        try:
            cid = int(_part)
        except ValueError:
            rv = getattr(rv, _part)
        else:
            rv = rv.all()[cid]
    return rv


class VCardTestCase(TestCase):

    def test_importVCard(self):
        file_name = 'vcard_test_single.vcf'
        raw_data = self.load_file(file_name)
        vcard = VCard.fromVCard(raw_data)
        vcard.commit()
        self.assertIsNotNone(vcard)
        self.assertEqual(vcard.adr_set.first().type, 'WORK')
        self.assertTrue(vcard.fn == u'Вася Пупкин')

    def test_importVCardMultiple(self):
        import types
        file_name = 'vcard_test_multi.vcf'
        raw_data = self.load_file(file_name)
        vcards = VCard.importFromVCardMultiple(raw_data)
        self.assertTrue(isinstance(vcards, types.GeneratorType))
        vcards = list(vcards)
        self.assertEqual(len(vcards), 2)
        vcards = map(lambda vcard: vcard.commit(), vcards)
        accessors = ('fn', 'org_set__0__organization_name', 'title_set__0__data')
        expected = [
            (u'Вася Пупкин', u'Алмаклауд', u'Менеджер'),
            (u'Майлюбаев Ернар', u'Алмаклауд', u'ЛОХ')
        ]
        for i, vcard in enumerate(vcards):
            for j, accessor in enumerate(accessors):
                actual = get(vcard, accessor)
                self.assertEqual(actual, expected[i][j])

    def test_importHugeList(self):
        file_name = 'vcard_huge.vcf'
        raw_data = self.load_file(file_name)
        vcards = list(VCard.importFromVCardMultiple(raw_data, autocommit=True))
        self.assertEqual(len(vcards), 863)

    def test_autocommit(self):
        file_name = 'vcard_test_multi.vcf'
        raw_data = self.load_file(file_name)
        vcards = VCard.importFromVCardMultiple(
            raw_data, autocommit=True)
        expected = [u'Менеджер', u'ЛОХ']
        for i, vcard in enumerate(list(vcards)):
            actual = vcard.title_set.all()[0].data
            self.assertEqual(actual, expected[i])

    def test_exportToVCard(self):
        file_name = 'vcard_test_single.vcf'
        raw_data = self.load_file(file_name)
        expected = VCard.fromVCard(raw_data, autocommit=True)
        actual = VCard.fromVCard(expected.toVCard(), autocommit=True)
        self.assertEqual(expected.fn, actual.fn)
        self.assertEqual(expected.family_name, actual.family_name)
        self.assertEqual(expected.org_set.all()[0].organization_name,
                         actual.org_set.all()[0].organization_name)

    def test_exportToVCardMulti(self):
        file_name = 'vcard_test_multi.vcf'
        raw_data = self.load_file(file_name)
        expected = list(VCard.importFromVCardMultiple(
            raw_data, autocommit=True))
        new_raw_data = ''.join(VCard.exportToVCardMultiple(expected))
        actual = list(VCard.importFromVCardMultiple(
            new_raw_data, autocommit=True))
        self.assertEqual(len(expected), len(actual))
        for exp, act in zip(expected, actual):
            self.assertEqual(exp.fn, act.fn)
            self.assertEqual(exp.family_name, act.family_name)
            self.assertEqual(exp.org_set.all()[0],
                             act.org_set.all()[0])
            self.assertEqual(exp.title_set.all()[0],
                             act.title_set.all()[0])

            self.assertEqual(exp.adr_set.first(), act.adr_set.first())

    def load_file(self, name):
        path = pj(CURRENT_MODULE, 'fixtures', name)
        try:
            return open(path, 'r').read()
        except IOError:
            print 'such file does not exist: %s' % path
            return None
