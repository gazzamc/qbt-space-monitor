# QBittorrent Space Monitor

This Docker container contains a python script that will manage qbittorrent downloads when space is limited.

## Note:
In QBittorrent, be sure to set all new downloads to pause when added.

# Docker Compose Example
Using **Ofelia** to schedule a check every 15mins

```
services:
    scheduler:
        image: mcuadros/ofelia:latest
        container_name: scheduler
        command: daemon --docker
        volumes:
        - /var/run/docker.sock:/var/run/docker.sock:ro
        labels:
        ofelia.job-run.qbt-monitor.schedule: "@every 15m"
        ofelia.job-run.qbt-monitor.container: "qbt-monitor"

    qbt-monitor:
        image: ghcr.io/gazzamc/qbt-space-monitor:latest
        container_name: qbt-monitor
        environment:
        - MINIMUM_SPACE=50G # Threshold in which the script will not resume the downloads, default=30g
        - QBITTORRENT_IP=192.168.1.14 # IP of Qbittorrent, default=127.0.0.1
        - QBITTORRENT_PORT=8080 #Optional
        - QBITTORRENT_USER=admin #Optional
        - QBITTORRENT_PASS=adminadmin #Optional
        - DOWNLOAD_DIR=downloads #Optional
        depends_on:
        - qbittorrent
        volumes:
        # Point to the same download folder as qbittorrent, will be used to determine space available
        - ~/path/to/downloads:/app/downloads:ro

```
