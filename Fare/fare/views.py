"""
 Get bank account list with:
 curl -u chris@koansys.com:PASSWORD
      -H 'Accept: application/xml' -H 'Content-Type: application/xml'
      https://koansys.freeagentcentral.com/bank_accounts

 POST transaction to bank id:

 curl -v
         -u chris@koansys.com:PASSWORD
	  -H 'Accept: application/xml'
	  -H 'Content-Type: application/xml'
	  --data @bankacctentry.xml
	  https://koansys.freeagentcentral.com/bank_accounts/ACCTNUM/bank_account_entries


   So: how do I find my bank account
 -->

<bank-account-entry>
 <bank-account-id type="integer">ACCTNUM</bank-account-id>
 <dated-on type="datetime">2010-01-06T00:00:00Z</dated-on>
 <description>TEST BANK ACCT ENTRY</description>
 <entry-type>Meals</entry-type>
 <gross-value type="decimal">-42.00</gross-value>
</bank-account-entry>
"""

from webob.exc import HTTPFound
import urllib2
from base64 import encodestring
import xml.etree.cElementTree as et
import logging
import datetime


logging.basicConfig(level=logging.DEBUG)

class FareError(Exception): pass
class NonXMLResponseError(FareError): pass
class BadAuthError(FareError): pass
class BadResponse(FareError): pass

def _get_response(domain, email, password, path, data=None):
    """Take auth creds, REST path, POST data, return HTTP response file hanele.
    If there's data, then urllib2 makes this a POST as needed.
    Response is XML, no JSON available (yet).
    """
    url = "https://%s.freeagentcentral.com/%s" % (domain, path)
    logging.info("_get_response url=%s" % url)
    print "# URL=%s" % url
    request = urllib2.Request(url, data,
                              headers={'Accept' : 'application/xml',
                                       'Content-Type' : 'application/xml'},
                              )
    base64string = encodestring('%s:%s' % (email, password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        site = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        # XXX wrongly catches 404=NotFound, 400=BadRequest too
        raise BadAuthError, "Authentication failed, check your username and password, ensure Settings->API is enabled (%s)" % e
    if not site.headers['content-type'].startswith("application/xml"):
        raise NonXMLResponseError, "Not an XML response, check your domain"
    return site

def _get_bank_accounts(domain, email, password):
    site = _get_response(domain, email, password, "bank_accounts")
    accounttree = et.parse(site)
    accounts = {}
    for acct in accounttree.findall('bank-account'):
        id = acct.findall('id')[0].text
        accounts[id] = acct.findall('name')[0].text
    return accounts

def _get_bank_account_entries(domain, email, password, account, range="?view=recent"):
    """Return list of transactions as list of dicts, defaulting to recent set.
    /bank_accounts/6951/bank_account_entries
    """
    # XXX It's giving us more than 10, don't show them to the user
    site = _get_response(domain, email, password, 
                         "bank_accounts/%s/bank_account_entries%s" % (account, range))
    tree = et.parse(site)
    entries = []
    # XXX Why is this so hard here?
    for e in tree.getroot().find('manual-entries').findall('bank-account-entry'):
        entry = {}
        entry['date']        = e.findall('dated-on')[0].text[:10]
        entry['description'] = e.findall('description')[0].text
        entry['category']    = e.findall('entry-type')[0].text
        entry['amount']      = e.findall('gross-value')[0].text
        entries.append(entry)
    return sorted(entries, key=lambda(k): k['date'], reverse=True)[:10]

    
def _get_expenses_types(domain, email, password):
    """Return list of expenses types to categorize expenses.
    Unfortunately, they're categorized oddly instead of using attributes,
    so we'll have to ask for each subset and then set the pulldown apprpriately.
    Need to make select option groups with the supertypes.
    <expense-types>
      <admin-expenses>
        <type>Accommodation</type>
        ...
      </admin-expenses>
      <cost-of-sales>
        <type>Commission Paid</type>
        ...
      </cost-of-sales>
      <capital-assets>
        <type>Purchase of Capital Asset</type>
        ...
      </capital-assets>
    </expense-types>

    """
    site = _get_response(domain, email, password, "expenses/types")
    tree = et.parse(site)
    uber_types = [('admin-expenses',[]), ('cost-of-sales',[]), ('capital-assets',[])]
    for uber,types in uber_types:
        for e in tree.getroot().find(uber).findall('type'):
            types.append(e.text)
        types.sort()
    return uber_types
        
def home(request):
    domain = email = password = message = ''
    if request.method == 'POST':
        domain =   request.POST['domain']
        email  =   request.POST['email']
        password = request.POST['password']
        # validate form
        if not (domain and email and password):
            message = 'You must fill in all the boxes'
        else:
            # auth and retrieve bank entries
            # pass bank info to expense rendering form (how? session?)
            response = HTTPFound(location="/expense")
            # XXX I should NOT be storing sensitive data in cookies
            # How to pass these to other pages? 
            response.set_cookie('domain_', domain)
            response.set_cookie('email', email)
            response.set_cookie('password', password)
            return response
    return dict(domain=domain, email=email, password=password, message=message)


class ExpenseForm(object):

    def __init__(self, **kwargs):
        """Create (empty) form from attrs"""
        logging.info("ExpenseForm init   kwargs.keys=%s" % kwargs.keys())
        for kw in kwargs.keys():
            setattr(self, kw, kwargs[kw])
        self.errors     = []

    def process_post(self, post):
        """Process a request.POST"""
        #type of POST is <instance>
        for attr in post.keys():            # need to compare with attrs in form.__dict__?
            setattr(self, attr, post[attr]) # default to '' if no attr??

    def is_valid(self):
        try:
            float(self.amount)
        except ValueError, e:
            self.errors.append("Amount must be numeric (%s)" % e)
        if self.errors:
            return False
        return True
        



def expense(request):
    #message = ''
    domain = request.cookies['domain_']
    email = request.cookies['email']
    password = request.cookies['password']
    accounts = _get_bank_accounts(domain, email, password)
    logging.info("expense accounts=%s" % accounts)

    # category selection done in HTML in the template

    (date_year, date_month, date_day) = datetime.date.today().isoformat().split('-')
    form = ExpenseForm(domain=domain, email=email,
                       accounts=accounts, account='',
                       date_year=date_year, date_month=date_month, date_day=date_day,
                       amount='', description='', category='',
                       entries=[])
    if request.method == 'POST':
        form.process_post(request.POST)
        if form.is_valid():     # if not, sets form.errors
            logging.info("expense post form=%s" % form)
            data = """
<bank-account-entry>
 <bank-account-id type="integer">%(account)s</bank-account-id>
 <dated-on type="datetime">%(date_year)s-%(date_month)s-%(date_day)sT00:00:00Z</dated-on>
 <description>%(description)s</description>
 <entry-type>%(category)s</entry-type>
 <gross-value type="decimal">-%(amount)s</gross-value>
</bank-account-entry>
""" % form.__dict__
            logging.info("expense post form data=%s" % data)
            response = _get_response(domain, email, password,
                                     "/bank_accounts/%s/bank_account_entries" % form.account,
                                     data)
            if response.code == 201:
                message = "%s %s" % (response.msg, response.headers['location'])
                form.entries = _get_bank_account_entries(domain, email, password, form.account)
                form.entries_account = accounts[form.account]
            else:
                message = "Something bad? %s %s" % (response.code, response.msg)
            form.message = message
            return form.__dict__
    # Method is GET or POST form invalid
    form.message = "new form"
    return form.__dict__
