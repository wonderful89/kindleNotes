
filePath=../mebook/../moehui.db
if [ ! -f $filePath ];then
    echo "不复制数据库"
    # python mainPrg.py -e  // 检查错误模式
    python mainPrg.py
else
    echo "复制数据库"
    rm moehui.db
    mv $filePath .
    python mainPrg.py
fi
