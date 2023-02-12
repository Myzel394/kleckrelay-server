import base64
import string

DB_URI = "postgresql://user:password@127.0.0.1:35432/mail"
MAX_ENCRYPTED_NOTES_SIZE = 10_000
ACCESS_TOKEN_EXPIRE_IN_MINUTES = 60 * 3  # 3 hours
REFRESH_TOKEN_EXPIRE_IN_MINUTES = 60 * 24 * 60  # 60 Days
# CHANGE THIS IN PRODUCTION!!!
JWT_SECRET_KEY = base64.b64decode("IyNNYWlsVGVzdF9TZWNyZXRLZXlfQ2hhbmdlX01l")
# CHANGE THIS IN PRODUCTION!!!
JWT_REFRESH_SECRET_KEY = base64.b64decode("IyNNYWlsVGVzdF9SZWZyZXNoX1NlY3JldEtleV9DaGFuZ2VfTWU=")
EMAIL_LOGIN_TOKEN_LENGTH = 5
EMAIL_LOGIN_TOKEN_CHARS = string.digits
EMAIL_LOGIN_TOKEN_MAX_TRIES = 5
EMAIL_LOGIN_TOKEN_EXPIRATION_IN_SECONDS = 60 * 15  # 15 minutes
EMAIL_LOGIN_TOKEN_CHECK_EMAIL_EXISTS = "True"
IS_DEBUG = "False"
API_DOMAIN = "api.kleckrelay.com"
MAIL_DOMAIN = "mail.kleckrelay.com"
APP_DOMAIN = "app.kleckrelay.com"
RANDOM_EMAIL_ID_MIN_LENGTH = 6
RANDOM_EMAIL_ID_CHARS = string.ascii_letters + string.digits
RANDOM_EMAIL_LENGTH_INCREASE_ON_PERCENTAGE = 0.0005  # 0.05%
CUSTOM_EMAIL_SUFFIX_LENGTH = 4
CUSTOM_EMAIL_SUFFIX_CHARS = string.digits
POSTFIX_HOST = "127.0.0.1"
POSTFIX_PORT = 25
POSTFIX_USE_TLS = "True"
DEBUG_MAILS = "False"
SLOW_HASH_SALT = "KleckRelay_#ChangeMe"
FAST_HASH_SALT = "KleckRelay_#ChangeMeToo"
USER_PASSWORD_HASH_SALT = "KleckRelay_#AlsoChangeMeToo"
EMAIL_LANDING_PAGE_URL_TEXT = "KleckRelay"
EMAIL_LANDING_PAGE_URL = "kleckrelay.com"
IMAGE_PROXY_TIMEOUT_IN_SECONDS = 8
IMAGE_PROXY_STORAGE_LIFE_TIME_IN_HOURS = 24
IMAGE_PROXY_STORAGE_PATH = "./storage/image_proxy/images"
ENABLE_IMAGE_PROXY = "True"
USER_EMAIL_ENABLE_DISPOSABLE_EMAILS = "False"
USER_EMAIL_ENABLE_OTHER_RELAYS = "True"
USER_EMAIL_OTHER_RELAY_DOMAINS = ",".join({
    "duck.com",

    "simplelogin.com",
    "aleeas.com",
    "slmail.me",
    "simplelogin.fr",

    "mozmail.com",

    "anonaddy.com",
    "anonaddy.me"
})
GNUPG_HOME_DIR = "~/.gnupg"
# DO NOT USE THIS PRIVATE KEY!!!!!!!!!!!!!!!!!!
# THIS KEY IS !! ONLY !! USED DURING DEVELOPMENT!!!!!
# CREATE YOUR OWN KEY IF YOU ARE USING THIS OUTSIDE OF DEVELOPMENT!!!!!
SERVER_PRIVATE_KEY = \
"LS0tLS1CRUdJTiBQR1AgUFJJVkFURSBLRVkgQkxPQ0stLS0tLQpWZXJzaW9uOiBPcGVuUEdQLmpzIHY0LjEwLjEwCkNvbW1" \
"lbnQ6IGh0dHBzOi8vb3BlbnBncGpzLm9yZwoKeGNMWUJHUEcyRmdCQ0FEVUVKVVpIYWtlS2ZxTEF6UU9tVTBBK1NuWFI2bU" \
"ttbEttT2YwUzZDZVBka0VVCmtNUXJLUkFHOGxpT3FIU00ydGcyMW95T2xBQnFRSlJXSlhuSHBBcDMxVWRHTG1BQ3VVT3lVc" \
"3poYy83VgpYc1RTdWtCKzlIQ2dvQTFrTjJqbFVBK24xSGduOVRBdlV0bEhMMjZIYXNrcE95YlhTYWFFMUJVYVJRWngKNjRq" \
"d2J2ckU2RlV1Y0t4MmxUaG5KdGpyOHJyMEgwUkdYRFVSc21Zamc0ZEp3MFcrU2w1aVpYKzJZUzI2CityOTk1RDNwY2pienV" \
"xemZ0OW9QRnNwekNKS2pUdGJyUkpYRXg4bHNrR2J4ZUpaQVlzL2NDd1Bab05IRwo1eE1VR3dKNW9PZFl0dlB2VlBURnBwel" \
"U0QWMrTVdreHppTEE2TnJ4ZlYvcS9DVGFBQ2ozM3BmYkFCRUIKQUFFQUIvNHpFTmt1aHA5eVpZNXhDakR2Y1FnRGUzeVJYQ" \
"zdkOHdLREI4VEMyRWVxZXNINk4xQWR5cElTCjhpblVGSW1ZWDV5Z08vTDE1SHJqR3pEOU82SURLcVBncm1tdTR6ejRldTly" \
"MGhlSEZOMGhPV1J4RUN1Mgp4cHNXZXVRdXBVOHJwU2RYOVVpSDZybVRNOEtocXpEVkNDaHZ0dEJJR0hLeVdyWElNU1gzcWM" \
"yOGc3VEYKSW91dk1SeDdpV3F4ZmdtMUtXbWlpRm9mRFJFWkFsTDhXQU5zZUhmUkNCWkdqT0srdFZJVTJlM2dubHJZCnJRUm" \
"12U1k3ak0yMzJFOHFiMWZmQTk1SVlvTk51U2RFNzhkdllBaTEycWk1dHVLNTh5TTJNK1ByVVJnRwprN2NYdmxqcVVjTDVhK" \
"0l1UE9iWDN3aHdOcDJpMDhMMC85NjRjSkFwZk41Q1ZwNlZCQURvbGMwN3Vlb0gKZHd3cDhFaC9HRkt1UlRNL1dkQTZxRmZt" \
"czZrSTdjZG5STFVHTlhQaGZ5Q2c0Nk84VEZjUDhLQ01hNjhaCmhzV0ZBcHhhdkxpLzBEMkliSE1QTkwra3F0SFRCRmtkNFA" \
"1ZHA5a2lMTlh6UmtLdFE4akNQamk1M2w5bgp0SkJuTVhkY2NDRjQxZHNvWlFDRVBjdklkeUVZMk5Zc2oyRlZOUHFtM3dRQT" \
"ZXbnRsOGJGdkQzQk1nb2oKMlVpMzQrK0taVVg1RndBd3pPcVQxQXFxeC9XZmNnbmV5Y1RqcTB0WEFDcmZYK2E3OWVKbDlsN" \
"Vc5VVpDClJ2dnJFUkdiRm1HS3Uxb01HZ3lVNkNWYStDalZXTHoyLzVUL2FIWUlHZkU4QzlOZHhNOG1LcmdpQ29HRwpKZ29w" \
"ZXFsYTFLZThjMzVjd05iQzFhdFcvVndoalczMDJvVUVBSldXRVg2VzYwV28vd2J3Szd1c1k5c2kKQjVkTjlWblpwSEF6Y0t" \
"ZaGwwRGZaVUFRWlhwWnAzWHhHNmkzUkJobjFDQ25Yakh4cnBycVZrSUtxT3Q2CjFTOEJSRk1scFdRZ1JYVkU2Z2ZJMGY3SW" \
"ZJZ01KLzVFK09kNW5JTUtncnB5c0xodjZ5alVEeGo5YksyWgpzeEF1M0FXNW8rUGprdlEyWmNQTUNsbUJXUzIzUXpUTkVXR" \
"WdQR0ZBWlhoaGJYQnNaUzVqYjIwK3dzQ04KQkJBQkNBQWdCUUpqeHRoWUJnc0pCd2dEQWdRVkNBb0NCQllDQVFBQ0dRRUNH" \
"d01DSGdFQUlRa1FENi9mCkpjb3djS2tXSVFUbXN0UWxSdm12SnRUa3hlTVByOThseWpCd3Flay9DQURRSDlNeUEzdWRuWGh" \
"Wdm1DbAowa2E2aXRaWXA1R0lya2gvQmFHdWYva3MrVk55amZ6cm9jbUlnYmkvOWZPM3BWbzMwV3JWdlErb2xZV2IKYXIzc0" \
"05SitGZUxiZ251Rm1HM2xtbGlZdU5RWlFZWEd4SWNtVXdQVDlDVXNKRGQ1YlV6bk9reXRNNmoxCmRkZWM2ODZEMm5IVktvb" \
"i9pRks0T3FsbUFSdHhrOW1SaTB3OUpDWTl0V0RrZ205R29GTzFROFNrZjRRNwo3U0syakplcktNUTNHSnplVXl0dEhXNEhL" \
"RUZZb1JRR3J2eGJ4UERQMXRLaXpaYS9GTlJCUEJJVHo0UWkKemdvdjRCZDRTZW1Tc0cyTVRDUVdFeUxaRUd6MVpMM0szd2x" \
"wbDFhb1JVVnpFRUhtYmJhVXBCclQyUzl5CnJqRHI0ZU03VHEwb29oRFlNMnZPYUhSQng4TFlCR1BHMkZnQkNBQ3d6TEs2eD" \
"dYbHRXOUFyUnVjeXBmNgpLTk1lWFNaR2tQcVc5VHVUMk9BZDl6K0hLVUYvYk45M0VuS1pSRTJaU3hPaEN6amtxT2hUbmVkM" \
"kp2dWcKNnc1R3N4VHZxVjBXYW9EV2hNU1A5MWd2Q1I3ajcvTURqQkFZSFI1YmREWGZzazljUVZTWDgwRE8zTEloCldPWm85" \
"amVOZ1NkMlRuUnREalZ1cXFod1VyZERQcHRTM0Jzb2E5VG1GNHNTN3pOdTNGVDZ1amNuUDd6TgpjbHZmcTBLZ0E5Z0s2b21" \
"VUDVNcWR6OTY3ci9BMnZ0cld0R3FicEJwaEZlbnZuNVNqMlV4eG1TYWRhQysKSnNUNGhWN0pncGZVclV6cE1XbkJQeEVLWj" \
"IrTGM1WFNaekxFenhjZ2cyMWxWVXJnTTdBZVpEaHNBMHVSCnc4WVVJbG4rWXZWVTk1TnJTaDNsQUJFQkFBRUFCLzBjZDFqd" \
"nFlZ25yQ2JWaXdtL0hQK0xUN2R1VkNFdAppM3BOZy82cnQyZWVhNGpYQWxXQlpzNDBKY3c5MFRtTlRRRkVGTUo4VHBYWm9M" \
"cjcweHNBdGRmK21pYnMKejZBbFU5Q2F1WlhNZUU3Q2cvMXRSZDBpM1JKYVQ1WHJzN0pZNmlUTS9kZlkvMW1YOVFEWlRhOEx" \
"oMWs2CmQya2JLMWFqbUg0UjYzaGpYVzRVYldONzBVbTkrY0tPSjhQRENxWGFlWXExdmllTGRnN3ZRZWEyc3dzWQpOaFJDU3" \
"E1OG1ubmh2ZnR5RWhwdkVpbGRROFhsL1RIVXZ3ZjM5TElHTXNhQjZCNlN3RnJtemhsTXJFNXAKTm1YVnQ0by83MmtGNEdQY" \
"lVVa0JtL2ZCWU4zdkhacXBwcFNZVlg5Y08wUHNaQW5IZGJ3aXFRUlBaamd1Cm1KK1VhMzl4WVdHaEJBREhEWXFSVkwrOHFL" \
"ODhwUm43WjA5cFNGaHZ0ZEtJWU1xcGJ0ZkVFMGRTTnNGVwoybXVRTkMxTjk4aUJMdDFWTVpkbFgvZDNyeEdoSFFhWDRWTzJ" \
"adkdXMUowRzdaZTk3TWNLcmVYcG16ZkQKdlpPM0VDMytGQWpZRG9oeEs4UlBKTEd2QjNBakwrcm9iTldsUlQ4YWt4UmVsZ0" \
"hPc1F4ZHNiMzhTUUR5Clh6Y21rd1FBNDJGWVkvOXphSmY5VVhkaHR6blZZaHRjbXNPVlVwS3MvSkV5S2p5K2pKemZPM29rK" \
"zN3RQpoMWlDaFRCeXJFR1lwYktkVmdNMXA5RGRUNUVrRll0bCtBT1hjZHB1em4vZGdHdDFmNHM3c3Vsa2ExVnMKY2x6cW5n" \
"UkZLb216eXBhMmYyZ0owbnZSYzY2eHNKczdleDQ3NUF1OTZsK0g3S2ZZY3pMbWJSdVV2S2NECi9qa05QYjdWdTJFak5GaWs" \
"1eHBsckUvalFMU3VXSGQzOFNNeTN3blRHeDJ3WFlmUERIa1llUDJZZ1NqcQpxd1dod21jRWdSMFBYY3N6RGFZMGhlTnFlWU" \
"1xQkZpMkNsaCtSQVNKQ1Y3aDFlNER5cnE4cGFIR01ZRGkKc0srcmJsL2pMa2x6ZFBNU2tuck54QUp6UXN6OEZjekpWaEcwR" \
"TNSMjRJUll4NWZkb3Rmc1FjN0N3SFlFCkdBRUlBQWtGQW1QRzJGZ0NHd3dBSVFrUUQ2L2ZKY293Y0trV0lRVG1zdFFsUnZt" \
"dkp0VGt4ZU1Qcjk4bAp5akJ3cVdkTUIvOVNKZGt5am9PVEdNVFRhOUJaNk0vOCt6RzFIS2FNRTVjQyt4b3F4OG5MUUpBTy9" \
"KV0oKMDB4SDkxcW03N0F0WnhyMUpIK2x0c2RrRERoUXMrZHdISWpVV1haTjd3SnNwREV6NGY2c2tRRWVySzVXCmhtSzJhdG" \
"dDMkQxRmVidnJuQjBMS2xDY2o4ZDQzZzREamxuaEVHNkFIenYwUWxBRHI1VlNGRTdkaSs5TgpBcHV6WDFxVWdXbUxxSHVMY" \
"3hUQkJtYUo4S09mTWhwNWdCVE9aU2w3elc5RTU3T3NHblVHRERPVWg2VDIKTFEzNGt4Wi93ZEt1ZzQrYWRGRFphODZVRk5K" \
"L0duR1BVak9kbkNYZXZHVzVieXU0RHhmalI1Zk93TENDCmJxVWFHeGgwd2cvL0x1Wkh3T0NidHFkb0YvRFNFeDFVU2pzY1l" \
"4WUllcE91QW94OUhiWDUKPWd3d0EKLS0tLS1FTkQgUEdQIFBSSVZBVEUgS0VZIEJMT0NLLS0tLS0K"""
EMAIL_RESEND_WAIT_TIME_IN_SECONDS = 60
INSTANCE_SALT = "KleckRelay-Salt-ChangeMe"
ALLOW_STATISTICS = "True"
DKIM_PRIVATE_KEY = ""
ADMINS = ""
USE_GLOBAL_SETTINGS = "True"
ALLOW_LOGS = "True"
