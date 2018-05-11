About libjpeg-turbo
===================

Home: http://www.libjpeg-turbo.org/

Package license: IJG, modified 3-clause BSD and zlib

Feedstock license: BSD 3-Clause

Summary: IJG JPEG compliant runtime library with SIMD and other optimizations
Can be mixed with libjpeg >= 9:
  - Library files live in custom locations
  - Public symbols are prefixed with "turbo_"
  - Provided headers allow to keep using standard libjpeg API




Current build status
====================

[![Linux](https://img.shields.io/circleci/project/github/gaiar/libjpeg-turbo-feedstock/master.svg?label=Linux)](https://circleci.com/gh/gaiar/libjpeg-turbo-feedstock)
![OSX disabled](https://img.shields.io/badge/OSX-disabled-lightgrey.svg)
![Windows disabled](https://img.shields.io/badge/Windows-disabled-lightgrey.svg)

Current release info
====================

[![Conda Downloads](https://img.shields.io/conda/dn/gaiar/libjpeg-turbo.svg)](https://anaconda.org/gaiar/libjpeg-turbo)
[![Conda Version](https://img.shields.io/conda/vn/gaiar/libjpeg-turbo.svg)](https://anaconda.org/gaiar/libjpeg-turbo)
[![Conda Platforms](https://img.shields.io/conda/pn/gaiar/libjpeg-turbo.svg)](https://anaconda.org/gaiar/libjpeg-turbo)

Installing libjpeg-turbo
========================

Installing `libjpeg-turbo` from the `gaiar` channel can be achieved by adding `gaiar` to your channels with:

```
conda config --add channels gaiar
```

Once the `gaiar` channel has been enabled, `libjpeg-turbo` can be installed with:

```
conda install libjpeg-turbo
```

It is possible to list all of the versions of `libjpeg-turbo` available on your platform with:

```
conda search libjpeg-turbo --channel gaiar
```




Updating libjpeg-turbo-feedstock
================================

If you would like to improve the libjpeg-turbo recipe or build a new
package version, please fork this repository and submit a PR. Upon submission,
your changes will be run on the appropriate platforms to give the reviewer an
opportunity to confirm that the changes result in a successful build. Once
merged, the recipe will be re-built and uploaded automatically to the
`gaiar` channel, whereupon the built conda packages will be available for
everybody to install and use from the `gaiar` channel.
Note that all branches in the gaiar/libjpeg-turbo-feedstock are
immediately built and any created packages are uploaded, so PRs should be based
on branches in forks and branches in the main repository should only be used to
build distinct package versions.

In order to produce a uniquely identifiable distribution:
 * If the version of a package **is not** being increased, please add or increase
   the [``build/number``](http://conda.pydata.org/docs/building/meta-yaml.html#build-number-and-string).
 * If the version of a package **is** being increased, please remember to return
   the [``build/number``](http://conda.pydata.org/docs/building/meta-yaml.html#build-number-and-string)
   back to 0.