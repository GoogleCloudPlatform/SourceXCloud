
SourceXCloud - a Framework for deploying from any Source to any Cloud Target
============================================================================

SourceXCloud is an experimental pluggable framework for deploying directly
from any source environment to any target cloud environment. This is
alpha-quality code, expect difficulties.

This code is provided as a demonstration of a concept, not as production-ready
code.  We will accept patches, and it may receive development attention if
enough people find it useful, but in general: use it at your own risk.

Using the Framework
-------------------

The SourceXCloud ("sxc" for short) libraries and tools let you:

- Determine what kind of source directory you are using.
- Construct an Intermediate Representation ("IR") of the deployable contents
  of that directory and its versioned dependencies.
- Deploy a runtime based on the directory to one of a number of different
  cloud platforms.

The modules that do source recognition and IR generation are called
"aggergators."  The modules that deploy from IR to target platforms are called
"actuators."  These are installed in the "extensions" subdirectory and consist
of binary hook files and data files.

Example of pushing a source directory

    $ cd myDjangoDir
    $ sxc push . gaemvm
    copying files
    generating dockerfile
    adding install hook: u'/usr/bin/python /app/manage.py syncdb'
    generating app.yaml
    gcloud: 10:28 AM Host: appengine.google.com
    gcloud: Updating module [default] from file [/tmp/tmp2jNkIH/app.yaml]
    gcloud: {bucket: vm-containers.organic-lacing-568.appspot.com, path: /containers}
    gcloud:
    ...

There are currently two supported aggregators (django and node.js) and two
supported actuators (Google App Engine Managed VMs and Digital Ocean VMs).

For more extensive documentation, see the source code.

License and Disclaimers
-----------------------

Copyright 2015 Google Inc.

[Licensed under the Apache License, version 2.0](LICENSE)

Contributions are welcome. Please, see the CONTRIBUTING document for details.

This is not an official Google product (experimental or otherwise), it is
just code that happens to be owned by Google.

This is experimental code.  The interfaces in this package, both the library API
and hook protocols, are subject to change without notice.
