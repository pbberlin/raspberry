# backup from SSD to classic disk 
#   performs with approx 10 MB/s

screen -r backup

year_month=$(date +"%y_%m")
mkdir -p /media/pbu/1tb_2022/b_$year_month
rsync -av --progress /media/pbu/T7/media/ /media/pbu/1tb_2022/b_$year_month/
