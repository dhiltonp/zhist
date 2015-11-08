#!/bin/bash

export ZPOOL=test_zhist_zpool1

# destroy zpool
zpool destroy -f $ZPOOL
echo rm `rm -v $ZPOOL`
