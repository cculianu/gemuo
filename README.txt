GemUO README
============

(c) 2005-2010 Max Kellermann <max@duempel.org>


What is GemUO?
--------------

GemUO is an Ultima Online client written in the Python programming
language.  It was written with unattended macroing in mind; it should
be possible to write complex bots for training skills, harvesting
resources or even fighting.


Getting GemUO
-------------

As of now, there are no releases.  GemUO is work in progress, and the
source must be downloaded from the git repository:

 git clone git://git.berlios.de/gemuo

This is the project's home page:

 http://max.kellermann.name/projects/gemuo/


Installation
------------

GemUO is being developed on Linux, but it probably runs on Windows,
too.  You need Python 2.5 to run it.


Running
-------

Type

 python src/hiding.py the.server.com 2593 username password CharName

This connects to the specified shard, and trains the Hiding skill.
There are other example macros.

It is recommended to run GemUO with uoproxy
(http://max.kellermann.name/projects/gemuo/) so you can watch the
scripts while they run.


Documentation
-------------

So far, there has been little time to write documentation on the code.
This project is aimed at hackers who can read the source.


Contributing
------------

Contributions to GemUO are welcome.  Send patches to max@duempel.org


Legal
-----

Copyright 2005-2010 Max Kellermann <max@duempel.org>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; version 2 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
