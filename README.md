# spider
## 信息门户.py
- Done
   - 每次调用程序会登陆教务系统获取最新的本学期成绩
   - 将获得的成绩中发布的成绩个数与result.txt中保存的成绩个数进行比较，如果不同说明成绩有更新，将会把成绩信息构成一个邮件，发送给设定好的邮箱
   - 每次调用无论成绩改变与否，都会输出调用时间和成绩信息
   - 可以结合linux服务器中的crontab命令实现每隔一个小时调用一次，将输出的时间和成绩信息存入日志文件

## 全民K歌.py

- Todo
  - 实现一个爬虫，下载不才上传的所有歌