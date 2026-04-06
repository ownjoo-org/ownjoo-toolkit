import unittest

from ownjoo_toolkit.data.flex import FlexMixin


class ConcreteFlexMixin(FlexMixin):
    """Concrete subclass of FlexMixin for testing."""

    class_attr: str = 'class_value'


class TestFlexMixin(unittest.TestCase):
    """Tests for FlexMixin."""

    def test_should_set_attrs_from_kwargs(self):
        obj = ConcreteFlexMixin(name='Alice', age=30)
        self.assertEqual(obj.name, 'Alice')
        self.assertEqual(obj.age, 30)

    def test_should_get_existing_attr(self):
        obj = ConcreteFlexMixin(name='Alice')
        self.assertEqual(obj.get('name'), 'Alice')

    def test_should_get_default_for_missing_attr(self):
        obj = ConcreteFlexMixin()
        self.assertEqual(obj.get('missing', 'default'), 'default')

    def test_should_return_none_for_missing_attr_with_no_default(self):
        obj = ConcreteFlexMixin()
        self.assertIsNone(obj.get('missing'))

    def test_should_get_falsy_value_not_default(self):
        obj = ConcreteFlexMixin(count=0, flag=False, label='')
        self.assertEqual(obj.get('count', 99), 0)
        self.assertEqual(obj.get('flag', True), False)
        self.assertEqual(obj.get('label', 'fallback'), '')

    def test_to_dict_includes_instance_attrs(self):
        obj = ConcreteFlexMixin(name='Alice', age=30)
        d = obj.to_dict()
        self.assertEqual(d['name'], 'Alice')
        self.assertEqual(d['age'], 30)

    def test_to_dict_includes_class_attrs(self):
        obj = ConcreteFlexMixin()
        d = obj.to_dict()
        self.assertIn('class_attr', d)
        self.assertEqual(d['class_attr'], 'class_value')

    def test_to_dict_instance_attr_overrides_class_attr(self):
        obj = ConcreteFlexMixin(class_attr='overridden')
        d = obj.to_dict()
        self.assertEqual(d['class_attr'], 'overridden')

    def test_to_dict_excludes_private_attrs(self):
        obj = ConcreteFlexMixin(_private='secret')
        d = obj.to_dict()
        self.assertNotIn('_private', d)

    def test_repr_includes_class_name(self):
        obj = ConcreteFlexMixin(name='Alice')
        self.assertIn('ConcreteFlexMixin', repr(obj))

    def test_repr_includes_attrs(self):
        obj = ConcreteFlexMixin(name='Alice')
        self.assertIn('Alice', repr(obj))


if __name__ == '__main__':
    unittest.main()
