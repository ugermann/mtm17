# coding=utf-8
from collections import OrderedDict
def prubeh():
	text=''' 

	"estoy"+gerund+"melo"=prub1j+"mě to"/prub1j+"mi to"/prub1j+"si to"/prub1j+"mi ho"/prub1j+"si ho"
	"estoy"+gerund+"telo"=prub1j+"tě to"/prub1j+"ti to"/prub1j+"si to"/prub1j+"ti ho"/prub1j+"si ho"
	"estoy"+gerund+"selo"=prub1j+"ho to"/prub1j+"mu to"/prub1j+"si to"/prub1j+"mu ho"/prub1j+"si ho"
	"estoy"+gerund+"noslo"=prub1j+"nás to"/prub1j+"nám to"/prub1j+"si to"/prub1j+"nám ho"/prub1j+"si ho"
	"estoy"+gerund+"oslo"=prub1j+"vám to"/prub1j+"jim to"/prub1j+"si to"/prub1j+"jim ho"/prub1j+"si ho" '''

	tvary={"estás;":"prub2j","está;":"prub3j","estamos;":"prub1m", "estáis;":"prub2m", "están;":"prub3m"}
	ret=""
	for v in tvary:
		#print v	
		second=tvary[v]
		ret+=text.replace("estoy",v).replace("prub1j",second)+"\n\n"

	return ret

def gerund():
	pass

def imper():
	pronouns={"me":["mi","mně","mě","si","se", "na mě", "na sebe", "se mnou"],"te":["ti","tě","si","se", "na tebe", "na sebe", "s tebou"],"le":["mu","ho","si","se", "na něj", "na sebe", "s ním"],"lo":["to","na to", "s tím"],
 "la":["jí","ji", "na ni", "s ní"], "nos":["nám","nás","na nás","s námi","se"] ,"os":["vám","vás","na vás", "s vámi", "se"],"les":["jim" ,"je","na ně","s nimi","se"],"las":["jim" ,"je","na ně","s nimi","se"],"los":["jim" ,"je","na ně","s nimi","se"],\
"melo":["mi to", "mi ho","si to","si ho"], "telo":["ti to", "ti ho","si to","si ho"],"selo":["jí ho","jí to","mu to", "mu ho","si to","si ho"], "noslo":["nám to","nám ho","si to","si ho" ],"oslo":["vám to","vám ho","si to","si ho" ], \
"mela":["mi to", "mi ji","si to","si ji"], "tela":["ti to", "ti ji","si to","si ji"],"sela":["jí ji","jí to","mu to", "mu ji","si to","si ji"], "nosla":["nám to","nám ji","si to","si ji" ],"osla":["vám to","vám ji","si to","si ji" ], \
"melos":["mi to", "mi je","si to","si je"], "telos":["ti to", "ti je","si to","si je"],"selos":["jí je","jí to","mu to", "mu je","si to","si je"], "noslos":["nám to","nám je","si to","si je" ],"oslos":["vám to","vám je","si to","si je" ], \
"melas":["mi to", "mi je","si to","si je"], "telas":["ti to", "ti je","si to","si je"],"selas":["jí je","jí to","mu to", "mu je","si to","si je"], "noslas":["nám to","nám je","si to","si je" ],"oslas":["vám to","vám je","si to","si je" ] \
}
	ret=""
	for p in pronouns:
		ret+='imper+"'+p+'"='
		for v in pronouns[p]:
			ret+='imper + "'+v +'" '
			if (len(pronouns[p])>1 and (pronouns[p].index(v)+1)!=len(pronouns[p])):
				ret+="/ "
 
		ret+="\n"
	return ret


