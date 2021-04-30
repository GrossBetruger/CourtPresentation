#!/bin/bash

PORT=${1:-7777}
export MB_JETTY_PORT=$PORT
echo running Metabase on port $PORT
java -Xmx6g -jar metabase.jar
