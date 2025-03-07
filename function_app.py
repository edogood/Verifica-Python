import azure.functions as func
import logging
import pyodbc
import json
import os

app = func.FunctionApp()

def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={os.getenv("DATABASE")};'
        f'Trusted_Connection={os.getenv("Trusted_Connection")};'
    )

@app.route(route="cantanti", methods=["POST"])
def register_singer(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    name = data.get("name")
    if not name:
        return func.HttpResponse(json.dumps({"Messaggio": "Serve il nome del cantante"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO cantanti (nome) VALUES (?)", (name,))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Cantante inserito", "name": name}), status_code=201)

@app.route(route="utenti", methods=["POST"])
def register_user(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    username = data.get("name")
    if not username:
        return func.HttpResponse(json.dumps({"Messaggio": "Nome inserito"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO utenti (nome_utente) VALUES (?)", (username,))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Utente registrato!", "username": username}), status_code=201)

@app.route(route="punteggi", methods=["POST"])
def assign_points(req: func.HttpRequest) -> func.HttpResponse:
    data = req.get_json()
    cantante_id = data.get("cantante_id")
    punti = data.get("punti")
    descrizione = data.get("descrizione", "")
    
    if punti is None or cantante_id is None or not isinstance(punti, int):
        return func.HttpResponse(json.dumps({"Messaggio": "Metti un valore valido"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO punteggi (cantante_id, punti, descrizione) VALUES (?, ?, ?)", (cantante_id, punti, descrizione))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Punti assegnati!"}), status_code=201)

import azure.functions as func
import logging
import pyodbc
import json
import os

app = func.FunctionApp()

def get_db_connection():
    return pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={os.getenv("DATABASE")};'
        f'Trusted_Connection={os.getenv("Trusted_Connection")};'
    )

@app.route(route="cantanti", methods=["POST"])
def register_singer(req: func.HttpRequest) -> func.HttpResponse:
    """Registra un cantante."""
    data = req.get_json()
    name = data.get("name")
    if not name:
        return func.HttpResponse(json.dumps({"Messaggio": "Serve il nome del cantante"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO cantanti (nome) VALUES (?)", (name,))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Cantante inserito", "name": name}), status_code=201)

@app.route(route="utenti", methods=["POST"])
def register_user(req: func.HttpRequest) -> func.HttpResponse:
    """Registra un utente."""
    data = req.get_json()
    username = data.get("name")
    if not username:
        return func.HttpResponse(json.dumps({"Messaggio": "Nome inserito"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO utenti (nome_utente) VALUES (?)", (username,))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Utente registrato!", "username": username}), status_code=201)

@app.route(route="punteggi", methods=["POST"])
def assign_points(req: func.HttpRequest) -> func.HttpResponse:
    """Assegna punti a un cantante."""
    data = req.get_json()
    cantante_id = data.get("cantante_id")
    punti = data.get("punti")
    descrizione = data.get("descrizione", "")
    
    if punti is None or cantante_id is None or not isinstance(punti, int):
        return func.HttpResponse(json.dumps({"Messaggio": "Metti un valore valido"}), status_code=400)
    
    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("INSERT INTO punteggi (cantante_id, punti, descrizione) VALUES (?, ?, ?)", (cantante_id, punti, descrizione))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"Messaggio": "Punti assegnati!"}), status_code=201)

@app.route(route="squadra", methods=["POST"])
def add_to_team(req: func.HttpRequest) -> func.HttpResponse:
    """Aggiunge un cantante alla squadra di un utente."""
    try:
        data = req.get_json()
    except ValueError:
        return func.HttpResponse(json.dumps({"Messaggio": "Invalid JSON data"}), status_code=400)

    utente_id = data.get("utente_id")
    cantante_id = data.get("cantante_id")

    if not utente_id or not cantante_id:
        return func.HttpResponse(json.dumps({"message": "inserire utente_id o cantante_id"}), status_code=400)

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM squadre WHERE utente_id = ?", (utente_id,))
        count = cursor.fetchone()[0]
        if count >= 5:
            return func.HttpResponse(json.dumps({"Messaggio": "Un utente non può avere più di cinque cantanti"}), status_code=400)

        cursor.execute("SELECT 1 FROM squadre WHERE utente_id = ? AND cantante_id = ?", (utente_id, cantante_id))
        exists = cursor.fetchone()
        
        if exists:
            return func.HttpResponse(json.dumps({"message": "Cantante già presente nella squadra"}), status_code=400)
        
        cursor.execute("INSERT INTO squadre (utente_id, cantante_id) VALUES (?, ?)", (utente_id, cantante_id))
        conn.commit()
    
    return func.HttpResponse(json.dumps({"message": "Cantante aggiunto con successo"}), status_code=201)


@app.route(route="punti/squadra/{utente_id}", methods=["GET"])
def team_score(req: func.HttpRequest) -> func.HttpResponse:
    """Restituisce il punteggio totale di una squadra."""
    try:
        utente_id = int(req.route_params.get("utente_id"))
    except (ValueError, TypeError):
        return func.HttpResponse(json.dumps({"Messaggio": "L'ID dell'utente deve essere un numero valido"}), status_code=400)

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT SUM(p.punti) FROM punteggi p
            JOIN squadre s ON p.cantante_id = s.cantante_id
            WHERE s.utente_id = ?
            """,
            (utente_id,)
        )
        score = cursor.fetchone()[0] or 0

    return func.HttpResponse(json.dumps({"utente_id": utente_id, "punti_totali": score}), status_code=200)

@app.route(route="punti/cantante/{cantante_id}", methods=["GET"])
def singer_score(req: func.HttpRequest) -> func.HttpResponse:
    """Restituisce il punteggio totale di un cantante."""
    try:
        cantante_id = int(req.route_params.get("cantante_id"))
    except (ValueError, TypeError):
        return func.HttpResponse(json.dumps({"Messaggio": "L'ID del cantante deve essere un numero valido"}), status_code=400)

    with get_db_connection() as conn, conn.cursor() as cursor:
        cursor.execute("SELECT SUM(punti) FROM punteggi WHERE cantante_id = ?", (cantante_id,))
        score = cursor.fetchone()[0] or 0

    return func.HttpResponse(json.dumps({"cantante_id": cantante_id, "punti_totali": score}), status_code=200)
