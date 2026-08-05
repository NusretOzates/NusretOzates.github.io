---
title: "How to use one MongoDB instance in multiple FastAPI routers?"
date: 2021-08-08
categories: [ml, software]
image: "img_0.png"
mediumUrl: "https://medium.com/carbon-consulting/how-to-use-one-mongodb-instance-in-multiple-fastapi-routers-810c288b1c51"
---

![Image](img_0.png)

[https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)

> When I begin to use FastAPI, I was fascinated by how it is easy to use and how it is possible to have an organized backend structure with it.

For example, when I have endpoints for`/item` and `/users` I would like to have them in separate files. With this approach, I could get rid of the problem of having one huge file to maintain and have a cleaner structure. I have just one problem with this approach: I have only one MongoDB instance and I need to use that one instance from every router file. After trying lots of bad or useless solutions, today I finally find the best and cleaner way to use the same MongoDB instance inside different routers and I want to share it with everyone. [This](https://github.com/michaldev/fastapi-async-mongodb) is where I find the solution and I will explain this implementation using PyMongo( not an async solution ). I will try to keep it simple and small. This is my file structure:

```text
app
```

```text
   --- db
         --- __init__.py
         --- mongo_manager.py
   --- routers
         --- __init__.py
         --- users.py
   --- main.py
```

This is what we have in mongo_manager.py:

```python
import logging
from pymongo import MongoClient
from pymongo.database import Database
class MongoManager:
    client: MongoClient = None
    db: Database = None
    def connect_to_database(self, path: str):
        logging.info("Connecting to MongoDB.")
        self.client = MongoClient(path)
        self.db = self.client.main_db
        logging.info("Connected to MongoDB.")
    def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")
    def get_users(self):
        users_query = self.db.users.find({}, {'_id': 0})
        return list(users_query)
```

It is a pretty simple class, given connection string, it connects to the database and assigns the client and db to the class variables. We only have one db operation which is get_users() and it returns all users in the database without their id in the database. db/__init__.py is next:

```python
from app.db.mongo_manager import MongoManager
db = MongoManager()
```

That’s all :) We will use this db object from the main.py and users.py! So, main.py is next!

```python
import uvicorn
from fastapi import FastAPI
from app.db import db
from app.rest import users
app = FastAPI(title="FastAPI")
app.include_router(users.router, prefix='/api/users')
@app.on_event("startup")
async def startup():
    await db.connect_to_database(path="YOUR MONGODB CONNECTION STRING")
@app.on_event("shutdown")
async def shutdown():
    await db.close_database_connection()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

As you can see from the 3. line we import the db object from the previous file we looked at. On the fastAPI **startup event**, we connect to the MongoDB database using the***connect_to_database()***function and we close the connection on **shutdown.** Now time to go to the users.py.

```python
from fastapi import APIRouter
from app.db import db
router = APIRouter()
@router.get('/')
def all_users():
    users = db.get_users()
    return users
```

I don’t know if it is the magic of the fastAPI or not but when we import the same db object from here, it doesn’t give us a newly initialized MongoManager object. What we get is a MongoManager object we configure in the startup!

I guess that’s all! You can use the same db object in the different routers too! Thanks for reading and I hope it helps someone out there because I waste lots of time until I found this method :)
