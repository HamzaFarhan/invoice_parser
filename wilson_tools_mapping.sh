#!/bin/bash
set -x
ZONE=us-central1-a
PROJECT_ID=red-night-393219
VMNAME=developervm
PORT_NO=8889
PORT_NOL=8889
PORT_NO2=8265
PORT_NOL2=8265

VM_INT_IP=$(gcloud compute  ssh --command='curl -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/ip' --zone "$ZONE" "$VMNAME" --project=$PROJECT_ID)
gcloud compute  ssh --ssh-flag="-L $PORT_NOL:$VM_INT_IP:$PORT_NO" --ssh-flag="-L $PORT_NOL2:127.0.0.1:$PORT_NO2" --zone "$ZONE" "hamza@$VMNAME" --project=$PROJECT_ID
