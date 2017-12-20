# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, division

from cms.api import add_plugin
from cms.models import Placeholder
from django.db import IntegrityError
from django.test import TestCase

from aldryn_forms.models import Option


class OptionTestCase(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        self.placeholder = Placeholder.objects.create(slot='test')
        self.field = add_plugin(self.placeholder, 'SelectField', 'en')

    def test_position_organic_ordering(self):
        ''' Tests that no manual ordering leads to an organic ordering: first added, first displayed. '''
        self.field.option_set.create(value='one')
        self.field.option_set.create(value='two')
        self.field.option_set.create(value='three')
        self.field.option_set.create(value='four')
        self.field.option_set.create(value='five')

        option1, option2, option3, option4, option5 = self.field.option_set.all()

        self.assertEquals(option1.value, 'one')
        self.assertEquals(option1.position, 10)
        self.assertEquals(option2.value, 'two')
        self.assertEquals(option2.position, 20)
        self.assertEquals(option3.value, 'three')
        self.assertEquals(option3.position, 30)
        self.assertEquals(option4.value, 'four')
        self.assertEquals(option4.position, 40)
        self.assertEquals(option5.value, 'five')
        self.assertEquals(option5.position, 50)

    def test_position_manual_ordering(self):
        self.field.option_set.create(position=100, value='below $10')
        self.field.option_set.create(position=200, value='between $10 and $50')
        self.field.option_set.create(position=10, value='super promo: below $1!')
        self.field.option_set.create(position=300, value='$50+ because you are rich')
        self.field.option_set.create(position=1, value='items for free (but they are broken - sorry)')

        option1, option2, option3, option4, option5 = self.field.option_set.all()

        self.assertEquals(option1.value, 'items for free (but they are broken - sorry)')
        self.assertEquals(option1.position, 1)
        self.assertEquals(option2.value, 'super promo: below $1!')
        self.assertEquals(option2.position, 10)
        self.assertEquals(option3.value, 'below $10')
        self.assertEquals(option3.position, 100)
        self.assertEquals(option4.value, 'between $10 and $50')
        self.assertEquals(option4.position, 200)
        self.assertEquals(option5.value, '$50+ because you are rich')
        self.assertEquals(option5.position, 300)

    def test_hybrid_ordering(self):
        self.field.option_set.create(position=31415, value='But after a while I got lazy')
        self.field.option_set.create(value='and so I didnt wanna')
        self.field.option_set.create(value='set this ordering')
        self.field.option_set.create(value='anymore')
        self.field.option_set.create(position=42, value='I started this ordering manually')

        option1, option2, option3, option4, option5 = self.field.option_set.all()

        self.assertEquals(option1.value, 'I started this ordering manually')
        self.assertEquals(option1.position, 42)
        self.assertEquals(option2.value, 'But after a while I got lazy')
        self.assertEquals(option2.position, 31415)
        self.assertEquals(option3.value, 'and so I didnt wanna')
        self.assertEquals(option3.position, 31425)
        self.assertEquals(option4.value, 'set this ordering')
        self.assertEquals(option4.position, 31435)
        self.assertEquals(option5.value, 'anymore')
        self.assertEquals(option5.position, 31445)

    def test_position_is_not_nullable(self):
        self.field.option_set.create(position=950, value='950')

        # Noise
        another_field = add_plugin(self.placeholder, 'SelectField', 'en')
        another_field.option_set.create(position=1000, value='1000 for another field so it does not matter')

        option1 = self.field.option_set.create(position=1, value='test')
        option1.position = None
        option1.save()
        self.assertEquals(option1.position, 960)  # We force a value for it on Option.save

        self.assertRaises(IntegrityError, Option.objects.update, position=None)  # See? Not nullable
