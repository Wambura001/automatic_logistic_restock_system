import pyodbc
from datetime import datetime

# 1. Database Connection Configurations
conn_str = (
    "Driver={ODBC Driver 18 for SQL Server};"
    "Server=localhost;"
    "Database=LogisticsInventory;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def run_inventory_audit():
    print("=" * 60)
    print(f"LAUNCHING AUTOMATED INVENTORY AUDIT: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Establish connection gate
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # 2. SQL Query to extract ONLY the latest date's stockouts & shortages
        # This matches the identical logic we verified inside your Power BI Data Model
        audit_query = """
        WITH LatestLog AS (
            SELECT MAX(LogDate) as MaxDate FROM DailyStockLog
        )
        SELECT 
            m.SKU,
            m.ProductName,
            m.SafetyStockLevel,
            l.CurrentStockLevel,
            (m.SafetyStockLevel - l.CurrentStockLevel) AS Deficit,
            m.UnitCost,
            ((m.SafetyStockLevel - l.CurrentStockLevel) * m.UnitCost) AS FinancialRisk
        FROM DailyStockLog l
        JOIN InventoryMaster m ON l.SKU = m.SKU
        CROSS JOIN LatestLog r
        WHERE l.LogDate = r.MaxDate
          AND l.CurrentStockLevel < m.SafetyStockLevel;
        """
        
        cursor.execute(audit_query)
        shortages = cursor.fetchall()
        
        # 3. Process and format the alert reports
        if not shortages:
            print("\nSUCCESS: All logistics warehouse inventory levels are healthy.")
            print("No reorder procurement warnings triggered.")
        else:
            print(f"\nALERT: Found {len(shortages)} critical inventory deficit areas!\n")
            print(f"{'SKU':<14} | {'Product Name':<35} | {'Stock':<5} | {'Safety':<6} | {'Risk Val':<10}")
            print("-" * 85)
            
            total_portfolio_risk = 0.0
            
            for row in shortages:
                sku, name, safety, current, deficit, cost, risk = row
                total_portfolio_risk += float(risk)
                
                # Format long product names nicely for the terminal layout
                display_name = name[:32] + "..." if len(name) > 35 else name
                
                print(f"{sku:<14} | {display_name:<35} | {current:<5} | {safety:<6} | ${risk:,.2f}")
            
            print("-" * 85)
            print(f"TOTAL LOGISTICS CAPITAL AT RISK: ${total_portfolio_risk:,.2f}")
            print("=" * 60)
            print("ACTION REQUIRED: Please forward these shortages to procurement immediately.")
            print("=" * 60)
            
        # Clean up database resources
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"\nAUTOMATION CRASH: Unable to complete data audit loop.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    run_inventory_audit()
