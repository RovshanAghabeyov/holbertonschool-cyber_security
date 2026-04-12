#!/bin/bash
awk -F'"' '{print $6}' log.txt  | sort | uniq -c | sort -nr | head -n1 | awk '{print $2}'

