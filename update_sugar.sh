#!/usr/bin/bash

cd /usr/src/sugar && (
./autogen.sh --prefix /usr \
&& make \
&& make install \
&& rm -rvf /usr/lib/python3.7/dist-packages/jarabe/ \
&& mv -v /usr/lib/python3.7/site-packages/jarabe /usr/lib/python3.7/dist-packages/
) > /usr/src/install-sugar.log 2>&1 \
&& echo OK
