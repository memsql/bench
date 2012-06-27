MemSQL Benchmark Tools
======================

This tool is a set of scripts that let you benchmark MemSQL, MySQL, and MongoDB as described in [Reading Between the Benchmarks](http://developers.memsql.com/blog/reading-between-the-benchmarks/). It simulates a multiplayer 
game by running queries against a database.

The benchmark is easy to get up and running, and we encourage you to both run it on your own and extend it to test your favorite database/configuration.

Requirements
------------

We've only tested it on Linux, but there should be nothing preventing it from running on similar \*nix systems. 

You'll need to install a few Python packages (through ``easy_install`` or ``pip``):

 + pymongo
 + MySQL-python  (requires libmysqlclient-dev and python-dev)


Configuring
-----------

The benchmark configuration is in config.py. The fields are explained inline, and you should visit this
file to adjust things like:

 + Which database to connect to and where
 + How many worker processes to use
 + Whether or not to enable printing statistics
 + How long the simulation runs

Running
-------

After you've tweaked the configuration options in config.py, just run benchmark with
```
python benchmark.py
```
