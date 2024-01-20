from flask import Flask, request, Response
import mysql.connector
import uuid
import json

app = Flask(__name__)
mydb_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="db_pool", pool_size=10, host="localhost",
                                                        username="root", password="cHetan123##", database="new_schema")


@app.route('/addItem', methods=["POST"])
def addItem():
    data = request.data.decode("utf-8")
    print(data)
    data = json.loads(data)

    text = data["text"]
    description = data["description"]

    with mydb_pool.get_connection() as mydb:
        cur = mydb.cursor()
        id = str(uuid.uuid4()).replace("-", "")
        cur.execute("""INSERT INTO main (text,description,completed,id) VALUES (%s,%s,%s,%s);""", (text, description, False, id))
        cur.close()
        mydb.commit()

    return Response(id, status=200)


@app.route('/removeItem')
def removeItem():
    id = request.args.get("id")
    if id is None:
        return Response(status=400)

    with mydb_pool.get_connection() as mydb:
        cur = mydb.cursor()
        cur.execute("""DELETE FROM main WHERE id=%s""", (id,))
        cur.close()
        mydb.commit()

    return Response(status=200)


@app.route('/editItem', methods=["POST"])
def editItem():
    data = request.data.decode("utf-8")
    data = json.loads(data)

    id = data["id"]

    with mydb_pool.get_connection() as mydb:
        cur = mydb.cursor()
        list_args = list(data.keys())
        if "task" in list_args:
            cur.execute("""UPDATE main SET text=%s WHERE id=%s""", (data["task"], id))
        if "completed" in list_args:
            cur.execute("""UPDATE main SET completed=%s WHERE id=%s""", (data["completed"], id))
        if "description" in list_args:
            cur.execute("""UPDATE main SET description=%s WHERE id=%s""", (data["description"], id))
        cur.close()
        mydb.commit()

    return Response(status=200)


@app.route('/list')
def listGet():
    with mydb_pool.get_connection() as mydb:
        cur = mydb.cursor()
        cur.execute("""SELECT * FROM main""")
        to_return = []
        rows = cur.fetchall()
        for row in rows:
            to_return.append(
                {
                    "task": row[0],
                    "description": row[1],
                    "completed": row[2],
                    "id": row[3]
                }
            )

        return Response(json.dumps(to_return))


if __name__ == '__main__':
    app.run(debug=True)
