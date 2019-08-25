
# 首先切换环境

today=`date +%Y%m%d`

rm -rf data
[ ! -d "data" ] && mkdir data

outputdir=data/${today}

rm -rf ${outputdir}
mkdir ${outputdir}

#scrapy crawl topapp -o ${outputdir}/topapp.json
#python chatterbox/unique.py ${outputdir}/topapp.json

rm all.log

bookPath=${outputdir}/books.json
scrapy crawl book -o $bookPath  -s LOG_FILE=all.log