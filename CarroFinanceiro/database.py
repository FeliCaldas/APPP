import sqlite3
import json

def get_db():
    return sqlite3.connect('vehicles.db')

def init_db():
    conn = get_db()
    c = conn.cursor()
    
    # Verifica se a coluna color existe
    c.execute("PRAGMA table_info(vehicles)")
    columns = [column[1] for column in c.fetchall()]
    
    # Cria a tabela se não existir
    c.execute('''
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year TEXT NOT NULL,
            color TEXT,
            purchase_price REAL NOT NULL,
            additional_costs REAL NOT NULL,
            fipe_price REAL NOT NULL,
            image_data TEXT
        )
    ''')
    
    # Adiciona a coluna color se não existir
    if 'color' not in columns:
        c.execute('ALTER TABLE vehicles ADD COLUMN color TEXT')

    # Nova tabela para manutenções
    c.execute('''
        CREATE TABLE IF NOT EXISTS maintenance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vehicle_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            cost REAL NOT NULL,
            mileage INTEGER,
            next_maintenance_date TEXT,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
        )
    ''')

    conn.commit()
    conn.close()

def add_vehicle(vehicle_data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO vehicles (brand, model, year, color, purchase_price, additional_costs, fipe_price, image_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        vehicle_data['brand'],
        vehicle_data['model'],
        vehicle_data['year'],
        vehicle_data['color'],
        vehicle_data['purchase_price'],
        vehicle_data['additional_costs'],
        vehicle_data['fipe_price'],
        vehicle_data['image_data']
    ))
    conn.commit()
    conn.close()

def get_vehicles():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM vehicles')
    vehicles = [dict(row) for row in c.fetchall()]
    conn.close()
    return vehicles

def update_vehicle(vehicle_id, vehicle_data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE vehicles
        SET brand=?, model=?, year=?, color=?, purchase_price=?, additional_costs=?, fipe_price=?, image_data=?
        WHERE id=?
    ''', (
        vehicle_data['brand'],
        vehicle_data['model'],
        vehicle_data['year'],
        vehicle_data['color'],
        vehicle_data['purchase_price'],
        vehicle_data['additional_costs'],
        vehicle_data['fipe_price'],
        vehicle_data['image_data'],
        vehicle_id
    ))
    conn.commit()
    conn.close()

def delete_vehicle(vehicle_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM vehicles WHERE id = ?', (vehicle_id,))
    conn.commit()
    conn.close()

# Funções para gerenciar manutenções
def add_maintenance(maintenance_data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO maintenance (vehicle_id, date, description, cost, mileage, next_maintenance_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        maintenance_data['vehicle_id'],
        maintenance_data['date'],
        maintenance_data['description'],
        maintenance_data['cost'],
        maintenance_data['mileage'],
        maintenance_data['next_maintenance_date']
    ))
    conn.commit()
    conn.close()

def get_vehicle_maintenance(vehicle_id):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM maintenance WHERE vehicle_id = ? ORDER BY date DESC', (vehicle_id,))
    maintenance_records = [dict(row) for row in c.fetchall()]
    conn.close()
    return maintenance_records

def update_maintenance(maintenance_id, maintenance_data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE maintenance
        SET date=?, description=?, cost=?, mileage=?, next_maintenance_date=?
        WHERE id=?
    ''', (
        maintenance_data['date'],
        maintenance_data['description'],
        maintenance_data['cost'],
        maintenance_data['mileage'],
        maintenance_data['next_maintenance_date'],
        maintenance_id
    ))
    conn.commit()
    conn.close()

def delete_maintenance(maintenance_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM maintenance WHERE id = ?', (maintenance_id,))
    conn.commit()
    conn.close()

def get_all_maintenance_records():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('''
        SELECT m.*, v.brand, v.model, v.year
        FROM maintenance m
        JOIN vehicles v ON m.vehicle_id = v.id
        ORDER BY m.date DESC
    ''')
    maintenance_records = [dict(row) for row in c.fetchall()]
    conn.close()
    return maintenance_records