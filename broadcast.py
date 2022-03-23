import datetime
import time
import requests
import pymysql
import os
import dotenv


# 방송 상태와 정보 조회
def get_broadcast_info(user_id):
    endpoint = f"https://bjapi.afreecatv.com/api/{user_id}/station"
    ua = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    res = requests.get(endpoint, headers={"User-Agent": ua})
    api_data = res.json()

    # 존재하는 방송국인지 확인 (code 정보가 없어서 추후 예외처리 필요)
    if "code" in api_data:
        if api_data["code"] == 9000:
            return {
                "user_exist": False,
                "on_air": False,
                "user_data": {},
                "broadcast_data": {}
            }

    # 기타 방송국 데이터 불러오기
    user_data = {
        "user_id": api_data['station']['user_id'],
        "user_nick": api_data['station']['user_nick'],
        "profile_image": api_data['profile_image']
    }

    # 방송 중인지 확인
    if api_data["broad"] is None:
        return {
            "user_exist": True,
            "on_air": False,
            "user_data": user_data,
            "broadcast_data": {}
        }
    else:
        return {
            "user_exist": True,
            "on_air": True,
            "user_data": user_data,
            "broadcast_data": {
                "broad_no": api_data['broad']['broad_no'],
                "broad_title": api_data['broad']['broad_title'],
                "broad_datetime": api_data['station']['broad_start'],
                "current_sum_viewer": api_data['broad']['current_sum_viewer'],
            }
        }


class Database:
    def __init__(self):
        pass

    def set(self):
        try:
            dotenv.load_dotenv()
            db = pymysql.connect(
                host=os.getenv("DB_HOSTNAME"),
                port=int(os.getenv("DB_PORT")),
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                database=os.getenv("DB_DATABASE"),
                charset="utf8mb4"
            )
            cursor = db.cursor(pymysql.cursors.DictCursor)
        except Exception as e:
            return {
                "status": False,
                "items": []
            }
        else:
            return {
                "status": True,
                "items": [db, cursor]
            }

    def close(self, db, cursor):
        cursor.close()
        db.close()


# 최신의 방송인지 확인
def is_latest_broadcast(user_id, broad_no):
    database = Database()
    db_info = database.set()
    if not db_info['status']:
        return False
    else:
        db, cursor = db_info['items']

    sql = f"SELECT broad_no, broad_datetime FROM latest_broadcast WHERE user_id='{user_id}' and del_stat=0 LIMIT 1"
    cursor.execute(sql)
    result = cursor.fetchone()
    database.close(db, cursor)

    if result is None:
        return False
    elif str(result['broad_no']) == str(broad_no):
        return False
    else:
        return True


# 가장 최신의 방송 id를 DB에 등록 (중복 알림 가지 않도록)
def set_latest_broadcast(user_id, broad_no, broad_datetime):
    database = Database()
    db_info = database.set()
    if not db_info['status']:
        return False
    else:
        db, cursor = db_info['items']

    try:
        update_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = f"UPDATE latest_broadcast SET broad_no='{broad_no}', broad_datetime='{broad_datetime}', update_datetime='{update_datetime}' WHERE user_id='{user_id}'"
        cursor.execute(sql)
        db.commit()
        database.close(db, cursor)
    except Exception as e:
        return False
    else:
        return True


# print(is_latest_broadcast('hami0825', '1234'))



