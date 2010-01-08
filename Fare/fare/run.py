from repoze.bfg.configuration import Configurator
from views import home, expense

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    config = Configurator()
    config.begin()
    config.add_view(home, renderer="templates/home.pt")
    config.add_view(expense, name='expense', renderer='templates/expense.pt')
    config.end()
    return config.make_wsgi_app()
