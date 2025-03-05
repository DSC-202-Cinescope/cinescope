# Infrastructure 

Our central postgres database is located on the Nautilus Kubernetes Cluster.

To launch and connect
1) Clone down our repository
git clone https://github.com/DSC-202-Cinescope/cinescope.git

2) Launch the postgres cluster
kubectl apply -f infra/postgres-deploy.yaml

3) Use port forwarding to access the database through Datagrip
kubectl port-forward cinescope-postgres-cluster-0 5432:5432 

