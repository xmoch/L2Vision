
################################################################################
#
# L2Vision README
# by zdev
#
################################################################################

------------
REQUIREMENTS
------------

You need to have Python installed on your box. You can get the Python package
from www.python.org. They have downloadables for Windows/Linux/Mac on their
site.

Note that most Linux/Mac users will find that python is already installed on
their machines by default. You really only need to go to the site and download
the installer if you're running on Windows.

-------
RUNNING
-------

By being able to read this file, I'm guessing you already downloaded this
package and decompressed it. Please leave the package as is.

The following instructions are Linux/Mac specific but it should be nearly the
same on a Windows box with Python installed.

  cd L2Vision
  python Launch.py [port]

For 'port', if you don't specify it, it will run on port 8000. If you specify it,
it will use that port instead. Once you have it running, open a web browser on
any computer that can reach the computer running L2Vision and enter the URL:

  http://machine_ip_addr:8000/

Replace 'machine_ip_addr' with the IP address of the machine running L2Vision.
Replace '8000' with the port you specified if you used something other than the
default port 8000.

That's it!

Remember, you won't see any characters in the main web page if no characters
have reported data from L2.Net. You need to make sure the L2.Net code snippet
is running in L2.Net to see any results in the L2Vision web page.

-----
FILES
-----

This is a short description of the files inside this package.

TOPLEVEL
  |
  +-- data/         ;; static images/CSS files used by L2Vision server
  +-- django/       ;; django open source web server (v1.1.1) unmodified
  +-- __init__.py   ;; python module file, empty but needed
  +-- l2v/          ;; L2Vision source files
  +-- L2Vision.l2s  ;; L2.Net code snippet needed for L2Vision
  +-- Launch.py     ;; python script to launch L2Vision
  +-- README.txt    ;; this file!
  +-- settings.py   ;; django settings file, no need to modify this
  +-- urls.py       ;; django dispatch file, no need to modify this
