# envfrom

Kubernetes [Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) or [ConfigMap](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#create-a-configmap) are commonly used to run apps deployed in pods.

But what about running this app locally with those same variables ? envfrom meet this need among others like [envdir](https://cr.yp.to/daemontools/envdir.html) or [.env](https://github.com/motdotla/dotenv).

### Installation
    pip install envfrom

### Usage

    usage: -m [-h] {cli,dir,dotenv,kube} ... child

    Call child process with custom environment

    positional arguments:
        {cli,dir,dotenv,kube}
                            env source
        cli                 Dict values: FOO=BAR BAR=FOO
        dir                 Set environment according to files in a specified path
        dotenv              Set environment according to .env file
        kube                Mirror specified kubernetes ressource volume keys (decoded)
        child                 child process

    optional arguments:
        -h, --help            show this help message and exit

### Kubernetes secrets example
Assuming that you already have the following secret created on your default namespace :

    
	apiVersion: v1
	kind: Secret
	metadata:
	  name: mysecret
	type: Opaque
	data:
	  username: YWRtaW4=
	
Running :

    env -i envfrom kube secrets mysecret env

Should output :

    username=admin


