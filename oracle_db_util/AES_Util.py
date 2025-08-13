import hashlib
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# 全局密钥
SECRET_KEY = "TEST_SECRET_STRING"

def encrypt_data(data: str) -> str:
    """加密手机号/证件号"""
    # 生成密钥的SHA-256哈希（32字节）
    key = hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()
    # 生成随机初始化向量（16字节）
    iv = get_random_bytes(16)
    
    # 创建AES加密器
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 加密并填充数据
    encrypted = cipher.encrypt(pad(data.encode('utf-8'), AES.block_size))
    # 组合IV+密文并进行Base64编码
    return base64.b64encode(iv + encrypted).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """解密手机号/证件号"""
    # 生成密钥的SHA-256哈希
    key = hashlib.sha256(SECRET_KEY.encode('utf-8')).digest()
    # Base64解码原始数据
    raw_data = base64.b64decode(encrypted_data)
    # 提取前16字节作为IV
    iv = raw_data[:16]
    # 剩余部分是密文
    ciphertext = raw_data[16:]
    
    # 创建AES解密器
    cipher = AES.new(key, AES.MODE_CBC, iv)
    # 解密并移除填充
    decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted.decode('utf-8')