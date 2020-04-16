#!/usr/bin/env bash
docker run -ti -p 8080:80 \
  -v /shared-volume:/shared-volume:rw \
  -v /ssh-volume:/ssh-volume:rw \
  -v /var/run/docker.sock:/var/run/docker.sock \
  qassembler:latest $@