# Cinescope: 
## Relationsal Genre Viewer Featuring Verticle and Horizontal Scaling, Postgres, Neo4J, and Redis on the Nautilus Kubernetes Platform
### Cinescope can be viewed publically (until 3/30) at cinescope.nrp-nautilus.io

## Follow the instructions on how to deploy cinescope on your own.

# The Cinescope instructions are intended to be ran in a Linux environment. If you wish to deploy on Windows or Mac, you may do so however the project was developed in Linux and the documentation is Linux specific. 

# Requirements:
# 


Our central postgres database is located on the Nautilus Kubernetes Cluster.

To launch and connect
1) Clone down our repository
git clone https://github.com/DSC-202-Cinescope/cinescope.git

2) Launch the postgres cluster
kubectl apply -f infra/postgres-deploy.yaml

3) Use port forwarding to access the database through Datagrip
kubectl port-forward cinescope-postgres-cluster-0 5432:5432 

