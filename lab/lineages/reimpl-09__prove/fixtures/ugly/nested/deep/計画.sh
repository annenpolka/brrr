#!/bin/sh
# $DUE_COMMENTED should not count
echo "${DUE_HOME}/state"
echo "$DUE_PORT"
curl -H "x: $DUE_API_KEY" example.test
