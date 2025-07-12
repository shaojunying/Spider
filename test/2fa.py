import pyotp
import time

# 用于生成2FA的密钥，可以是任意字符串
secret_key = 'GYIKPUYLY44QZMEV'

# 初始化TOTP对象，指定密钥
totp = pyotp.TOTP(secret_key)

# 获取当前时间的验证码
otp_code = totp.now()
# 获取当前验证码的剩余有效时间
time_remaining = totp.interval - (time.time() % totp.interval)

print(f"Current OTP Code: {otp_code}")
print(f"Time Remaining (seconds): {int(time_remaining)}")