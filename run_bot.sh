#!/bin/bash
# تشغيل البوت مع تسجيل جميع المخرجات

echo "🚀 بدء تشغيل بوت الاستعلام..." | tee -a /tmp/bot_log.txt
date >> /tmp/bot_log.txt
echo "----------------------------------------" >> /tmp/bot_log.txt

python -u main.py 2>&1 | tee -a /tmp/bot_log.txt
