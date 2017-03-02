
import pymysql
import pymysql.cursors
from config import connect_dict


connection = pymysql.connect(**connect_dict)
    
def make_db_request(requests):
    if type(requests) != list:
        requests=[requests]
    results = []
    with connection.cursor() as cursor:
        for request in requests:
            if not request:
                continue
            cursor.execute(request)
            result = cursor.fetchall()
            results.append(result)
    if len(results) == 1:
        return results[0]
    return results
        
def make_update(updates):
    """
    Makes updates to the server.
    Used for when only a small number of updates are needed, as it commits after every update.
    
    """
    if type(updates) != list:
        updates = [updates]
    try:
        for update in updates:
            add_update(update)
            stop_update()
    except Exception as e:
        print(e)
    finally:
        pass
    
def add_update(update):
    """
    Use with stop_update to control when to make commits to the server.
    Ideal for larger amount of update statements at once.
    """
    with connection.cursor() as cursor:
        cursor.execute(update)
    
def stop_update():
    connection.commit()
