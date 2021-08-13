# Fontsearch

A Python script for Linux that finds installed fonts that support a given
character.

Tested on Ubuntu 20.04.

## Getting started

You need to have `make` and `virtualenv` installed for this to work.

Before searching, navigate into the cloned directory and set up the Python
environment using:

```sh
make virtualenvs
```

This will create a virtual Python environment and install the necessary
packages into it.

After that, activate the virtualenv by typing:

```sh
. virtualenvs/py3/bin/activate
```

You have to activate the virtualenv each time before searching for characters.
After that, you can search for a character `character` as follows:

```sh
./fontsearch.py "${character}"
```

The script may output information to `stderr` about files for which it cannot
determine whether the character is supported. If you wish to suppress that
output, simply re-route `stderr`:

```sh
./fontsearch.py "${character}" 2> /dev/null
```

To see more options, type the following:

```sh
./fontsearch.py --help
```

When you are done, you can deactivate the Python environment using:

```sh
deactivate
```

## Documentation

To get help on how to use `fontsearch.py`, to see the supported font formats,
or to see all command options, type the following with the Python virtualenv
activated:

```sh
./fontsearch.py --help
```

For help on the makefile options (mostly of interest for developers), type:

```sh
make help
```
