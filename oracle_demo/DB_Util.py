# pip install PyYAML oracledb

import yaml
import re
import oracledb
from pathlib import Path
from typing import Any, Dict, List, Sequence

BASE_DIR = Path(__file__).resolve().parent        # 当前文件所在目录
DEFAULT_SQL_FILE = BASE_DIR / "sqls.yml"          # 绝对路径

class OracleDB:
    """
    通用 Oracle 工具类
    """
    _placeholder_regex = re.compile(r'\?')  # 用于把 ? -> :1 :2 ...

    def __init__ (
        self,
        dsn: str = "10.10.0.111:1521/ORCL",
        user: str = "test_user",
        password: str = "test_user",
        sql_file: str | Path = DEFAULT_SQL_FILE
    ):
        # 1. 初始化连接
        oracledb.init_oracle_client()

        self._conn = oracledb.connect(user=user, password=password, dsn=dsn)
        self._cursor = self._conn.cursor()

        # 2. 读取 SQL 文件
        with open(sql_file, "r", encoding="utf-8") as f:
            data: Dict[str, str] = yaml.safe_load(f)
            self._sql_dict: Dict[str, str] = data if data is not None else {}

    # ---------- 私有工具方法 ------------------------------------------------
    @staticmethod
    def _row_to_dict(cursor, row) -> Dict[str, Any]:
        """
        把一行结果转成 dict；列名全部转换成小写。
        """
        col_names = [d[0].lower() for d in cursor.description]
        return dict(zip(col_names, row))

    @staticmethod
    def _convert_placeholders(sql: str) -> str:
        """
        把 ? 占位符转换成 python-oracledb 识别的 :1, :2, :3 ……
        """
        idx = 0

        def repl(_: re.Match) -> str:
            nonlocal idx
            idx += 1
            return f":{idx}"

        return OracleDB._placeholder_regex.sub(repl, sql)

    def _get_sql(self, sql_or_key: str) -> str:
        """
        如果提供的是 key，则从 sql_dict 里取；否则直接返回原始字符串
        """
        return self._sql_dict.get(sql_or_key, sql_or_key)

    # ---------- CRUD API ---------------------------------------------------
    def execute_dml(self, sql_or_key: str, params: Sequence[Any] = ()) -> int:
        """
        通用 Insert / Update / Delete  
        返回受影响行数
        """
        sql = self._convert_placeholders(self._get_sql(sql_or_key))

        with self._conn:  # 自动处理提交/回滚
            self._cursor.execute(sql, params)

        return self._cursor.rowcount
        
    def fetch_one(self, sql_or_key: str, params: Sequence[Any] = ()) -> Dict[str, Any]:
        """
        查询一行，返回 dict；若无数据则返回 {}
        """
        sql = self._convert_placeholders(self._get_sql(sql_or_key))
        self._cursor.execute(sql, params)
        row = self._cursor.fetchone()
        return {} if row is None else self._row_to_dict(self._cursor, row)

    def fetch_all(self, sql_or_key: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        """
        查询多行，返回 list[dict]
        """
        sql = self._convert_placeholders(self._get_sql(sql_or_key))
        self._cursor.execute(sql, params)
        rows = self._cursor.fetchall()
        return [self._row_to_dict(self._cursor, r) for r in rows]

    # ---------- 释放资源 ----------------------------------------------------
    def close(self):
        try:
            self._cursor.close()
        finally:
            self._conn.close()

    # 允许 with OracleDB(...) as db: 使用
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
