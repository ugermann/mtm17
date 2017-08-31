#!/bin/bash

while true
do
  echo "sleep 1 ; echo 'I got command and executed it!'" | nc -l 9898
done
