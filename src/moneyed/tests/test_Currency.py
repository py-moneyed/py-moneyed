import unittest


class TestCurrency(unittest.TestCase):

    def create_instance(self, code='', numeric='999', name='', countries=[]):
        from moneyed.classes import Currency
        return Currency(code=code, numeric=numeric, name=name, countries=countries)

    def test_subclass(self):
        from moneyed.classes import Currency
        self.assertTrue(issubclass(Currency, object))

    def test_code_default(self):
        instance = self.create_instance()
        self.assertEqual(instance.code, '')

    def test_code(self):
        instance = self.create_instance(code='EUR')
        self.assertEqual(instance.code, 'EUR')

    def test_numeric_default(self):
        instance = self.create_instance()
        self.assertEqual(instance.numeric, '999')

    def test_numeric(self):
        instance = self.create_instance(numeric='888')
        self.assertEqual(instance.numeric, '888')

    def test_name_default(self):
        instance = self.create_instance()
        self.assertEqual(instance.name, '')

    def test_name(self):
        instance = self.create_instance(name='Euro')
        self.assertEqual(instance.name, 'Euro')

    def test_countries_default(self):
        instance = self.create_instance()
        self.assertEqual(instance.countries, [])

    def test_countries(self):
        instance = self.create_instance(countries=['Finland'])
        self.assertEqual(instance.countries, ['Finland'])

    def test__repr__(self):
        instance = self.create_instance(code='EUR')
        self.assertEqual(instance.__repr__(), 'EUR')
