for p in  50000 50027 50003  50004  50005  50007  50008  50009  50010  50011  50013  50014  50015  50016  50020  50021  50023  50024  50026  ; do echo $p; ssh -p $p michal@13.84.180.248 'df -h | wc -l' ; done