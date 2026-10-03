import pyodbc

conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost;"
    "Database=LogisticsInventory;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

# 1. Define our logistics dataset
products = [
    ('SKU-PAL-001', 'Heavy Duty Wooden Pallets', 'Storage Equipment', 25.00, 150),
    ('SKU-BOX-022', 'Corrugated Shipping Boxes (Large)', 'Packaging', 1.50, 500),
    ('SKU-TAG-105', 'RFID Logistics Tracking Tags', 'Electronics', 0.75, 1000),
    ('SKU-STR-044', 'Industrial Poly Strapping Roll', 'Packaging', 45.00, 50),
    ('SKU-LUB-881', 'Forklift Hydraulic Fluid (5G)', 'Maintenance', 85.00, 20)
]

stock_logs = [
    # Day 1: Starting positions (Healthy Stock)
    ('2026-09-01', 'SKU-PAL-001', 400, 20, 0),
    ('2026-09-01', 'SKU-BOX-022', 1200, 150, 0),
    ('2026-09-01', 'SKU-TAG-105', 3500, 400, 0),
    ('2026-09-01', 'SKU-STR-044', 120, 5, 0),
    ('2026-09-01', 'SKU-LUB-881', 45, 1, 0),
    # Day 5: Mid-week steady business
    ('2026-09-05', 'SKU-PAL-001', 320, 15, 0),
    ('2026-09-05', 'SKU-BOX-022', 600, 180, 0), 
    ('2026-09-05', 'SKU-TAG-105', 1900, 450, 0),
    ('2026-09-05', 'SKU-STR-044', 100, 8, 0),
    ('2026-09-05', 'SKU-LUB-881', 41, 2, 0),
    # Day 10: Shipment Delivery Arrives (Restock Event)
    ('2026-09-10', 'SKU-PAL-001', 245, 25, 200),
    ('2026-09-10', 'SKU-BOX-022', 420, 110, 2000), 
    ('2026-09-10', 'SKU-TAG-105', 1000, 300, 5000), 
    ('2026-09-10', 'SKU-STR-044', 68, 6, 0),
    ('2026-09-10', 'SKU-LUB-881', 31, 0, 0),
    # Day 15: Post-restock operations (Alert thresholds tripped)
    ('2026-09-15', 'SKU-PAL-001', 420, 18, 0),
    ('2026-09-15', 'SKU-BOX-022', 2310, 140, 0),
    ('2026-09-15', 'SKU-TAG-105', 5700, 380, 0),
    ('2026-09-15', 'SKU-STR-044', 38, 7, 0),   
    ('2026-09-15', 'SKU-LUB-881', 31, 3, 0),
    # Day 20: Continued drawdown
    ('2026-09-20', 'SKU-PAL-001', 330, 22, 0),
    ('2026-09-20', 'SKU-BOX-022', 1610, 165, 0),
    ('2026-09-20', 'SKU-TAG-105', 3800, 410, 0),
    ('2026-09-20', 'SKU-STR-044', 11, 4, 0),    
    ('2026-09-20', 'SKU-LUB-881', 19, 2, 0),    
    # Day 25: The Stockout Event
    ('2026-09-25', 'SKU-PAL-001', 220, 15, 0),
    ('2026-09-25', 'SKU-BOX-022', 785, 130, 0),
    ('2026-09-25', 'SKU-TAG-105', 1750, 390, 0),
    ('2026-09-25', 'SKU-STR-044', 0, 0, 0),     
    ('2026-09-25', 'SKU-LUB-881', 9, 1, 0),     
    # Day 30: End of Month Closing balances
    ('2026-09-30', 'SKU-PAL-001', 145, 12, 0),  
    ('2026-09-30', 'SKU-BOX-022', 655, 115, 0),
    ('2026-09-30', 'SKU-TAG-105', 1360, 420, 0),
    ('2026-09-30', 'SKU-STR-044', 0, 0, 100),   
    ('2026-09-30', 'SKU-LUB-881', 4, 1, 0)     
]

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # 2. Clear out any old records to avoid duplicate keys
    cursor.execute("DELETE FROM DailyStockLog")
    cursor.execute("DELETE FROM InventoryMaster")
    
    # 3. Batch insert master items
    cursor.executemany(
        "INSERT INTO InventoryMaster (SKU, ProductName, Category, UnitCost, SafetyStockLevel) VALUES (?, ?, ?, ?, ?)",
        products
    )
    print(f"Successfully inserted {len(products)} master records.")
    
    # 4. Batch insert history logs
    cursor.executemany(
        "INSERT INTO DailyStockLog (LogDate, SKU, CurrentStockLevel, UnitsSold, UnitsReceived) VALUES (?, ?, ?, ?, ?)",
        stock_logs
    )
    print(f"Successfully inserted {len(stock_logs)} operational logs.")
    
    # Save the transactions firmly into the database
    conn.commit()
    
    # 5. Confirm count
    cursor.execute("SELECT COUNT(*) FROM InventoryMaster")
    print(f"Current items registered in Master Catalog: {cursor.fetchone()[0]}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"Data loading failed: {e}")
