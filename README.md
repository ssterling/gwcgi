Greaseweazle CGI Interface
==========================

Web interface to Greaseweazle host tools.

The only sensible use case I can think of is something like mine,
in which my Greaseweazle and thus drives are connected to a PC other than
the one at my desk.
(To be fair, this was $80 cheaper than a dual 5¼″ drive bay enclosure.)

Installation
------------

Dependencies:
* Git
* Perl 5
* [websocketd](//github.com/joewalnes/websocketd)
* A webserver, e.g. Apache

Directions:
1. Clone this repository into somewhere served by your webserver, e.g.
   `/var/www/gwcgi`, and `cd` to that directory.
2. Clone the [greaseweazle repository](//github.com/keirf/greaseweazle).
   The `greaseweazle` directory created by Git should be in the same directory
   as this `README.md`.
3. Configure your webserver to allow CGI scripts to be executed in whatever
   directory you cloned this repository.
4. Set up Greaseweazle per
   [the wiki](https://github.com/keirf/greaseweazle/wiki/Software-Installation#linux).
5. Create a directory called `images` in the directory to which you cloned this
   repository.  Make it writable by the user which will be running `index.cgi`
   (probably `httpd` or `apache` or something).
6. Set up websocketd to run `gw-wrapper.sh` on port 8080
   (configurable by editing [`index.cgi`](index.cgi)):
   `websocketd --port 8080 ./gw-wrapper.sh` or something similar.

Notes
-----

* There are a few duplicate templates—e.g. 5¼″ quad-density and high-density formats
  both having 80 tracks at 96 TPI, thus using the same parameters when invoking
  Greaseweazle—, but these are to simplify the dropdown menu and to avoid having
  up to three density and/or BPI specifications on one entry.

To-do
-----

* Make the code suck less
* More configurability
* Include BPI info
