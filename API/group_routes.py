from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID, uuid4
import mysql.connector

router = APIRouter()

class Group(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    user_ids: List[UUID]

# Connexion à la base de données MySQL
def connect_to_database():
    try:
        db_connection = mysql.connector.connect(
            host="mysql",
            user="your_username",
            password="your_password",
            database="watchOurMoviesDB"
        )
        return db_connection
    except mysql.connector.Error as err:
        print(f"MySQL connection error: {err}")
        return None

db_connection = connect_to_database()

# Endpoint pour récupérer tous les groupes depuis la base de données
@router.get("/groups/", response_model=List[Group])
def read_groups():
    try:
        if not db_connection.is_connected():
            db_connection.reconnect()
        cursor = db_connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Groupe")
        groups = cursor.fetchall()
        
        # Récupérer les user_ids pour chaque groupe
        for group in groups:
            cursor.execute("SELECT user_id FROM Group_User WHERE group_id = %s", (group["id"],))
            user_ids = [user_id["user_id"] for user_id in cursor.fetchall()]
            group["user_ids"] = user_ids
        
        cursor.close()
        return groups
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

# Endpoint pour ajouter un nouveau groupe à la base de données
@router.post("/groups/", response_model=Group)
def add_group(group: Group):
    try:
        if not db_connection.is_connected():
            db_connection.reconnect()
        cursor = db_connection.cursor()

        # Vérication que tous les utilisateurs existent
        for user_id in group.user_ids:
            cursor.execute("SELECT * FROM User WHERE id = %s", (str(user_id),))
            user = cursor.fetchone()
            if user is None:
                raise HTTPException(status_code=400, detail=f"User {user_id} does not exist")

        cursor.execute("INSERT INTO Groupe (id, name) VALUES (%s, %s)", 
                       (str(group.id), group.name))

        for user_id in group.user_ids:
            cursor.execute("INSERT INTO Group_User (group_id, user_id) VALUES (%s, %s)", 
                           (str(group.id), str(user_id)))

        db_connection.commit()
        cursor.close()
        return group
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")