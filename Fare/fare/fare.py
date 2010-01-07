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

from webob import Response
from webob.exc import HTTPFound
import urllib2
from base64 import encodestring
import xml.etree.cElementTree as et

class FareError(Exception): pass
class NonXMLResponseError(FareError): pass
class BadAuthError(FareError): pass
class BadResponse(FareError): pass

def _get_bank_accounts(domain, email, password):
    # boo hoo: no application/json response type
    request = urllib2.Request("https://%s.freeagentcentral.com/bank_accounts" % domain,
                              headers={'Accept' : 'application/xml',}
                              #'Content-Type' : 'application/xml'})
                              )
    base64string = encodestring('%s:%s' % (email, password))[:-1]
    request.add_header("Authorization", "Basic %s" % base64string)
    try:
        site = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        raise BadAuthError, "Authentication failed, check your username and password, ensure Settings->API is enabled (%s)" % e
    if not site.headers['content-type'].startswith("application/xml"):
        raise NonXMLResponseError, "Not an XML response, check your domain"
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
    import pdb; pdb.set_trace()
    return dict(domain=domain, email=email, password=password, message=message)
