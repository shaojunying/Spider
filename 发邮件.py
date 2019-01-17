#!/usr/bin/python3
# coding: utf-8

import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 第三方 SMTP 服务
mail_host = "smtp.126.com"  # SMTP服务器
mail_user = "shaojunying1999"  # 用户名
mail_pass = "shaojunying1999"  # 密码

sender = 'shaojunying1999@126.com'  # 发件人邮箱
receivers = ['sjy19990407@qq.com', 'shaojunying@bupt.edu.cn']  # 接收人邮箱

content = '最新的成绩是'
title = 'The grades have been updated.'  # 邮件主题
message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
message['From'] = "{}".format(sender)
message['To'] = ",".join(receivers)
message['Subject'] = Header(title, 'utf-8')

try:
    smtpObj = smtplib.SMTP_SSL(mail_host, 465)  # 启用SSL发信, 端口一般是465
    smtpObj.login(mail_user, mail_pass)  # 登录验证
    smtpObj.sendmail(sender, receivers, message.as_string())  # 发送
    print("mail has been send successfully.")
except smtplib.SMTPException as e:
    print(e)
