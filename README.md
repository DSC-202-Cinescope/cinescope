# DSC202 Winter '25
## Cinescope: TMDB Relational Genre Viewer 
### Featuring Verticle and Horizontal Scaling, Postgres, Neo4J, and Redis on the Nautilus Kubernetes Platform
### Cinescope can be viewed publically (until 3/30) at cinescope.nrp-nautilus.io

Group:
Joel Polizzi, Dongting Cai, Xuanwen Hua

TMDB (The Movie Database) provides a rich database suitible for relational querying. The Cinescope project has developed a development to production pipeline to do relational searching in Postgres and Neo4J utilizing data from TMDB. Furthermore, Cinescope experiments with verticle and horizontal scalling of software services and databases and has been deployed in a highly reproducible way: leveraging cloud-native infrastructure and storing our infrastructure deployments in YAML files.

#### Follow the instructions will guide you through deploying cinescope on your own. 
#### The Cinescope instructions are intended to be ran in a Linux environment. If you wish to deploy on Windows or Mac, you may do so however the project was developed in Linux and the documentation is Linux specific. If you proceed outside of a linux environment then to the best of my knowledge the only difference will be in the installation instructions of Git and Git-Lfs.

## Table of Contents
- [Infrastructure Deployment](#infrastructure)
- [Connecting from external services](#external_connections)
- [Front-end Access](#live)
- [Project Report](#project-report)
- [Slides](#Slides)

## Requirements:
1)  Ubuntu 22:04
2)  Git package installation
3)  Git-lfs
4)  Nautilus login.

## Nautilus Access
Nautilus is the platform we deployed Cinescope on. Access is available to UCSD students and staff. 
To gain access follow this link and login with your University provider:
https://portal.nrp-nautilus.io/
<picture of nautilus>
Once you gain access you will need to copy your kubernetes config file to your home directory.
<screen shot the key copy process>

## Installing Git and Git-LFS
apt-get update && apt-get install git git-lfs -y

##To launch and connect
1) Clone down our repository
git clone https://github.com/DSC-202-Cinescope/cinescope.git

2) Launch the postgres cluster
kubectl apply -f infra/postgres-deploy.yaml

3) Use port forwarding to access the database through Datagrip
kubectl port-forward cinescope-postgres-cluster-0 5432:5432 

