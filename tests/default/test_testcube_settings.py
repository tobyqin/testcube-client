import unittest

from testcube_client.settings import get_cache, add_cache, delete_cache


class TestCases(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_cache_function(self):
        delete_cache('User', name='Toby')
        obj1 = get_cache('User', name='Toby')
        assert obj1 == None

        obj = {'name': 'Toby', 'age': 18}
        add_cache('User', obj)

        obj1 = get_cache('User', name='Toby')
        print(obj1)

        add_cache('User', obj)

        try:
            get_cache('User', name='Toby')
        except ValueError as e:
            print(e)

        delete_cache('User', name='Toby')
