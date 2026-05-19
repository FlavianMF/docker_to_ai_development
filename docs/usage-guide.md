# Usage Guide

## Build Image
`docker build -t hermes-docker .`

## Interactive Dev
1. Run container: `docker run -it -v $(pwd):/workspace hermes-docker`
2. Inside: `hermes`

## File Persistence
Mount host dirs to `/workspace`. Changes stay on host.
