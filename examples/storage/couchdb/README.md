
## Couchdb 2.0.0 on Kubernetes
This document describes the steps to create a Couchdb 2.0.0 cluster on Kubernetes.

### Prerequisites
Access to a kubernetes cluster running v1.4 or later, kubectl installed and configured.  Minikube was used for this example. Note that the service type for the couchdb cluster is set to "NodePort" as the loadbalancer type is unsupported by minikube. 
 

### Creating the Configmaps and secrets 

Couchdb has erlang at its core and as such needs to be correctly configured to allow for clustering within Kubernetes.  There are currently three config files `vm.args`, `local.ini` and `default.ini` that are stored as blobs in a [ConfigMap](http://kubernetes.io/docs/user-guide/configmap/) found at `core-config-maps/core-configmap.yaml`. The `vm.args` file is where we set the erlang 'magic' cookie for all the couchdb instances alowing them to communicate with each other.  Before we get to creating our couchdb cluster these config maps need to be created:
```
kubectl create -f core-config-maps/core-configmap.yaml -f core-config-maps/cluster-adm.yaml 
configmap "core-config" created
secret "cluster-adm" created
```
#### Note on Admin users
We have populated the `local.ini` config file with user "admin" and the plain text password "changeme". On startup couchdb will hash the users password.  If you would like to define your own admin users then just add them to local.ini section of the core-config.  Also make sure that there is a valid admin user credentials in the cluster admin secret at `core-config-maps/cluster-adm.yam` bash64 encoded, naturally. This is needed for the utility pods if misconfiger we are going to have a bad time. 


### Creating the services 

Along with the erlang cookie, Couchdb instances need to have a static network identity.  This static identity is used to set the erlang node names for the couchdb instances.  To achieve this in Kubernetes petsets are leveraged giving every couchdb pod its own DNS name for its lifetime. 
  
There are two services we need to create for our couchdb cluster.  First theres the headless service for pod to pod discovery using DNS lookup and to give static hostname. Then we have the service that exposes the couchdb cluster. Let us create them:

```
kubectl create -f couchdb-petset-headless-service.yaml -f couchdb-petset-service.yaml 
service "kubetest001-backend" created
service "kubetest001" created
```

### Creating the PetSet
Now that we have the necessary configmaps, secrates and the services created let's create the couchdb petset!
```
kubectl create -f couchdb-petset.yaml 
petset "kubetest001" created
```
You can now checkout the kubernetes dash to see the newly create couchdb cluster.  If your running minikube you can discover the cluster address as follows: 
```
minikube service kubetest001 --url
http://192.168.99.102:31391
```
using that: 
```
curl  http://192.168.99.102:31391
{"couchdb":"Welcome","version":"2.0.0","vendor":{"name":"The Apache Software Foundation"}}
```

:tada:

