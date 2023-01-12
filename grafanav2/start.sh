#! /bin/bash

#### Fill up all the variable below
PD_INTEGRATION_KEY="<ur_pd_integration_key>"
ADMIN_USER="admin" #change if you want
ADMIN_PASSWORD="<urpwd>"

#### end

cp conf/alertmanager.yaml.tpl conf/alertmanager.yaml
sed -i "s/PD_SERVICE_KEY/${PD_INTEGRATION_KEY}/g" conf/alertmanager.yaml

ADMIN_USER=${ADMIN_USER} \
ADMIN_PASSWORD=${ADMIN_PASSWORD} \
GF_USERS_ALLOW_SIGN_UP=false \
PROMETHEUS_CONFIG="./data/prometheus.yml" \
GRAFANA_CONFIG="./data/grafana.ini" \
docker-compose up -d --remove-orphans --build "$@"

sudo chown -R $USER:$USER data