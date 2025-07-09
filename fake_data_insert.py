import oracledb
import random
import string
import hashlib
import base64
from faker import Faker
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# 全局密钥
SECRET_KEY = "TEST_SECRET_STRING"

# 初始化Faker生成仿真数据
fake = Faker('zh_CN')

# 初始化oracle
oracledb.init_oracle_client()

# 数据库配置
db_config = {
    "user": "TEST",
    "password": "TEST",
    "dsn": "10.10.0.111:1521/ORCL",
    "min": 1,
    "max": 5,
    "increment": 1
}

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

def generate_simulated_data(num_records):
    """生成仿真数据"""
    data = []
    for i in range(num_records):
        # 生成仿真数据
        account = f"user_{fake.unique.random_number(digits=6)}"
        password = encrypt_data(''.join(random.choices(string.ascii_letters + string.digits, k=12)))
        real_name = fake.name()
        
        # 模拟加密数据
        mobile = encrypt_data(fake.phone_number())
        id_card = encrypt_data(fake.ssn())
        
        is_valid = 'Y' if random.random() > 0.1 else 'N'  # 90%有效，10%无效
        
        data.append((
            account,
            password,
            real_name,
            mobile,
            id_card,
            is_valid
        ))
    return data

def insert_data(data):
    """插入数据到数据库"""
    try:
        # 创建连接池
        pool = oracledb.create_pool(**db_config)
        
        # 从连接池获取连接
        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                # 准备SQL语句
                sql = """
                INSERT INTO T_USER (
                    USER_ACC, 
                    USER_PASSWD, 
                    USER_NAME, 
                    USER_PHONE, 
                    USER_ID_NUM, 
                    IS_VALID
                ) VALUES (
                    :1, :2, :3, :4, :5, :6
                )
                """
                
                # 批量插入数据
                cursor.executemany(sql, data)
                connection.commit()
                
                print(f"成功插入 {cursor.rowcount} 条数据")
                
    except oracledb.Error as e:
        print("数据库错误:", e)
    except Exception as e:
        print("发生错误:", e)
    finally:
        # 关闭连接池
        if 'pool' in locals():
            pool.close()

if __name__ == "__main__":
    # 生成100条仿真数据
    simulated_data = generate_simulated_data(100)

    # 插入数据到数据库
    insert_data(simulated_data)

    # for data in simulated_data[:5]:
    #     print(data)

    # 加解密测试
    # data = "12345678900"
    # encrypted_data = encrypt_data(data)
    # print(f'加密结果：{ encrypted_data }')
    
    # decrypted_data = decrypt_data(encrypted_data)
    # print(f"解密结果：{ decrypted_data }")
