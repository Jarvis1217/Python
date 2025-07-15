import datetime
import AES_Util
from DB_Util import OracleDB

if __name__ == "__main__":
    with OracleDB() as db:
        user_map = db.fetch_one("get_user_by_id", [3])
        
        user_map = {k: v.strftime("%Y-%m-%d %H:%M:%S") if isinstance(v, datetime.datetime) else v for k, v in user_map.items()}

        user_map["user_passwd"] = AES_Util.decrypt_data(user_map["user_passwd"])
        user_map["user_phone"] = AES_Util.decrypt_data(user_map["user_phone"])
        user_map["user_id_num"] = AES_Util.decrypt_data(user_map["user_id_num"])

        print(f"user_map = {user_map}")
