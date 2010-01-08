import unittest

from repoze.bfg.configuration import Configurator
from repoze.bfg import testing

class ViewTests(unittest.TestCase):
    def setUp(self):
        self.config = Configurator()
        self.config.begin()

    def tearDown(self):
        self.config.end()

    def test_view_home(self):
        from views import home
        request = testing.DummyRequest()
        info = home(request)
        self.assertEqual(info['message'], '')

    def test_get_bank_accounts_bad_domain(self):
        from views import _get_bank_accounts
        from views import NonXMLResponseError
        self.assertRaises(NonXMLResponseError, _get_bank_accounts,
                          "baddomain", "email", "password")

    def test_get_bank_accounts_bad_auth(self):
        from views import _get_bank_accounts
        from views import BadAuthError
        self.assertRaises(BadAuthError, _get_bank_accounts,
                          "koansyssandbox", "bademail", "badpassword")


    def test_get_bank_accounts_exist(self):
        from views import _get_bank_accounts
        domain = "koansyssandbox"
        email = "chris@shenton.org"
        password = "koansyssandbox"
        accounts = _get_bank_accounts(domain, email, password)
        # we don't know the bank account numbers or names
        # so just check we get a non-empty dict and an id is integer
        self.assertEquals(type(accounts), dict)
        self.assertNotEqual(len(accounts), 0)
        self.assertTrue(int(accounts.keys()[0]))

    def test_get_bank_account_entries(self):
        from views import _get_bank_account_entries
        domain = "koansyssandbox"
        email = "chris@shenton.org"
        password = "koansyssandbox"
        account = "6951"
        entries = _get_bank_account_entries(domain, email, password, account)
        print entries
        # we don't know the bank account numbers or names
        # so just check we get a non-empty dict and an id is integer
        #self.assertEquals(type(accounts), dict)
        #self.assertNotEqual(len(accounts), 0)
        #self.assertTrue(int(accounts.keys()[0]))




