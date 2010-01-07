from repoze.bfg.configuration import Configurator
#from fare.models import get_root
from fare import home, expense

def app(global_config, **settings):
    """ This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
#if __name__ == '__main__':
    config = Configurator()
    config.begin()
    config.add_view(home, renderer="templates/home.pt")
    config.add_view(expense, name='expense', renderer='templates/expense.pt')
    config.end()
#    app = config.make_wsgi_app()
#    serve(app)
    return config.make_wsgi_app()

#     zcml_file = settings.get('configure_zcml', 'configure.zcml')
#     config = Configurator(root_factory=get_root, settings=settings)
#     config.begin()
#     config.load_zcml(zcml_file)
#     config.end()
#    return config.make_wsgi_app()
