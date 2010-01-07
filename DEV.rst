================================================
 Getting BFG running simply for Fare with no DB
================================================

Checkout the code from GitHub.

Make a virtualenv for it::

 /usr/local/python/2.6.4/bin/virtualenv --no-site-packages ~/.virtualenvs/fare
 source ~/.virtualenvs/fare/bin/activate

Follow the Repoze BFG instructuctions::

 easy_install -i http://dist.repoze.org/bfg/1.2/simple repoze.bfg

Maybe punt on this?
===================

I can get a skeleton setup (without SQL or ZODB database)::

  paster create -t bfg_starter Fare
  cd Fare
  python setup.py develop

It didn't need to install anything that wasn't already installed by
the easy_install.  So perhaps I didn't need to do this, but it's nice
I don't have to create my own structure (setup.py, etc) from scratch.

I always forget about this, but you can get a python shell loaded up
with stuff your project uses::

  paster bfgshell Fare.ini main

Hmmm, this isn't working for me::

  $ paster bfgshell Fare.ini main
  Command 'bfgshell' not known (you may need to run setup.py egg_info)
