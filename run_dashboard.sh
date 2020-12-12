#!/bin/bash

PORT=$1
export MB_JETTY_PORT=$PORT
echo running Metabase on port $PORT
java -jar metabase.jar
