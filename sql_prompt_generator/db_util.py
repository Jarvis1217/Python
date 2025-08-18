import json
import oracledb

# oracle 初始化
oracledb.init_oracle_client()

DB_POOLS = {    
	"test_db_1": "test_db_1_dsn",
	"test_db_2": "test_db_2_dsn",
	"test_db_3": "test_db_3_dsn",
}

# 数据库选择
DB_CHOICE = ""

# 数据库表选择
TABLES = []

# 数据库配置
DSN = DB_POOLS.get(DB_CHOICE)
USER = DB_CHOICE
PASSWORD = DB_CHOICE

# 查询所有表及表注释
SQL_TABLES = """
    SELECT TABLE_NAME, COMMENTS AS TABLE_COMMENT
      FROM USER_TAB_COMMENTS
     WHERE TABLE_TYPE = 'TABLE'
       AND TABLE_NAME NOT LIKE 'BIN$%'
     ORDER BY TABLE_NAME
"""

# 查询表注释
SQL_TABLE_COMMENT = """
    SELECT table_name, comments
      FROM all_tab_comments
     WHERE owner = SYS_CONTEXT('USERENV','CURRENT_SCHEMA')
       AND table_name = :tn
"""

# 查询字段名、类型及注释
SQL_COLUMNS = """
    SELECT a.column_name,
           a.data_type ||
           CASE
               WHEN a.data_type = 'NUMBER' AND a.data_precision IS NOT NULL AND a.data_scale IS NOT NULL THEN
                '(' || a.data_precision || ',' || a.data_scale || ')'
               WHEN a.data_type = 'NUMBER' AND a.data_precision IS NOT NULL AND a.data_scale IS NULL THEN
                '(' || a.data_precision || ')'
               WHEN a.data_type IN ('CHAR', 'VARCHAR2') THEN
                '(' || a.data_length || ')'
               ELSE
                ''
           END AS data_type_desc,
           b.comments
      FROM all_tab_columns a
      LEFT JOIN all_col_comments b
        ON a.owner = b.owner
       AND a.table_name = b.table_name
       AND a.column_name = b.column_name
     WHERE a.owner = SYS_CONTEXT('USERENV','CURRENT_SCHEMA')
       AND a.table_name = :tn
     ORDER BY a.column_id
"""

# 查询所有表
def query_all_tables() -> dict:
    result: dict[str, str] = {}

    with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
        with conn.cursor() as cur:
            cur.execute(SQL_TABLES)
            for table_name, comment in cur:
                result[table_name] = comment or ""
    
    return result

# 查询表结构
def get_table_structure(table_name: str) -> str:
    tn = table_name.upper()

    result = {
        tn: "",
        "COLUMNS": {}
    }

    with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as conn:
        with conn.cursor() as cur:
            # 查询并组装表名
            cur.execute(SQL_TABLE_COMMENT, tn=tn)
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Table '{tn}' not found in current schema.")

            result[tn] = row[1]

            # 查询并组装列信息
            cur.execute(SQL_COLUMNS, tn=tn)
            columns = {}
            for col_name, type_desc, comment in cur:
                columns[col_name] = [type_desc, comment or ""]
            result["COLUMNS"] = columns

    # 返回 JSON 字符串
    return json.dumps(result, ensure_ascii=False)