def inf():
	text='''
		inf+"me"=inf + "mi" /inf + "mě" / inf + "na mě"/ inf + "na sebe"/inf + "se"
		inf+"te"=inf + "ti"  /inf + "tě" / "tě" + inf/ inf + "na tebe"/ inf + "na sebe"/inf+"se"
		inf+"le"=inf + "mu" /inf + "ho" / inf + "na něj"/ inf + "na sebe"/inf+"se"
		inf+"lo"=inf + "to" 
		inf+"se"=inf + "se" 
		inf+"la"=inf + "jí" /inf + "ji" / inf + "na ni"/ inf + "na sebe"/inf+"se"
		inf+"nos"=inf + "nám" /inf + "nás" / inf + "na nás"/ inf + "na sebe"/inf+"se"
		inf+"os"=inf + "vám"  /inf + "vás"/ inf + "na vás"/ inf + "na sebe"/inf+"se"
		inf+"les"=inf + "jim" /inf + "je" / inf + "na ně"/ inf + "na sebe"/inf+"se"
		inf+"los"=inf + "jim"  /inf + "je" /  inf + "na ně"/ inf + "na sebe"/inf+"se"
		inf+"las"=inf + "jim"  /inf + "je" /  inf + "na ně"/ inf + "na sebe"/inf+"se"

		inf+"melo"=inf + "mi to" / inf + "mi ho"/ inf + "si to" / inf + "si ho" /
		inf+"telo"=inf + "ti to" / inf + "ti ho" / inf + "si to" / inf + "si ho" /
		inf+"selo"=inf + "mu to" / inf + "mi ho"/ inf + "si to" / inf + "si ho" /
		inf+"noslo"=inf + "nám to" / inf + "nám ho"/ inf + "si to" / inf + "si ho" /
		inf+"oslo"=inf + "vám to" /inf +  "vám ho"/ inf + "si to" / inf + "si ho" /

		inf+"mela"=inf + "mi to" / inf + "mi ji"/ inf + "si to" / inf + "si ji" /
		inf+"tela"=inf + "ti to" / inf + "ti ji"/ inf + "si to" / inf + "si ji" /
		inf+"sela"=inf + "mu to" / inf + "mu ji"/ inf + "si to" / inf + "si ji" / inf + "jí to" / inf + "jí ji"
		inf+"nosla"=inf + "nám to" / inf + "nám ji"/ inf + "si to" / inf + "si ji" /
		inf+"osla"=inf + "vám to" / inf + "vám ji"/ inf + "si to" / inf + "si ji" /

		inf+"melos"=inf + "mi je" / inf + "si je" 
		inf+"telos"=inf + "ti je" / inf + "si je" 
		inf+"selos"=inf + "mu je" / inf + "si je" 
		inf+"noslos"=inf + "nám je" / inf + "si je" 
		inf+"oslos"=inf + "vám je" / inf + "si je" 

		inf+"melas"=inf + "mi je" / inf + "si je" 
		inf+"telas"=inf + "ti je" / inf + "si je" 
		inf+"selas"=inf + "mu je" / inf + "si je" 
		inf+"noslas"=inf + "nám je" / inf + "si je" 
		inf+"oslas"=inf + "vám je" / inf + "si je"'''
	ret=""
	pronouns={"me":["mi","mně","mě","si","se", "na mě", "na sebe", "se mnou"],"te":["ti","tě","si","se", "na tebe", "na sebe", "s tebou"],"le":["mu","ho","si","se", "na něj", "na sebe", "s ním"],"lo":["to","na to", "s tím"],
 "la":["jí","ji", "na ni", "s ní"], "nos":["nám","nás","na nás","s námi","se"] ,"os":["vám","vás","na vás", "s vámi", "se"],"les":["jim" ,"je","na ně","s nimi","se"],"las":["jim" ,"je","na ně","s nimi","se"],"los":["jim" ,"je","na ně","s nimi","se"],\
"melo":["mi to", "mi ho","si to","si ho"], "telo":["ti to", "ti ho","si to","si ho"],"selo":["jí ho","jí to","mu to", "mu ho","si to","si ho"], "noslo":["nám to","nám ho","si to","si ho" ],"oslo":["vám to","vám ho","si to","si ho" ], \
"mela":["mi to", "mi ji","si to","si ji"], "tela":["ti to", "ti ji","si to","si ji"],"sela":["jí ji","jí to","mu to", "mu ji","si to","si ji"], "nosla":["nám to","nám ji","si to","si ji" ],"osla":["vám to","vám ji","si to","si ji" ], \
"melos":["mi to", "mi je","si to","si je"], "telos":["ti to", "ti je","si to","si je"],"selos":["jí je","jí to","mu to", "mu je","si to","si je"], "noslos":["nám to","nám je","si to","si je" ],"oslos":["vám to","vám je","si to","si je" ], \
"melas":["mi to", "mi je","si to","si je"], "telas":["ti to", "ti je","si to","si je"],"selas":["jí je","jí to","mu to", "mu je","si to","si je"], "noslas":["nám to","nám je","si to","si je" ],"oslas":["vám to","vám je","si to","si je" ] \
}
	for p in pronouns:
		ret+='inf+"'+p+'"='
		for v in pronouns[p]:
			ret+='inf + "'+v +'" / ' + '"'+v+'" + inf'
			if (len(pronouns[p])>1 and (pronouns[p].index(v)+1)!=len(pronouns[p])):
				ret+="/ "
 
		ret+="\n"
	return ret
print prubeh()
print imper()
print inf()


