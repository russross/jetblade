JetBlade's only major dependencies are on Python (2.5 or 2.6), PyGame, and Cython. You will also need Mercurial to download the source code.

  * Install python 2.5 from [here](http://www.python.org/ftp/python/2.5.4).
  * Go to [pygame.org](http://www.pygame.org/) and download the appropriate installation package. I think you might need ctypes installed also.
  * Go to [cython.org](http://www.cython.org/) and download their latest release. Unfortunately they don't have binaries available on all platforms, so you may need to install Cython manually. Download the "latest release" source, open a terminal (e.g. on OSX, open Applications/Utilities/Terminal), head to the place you downloaded Cython, and run "python setup.py install".
  * Install mercurial, from [here](http://mercurial.berkwood.com/).
  * Go to a directory you want to keep all your programmin' stuffs. For example,
<pre>cd Applications</pre>
  * Run this:
<pre>hg clone https://jetblade.googlecode.com/hg/ jetblade</pre>
  * Once it finishes downloading, run this:
<pre>cd jetblade</pre>
<pre>python jetblade.py</pre>