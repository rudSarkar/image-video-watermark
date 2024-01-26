#!/bin/bash

docker build -t imagewatermark .

docker run -p 5000:5000 imagewatermark
