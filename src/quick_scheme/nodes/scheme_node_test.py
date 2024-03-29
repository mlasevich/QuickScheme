''' Unit Tests For SchemeNode '''

import logging
import unittest

from quick_scheme.field import Field
from quick_scheme.nodes.scheme_node import SchemeNode

from ..exceptions import QuickSchemeValidationException


class MyEmptyNode(SchemeNode):
    ''' Empty Scheme Node '''


class MyOpenEmptyNode(SchemeNode):
    ''' Empty Opened Scheme Node '''
    ALLOW_UNDEFINED = True


class MyClosedNode(SchemeNode):
    ''' Closed Scheme Node '''
    FIELDS = [
        Field('id', identity=True),
        Field('name', brief=False, ftype=str, default="def", always=True),
        Field('integer_no_default', ftype=int),
        Field('integer_with_default_1', ftype=int, default=1),
        Field('integer_with_default_2', ftype=int, default=2, always=False),
    ]


class MyOpenNode(MyClosedNode):
    ''' Open Scheme Node '''
    ALLOW_UNDEFINED = True
    FIELDS = [
        Field('id', identity=True),
        Field('name', brief=True, ftype=str, default="def", always=True),
        Field('integer_no_default', ftype=int),
        Field('integer_with_default_1', ftype=int, default=1),
        Field('integer_with_default_2', ftype=int, default=2, always=False),
    ]

    def _on_not_set_integer_no_default(self, data, **kwargs):
        ''' Runs if integer_no_default is not '''
        self._data['integer_no_default_unset'] = 'unset'

    def _before_set_b4(self, value, **_):
        ''' Runs Before b4 is set '''
        value = "__" + value + "__"
        return value

    def _after_set_after(self, value, field, extra_data):
        ''' Runs After 'after' is set '''
        extra_data['after_%s' % field] = value
        return True

    def _do_set_override(self, value, field, extra_data):
        ''' Runs instead setting 'override' '''
        print("Overriding!")
        extra_data['instead'] = {field: value}
        return True


class TestSchemeNode(unittest.TestCase):
    '''Field tests'''

    def test_class_name_empty(self):
        ''' Test class _name field '''
        node = MyEmptyNode(None, data={})
        self.assertEqual(node._name, 'MyEmptyNode')
        self.assertEqual(node.quick_scheme.name, 'MyEmptyNode')

    def test_class_name_closed(self):
        ''' Test class _name field '''
        node = MyClosedNode(None, data={})
        self.assertEqual(node._name, 'MyClosedNode')
        self.assertEqual(node.quick_scheme.name, 'MyClosedNode')

    def test_empty_node(self):
        ''' Test empty node with no data'''
        node = MyEmptyNode(None, data={})
        self.assertDictEqual(node.quick_scheme.get_data(), {})

    def test_empty_closed_node_with_data(self):
        ''' Test empty node with data'''
        with self.assertRaises(QuickSchemeValidationException) as ex:
            _ = MyEmptyNode(None, data={'id': 'one'})
        self.assertEqual(
            "Invalid field 'id' for 'MyEmptyNode'", str(ex.exception))

    def test_empty_opened_node_with_data(self):
        ''' Test empty node with data'''
        node = MyOpenEmptyNode(None, data={'id': 'one'})
        self.assertEqual(node.quick_scheme.get_data(), {'id': 'one'})

    def test_closed_node_empty(self):
        ''' Test getting action_desc'''
        node = MyClosedNode(None, data={})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': '',
                                                            'name': 'def',
                                                            'integer_no_default': 0,
                                                            'integer_with_default_1': 1})

    def test_closed_node_data(self):
        ''' Test getting action_desc'''
        node = MyClosedNode(
            None, data={'id': 'value', 'integer_no_default': 5})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1})

    def test_closed_node_extra_data(self):
        ''' Test getting action_desc'''

        with self.assertRaises(QuickSchemeValidationException) as ex:
            _ = MyClosedNode(
                None, data={'id': 'value', 'integer_no_default': 5, 'wrong': 'item'})
        self.assertEqual(
            "Invalid field 'wrong' for 'MyClosedNode'", str(ex.exception))

    def test_closed_node_brief(self):
        ''' Test getting action_desc'''
        with self.assertRaises(QuickSchemeValidationException) as ex:
            _ = MyClosedNode(None, data="my brief value")
        self.assertEqual(
            'Node MyClosedNode is defined via brief syntax but briefset field is not found',
            str(ex.exception))

    def test_open_node_empty(self):
        ''' Test getting action_desc'''
        node = MyOpenNode(None, data={})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': '',
                                                            'name': 'def',
                                                            'integer_no_default': 0,
                                                            'integer_with_default_1': 1,
                                                            'integer_no_default_unset': 'unset'})

    def test_open_node_data(self):
        ''' Test getting action_desc'''
        node = MyOpenNode(None, data={'id': 'value', 'integer_no_default': 5})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1})

    def test_open_node_data_hooks_b4(self):
        ''' Test before_set hook'''
        node = MyOpenNode(
            None, data={'id': 'value', 'integer_no_default': 5, 'b4': 'my_before'})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1,
                                                            'b4': '__my_before__'})

    def test_open_node_data_hooks_after(self):
        ''' Test after_set hook'''
        node = MyOpenNode(
            None, data={'id': 'value', 'integer_no_default': 5, 'after': 'my_after'})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1,
                                                            'after': 'my_after',
                                                            'after_after': 'my_after'})

    def test_open_node_data_hooks_instead(self):
        ''' Test 'on-set' hook '''
        node = MyOpenNode(
            None, data={'id': 'value', 'integer_no_default': 5, 'override': 'my_instead'})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1,
                                                            'instead': {'override': 'my_instead'}})

    def test_open_node_extra_data(self):
        ''' Test getting action_desc'''

        node = MyOpenNode(
            None, data={'id': 'value', 'integer_no_default': 5, 'wrong': 'item'})
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': 'value',
                                                            'name': 'def',
                                                            'integer_no_default': 5,
                                                            'integer_with_default_1': 1,
                                                            'wrong': 'item'})

    def test_open_node_brief(self):
        ''' Test getting action_desc'''
        node = MyOpenNode(None, data="my brief value")
        self.assertEqual(len(node.quick_scheme.fields),
                         len(MyClosedNode.FIELDS))
        self.assertDictEqual(node.quick_scheme.get_data(), {'id': '',
                                                            'name': 'my brief value',
                                                            'integer_no_default': 0,
                                                            'integer_with_default_1': 1,
                                                            'integer_no_default_unset': 'unset'})


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
