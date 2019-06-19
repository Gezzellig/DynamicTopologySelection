kubectl create clusterrolebinding varMyClusterRoleBinding \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:default
