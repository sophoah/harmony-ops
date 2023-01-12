# Monitoring stack for Harmony

## Description
This Monitoring stack is made of :
- grafana for the viewing of the graph
- node_exporter to monitor harmony host
- prometheus to capture the metrics and make it available for Grafana
- loki to display logs
- promtail to send logs to loki
- alertmanager integrated with pagerduty

## Prereq

haqqd logs are assumed to be coming from journalctl

For this to work you'll need sudo privilege to do do a one off install of docker

```bash
# install docker / docker-compose
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-compose docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker $USER #you need to logout and login back after that
```

node needs to have prometheus telemetry configured.

## Installing the stack

### Clone the repo

```bash
git clone https://github.com/harmony-one/harmony-ops
cd harmony/grafanav2
```

### Update start.sh

- update the admin/password of your grafana
- Next, If you wanna be alerted, you will need to create an account on pagerduty and get your integration key https://support.pagerduty.com/docs/services-and-integrations

> alertmanager will fail to start if the PD integration key is not filled up 


### Start the stack

```bash
bash start.sh
```


