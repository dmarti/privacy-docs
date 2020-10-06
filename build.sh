#!/bin/bash

# Run this script from the directory where it is installed.
trap popd EXIT
pushd $PWD &> /dev/null
cd $(dirname "$0")

dockerfail() {
	echo
	echo "Docker not found. Check that Docker is installed and running."
	echo
	exit 1
}
docker ps &> /dev/null || dockerfail

set -e
set -x

docker build --tag=make_letters .

docker run --volume "$(pwd)":/docs:rw,Z \
	--entrypoint make \
	make_letters

rm -rf tmp
