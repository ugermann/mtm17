for p in 50001 50004  50000  50003  50005  50007  50008  50009  50010  50011  50013  50014  50015  50016  50020  50021  50023  50024  50026  50027  ; do echo $p;  ssh -i /home/big_maggie/data/project/geneticke_algoritmy/azure_key -p $p michal@13.84.180.248 'chmod +x ~/val*sh &' ; done
 # 
