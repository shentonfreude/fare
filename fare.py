from webob import Response
from paste.httpserver import serve
from repoze.bfg.configuration import Configurator

def home(request):
    #return Response('fare home: get login creds, read accounts')
    return {'project': "Fare Project"}


def expense(request):
    return Response('GET or POST expense to picklist account, category')

if __name__ == '__main__':
    config = Configurator()
    config.begin()
    config.add_view(home, renderer="templates/home.pt")
    config.add_view(expense, name='expense')
    config.end()
    app = config.make_wsgi_app()
    serve(app)
