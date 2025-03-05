#!/bin/bash

apt-get update 
apt-get install git
git config --global user.email $1
git config --global user.name $2
git config --list
