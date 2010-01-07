"""
 Get bank account list with:
 curl -u chris@koansys.com:PASSWORD
      -H 'Accept: application/xml' -H 'Content-Type: application/xml'
      https://koansys.freeagentcentral.com/bank_accounts

 Extract name=Checking id=6667 bank-name=Burke&Herbert

 POST transaction to bank id:

 curl -v
         -u chris@koansys.com:PASSWORD
	  -H 'Accept: application/xml'
	  -H 'Content-Type: application/xml'
	  --data @bankacctentry.xml
	  https://koansys.freeagentcentral.com/bank_accounts/6677/bank_account_entries


   So: how do I find my bank account
 -->

<bank-account-entry>
 <bank-account-id type="integer">6677</bank-account-id>
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

class FareError(Exception): pass
class NonXMLResponseError(FareError): pass
class BadAuthError(FareError): pass
class BadResponse(FareError): pass

def _get_response(domain, email, password, path, data=None):
    """Take auth creds, REST path, POST data, return HTTP response file hanele"""
    # boo hoo: no application/json response type
    # if data, then it's a POST
    request = urllib2.Request("https://%s.freeagentcentral.com/%s" % (domain, path),
                              data,
                              headers={'Accept' : 'application/xml',
                                       'Content-Type' : 'application/xml'},
                              )
    base64string = encodestring('%s:%s' % (email, password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        site = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
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
        name = acct.findall('name')[0].text
        accounts[id] = name
    return accounts

    
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


def expense(request):
    message = ''
    domain = request.cookies['domain_']
    email = request.cookies['email']
    password = request.cookies['password']
    accounts = _get_bank_accounts(domain, email, password)
    # category selection done in HTML in the template

    if request.method == 'POST':
        values = dict(
            account=request.POST['account'],
            amount=request.POST['amount'],
            date=request.POST['date'],
            description=request.POST['description'],
            category=request.POST['category'],
            )
        # validate form: TODO: need more, like date (want picker)
        import pdb; pdb.set_trace()
        try:
            _famount = float(values['amount'])
        except ValueError:
            message = 'The amount must be an integer or floating point value'
        else:
            data = """
<bank-account-entry>
 <bank-account-id type="integer">%(account)s</bank-account-id>
 <dated-on type="datetime">%(date)sT00:00:00Z</dated-on>
 <description>%(description)s</description>
 <entry-type>%(category)s</entry-type>
 <gross-value type="decimal">-%(amount)s</gross-value>
</bank-account-entry>
""" % values
            response = _get_response(domain, email, password,
                                     "/bank_accounts/%s/bank_account_entries" % values['account'],
                                     data)
            if response.code == 201:
                message = "%s %s" % (response.msg, response.headers['location'])
            else:
                message = "Something bad? %s %s" % (response.code, response.msg)
            return dict(domain=domain, email=email,
                        message=message, accounts=accounts)

    return dict(domain=domain, email=email,
                message=message,accounts=accounts)
