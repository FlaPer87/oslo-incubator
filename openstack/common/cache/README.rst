This is a work-in-progress design.

The idea is to create a generic caching library with support to multiple backends.

INSPIRATION
===========

I took some inspiration from Django's cache package.

METHODS
=======

Existing methods are documented and mostly self-explained. Although, there are a couple of other methods "missing".

Should this methods exist?
- incr
- decr


What other methods could be useful?

Back-Ends
=========

It would be nice to target this back-ends during the first release:

- memory
- memcached
- redis

