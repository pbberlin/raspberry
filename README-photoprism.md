### MediaServer - DONT 

* openmediavault was a huge conglomerate of node, python and PHP.
* it only works on the non-desktop version of Raspian
* I think over complicated and does not provide much use for home media


[openmediavault installieren](https://carsten-nichte.de/docs/mediaserver-mit-raspberry-pi/)
[auch](https://www.openmediavault.org/screenshots.html)

=> Benötigt Raspian __lite__  - ohne Desktop

https://wiki.omv-extras.org/doku.php?id=omv7:raspberry_pi_install



* Jellyfin Webclient - Media server


## Photoprism auf Raspberry Pi

Remove previous failed stuff

```bash
# removing containers, volumes, networks AND IMAGES:
sudo docker system prune -a

# better
sudo docker rm pbu_photoprism_1

# no volumes
sudo docker volume ls


# in ~/storage   and everywhere:
rm .ppignore
rm .ppstorage
```

Clean state

```bash
# as normal user
wget https://dl.photoprism.app/docker/arm64/docker-compose.yml

nano docker-compose.yml
# only edit volume pointing to the original files / sources; i.e.
#     - "/media/pbu/T7/dropbox-24-09/img:/photoprism/originals"
# edit the admin user name and password


# cd to docker-compose.yml
cd ~
sudo docker-compose up -d

sudo docker-compose up -d

# check logs
sudo docker-compose logs -f --tail=100


# bad - use commands below
#  DONT USE -start
sudo docker ps -a
sudo docker stop  pbu_photoprism_1
sudo docker stop  pbu_mariadb_1
sudo docker start pbu_photoprism_1
sudo docker start pbu_mariadb_1
#  DONT USE -end




```

Wait 50 secs and call

[check UI 1](http://localhost:2342/)

[check UI 2](http://192.168.1.102:2342/)


### Updating - restarting of Photoprism

[see](https://docs.photoprism.app/getting-started/updates/)

```bash
docker compose pull
docker compose stop
docker compose up -d
```

[adding folders](https://docs.photoprism.app/getting-started/advanced/docker-volumes/)


[docker compose commands](https://docs.photoprism.app/getting-started/docker-compose/) - start and stop etc.

It seems, that folders can only be added at creation time?
I added:
    - "/media/pbu/T7/dropbox-24-09/video:/photoprism/originals/video"
and restarted, but nothing happened

I tried to add ~/storage/config/options.yml
        it was found upon restart - but the multi line syntax was rejected

