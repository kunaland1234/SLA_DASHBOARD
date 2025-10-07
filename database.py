import pandas as pd
import mysql.connector
from datetime import datetime, timedelta
import streamlit as st

# Fixed meters list
FIXED_METERS = [
    {'meter_number': 'AS3313009', 'type': '4G'},
    {'meter_number': 'AS3313010', 'type': '4G'},
    {'meter_number': 'AS3313011', 'type': 'BLE'},
    {'meter_number': 'AS3313012', 'type': 'BLE'},
    {'meter_number': 'AS3313013', 'type': 'BLE'},
    {'meter_number': 'AS3313014', 'type': 'BLE'},
    {'meter_number': 'AS3313015', 'type': '4G'},
    {'meter_number': 'AS3313017', 'type': 'BLE'},
    {'meter_number': 'AS3313019', 'type': '4G'},
    {'meter_number': 'AS3313020', 'type': 'BLE'}
]

def get_db_connection():
    """Create database connection using Streamlit secrets"""
    try:
        # Check if secrets are available
        if 'db_connection' not in st.secrets:
            st.error("❌ Database configuration not found in secrets")
            return None
            
        conn = mysql.connector.connect(
            host=st.secrets['db_connection']['host'],
            port=st.secrets['db_connection']['port'],
            database=st.secrets['db_connection']['database'],
            user=st.secrets['db_connection']['user'],
            password=st.secrets['db_connection']['password'],
            connect_timeout=10,
            buffered=True,
            autocommit=True
        )
        return conn
    except Exception as e:
        st.error(f"❌ Connection failed: {str(e)}")
        return None

# Rest of your functions remain exactly the same...
def test_db_connection():
    """Test database connection"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return True
    return False

def execute_query(query, params=None):
    """Execute query and return results"""
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor()
        start_time = datetime.now()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        results = cursor.fetchall()
        cursor.close()
        
        query_time = (datetime.now() - start_time).total_seconds()
        if query_time > 2.0:
            st.warning(f"⚠️ Query took {query_time:.2f}s")
        
        return results
    except Exception as e:
        st.error(f"Query error: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def get_alarms_data(target_dates):
    """
    Fetch alarm data for all target dates in optimized query
    Returns: dict {date: list of alarm records}
    """
    try:
        if not target_dates:
            return {}
        
        meter_numbers = [m['meter_number'] for m in FIXED_METERS]
        meter_placeholders = ', '.join(['%s'] * len(meter_numbers))
        
        # Build date conditions for BETWEEN clauses
        date_conditions = []
        for date_str in target_dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            date_conditions.append(f"(alarm_time BETWEEN '{date_str} 00:00:00' AND '{next_day} 00:00:00')")
        
        date_condition = ' OR '.join(date_conditions)
        
        # OPTIMIZED QUERY: Alarm data for all dates
        alarms_query = f"""
        SELECT alarm_time, meter_number, alarm_type 
        FROM sense_hes_demo.push_alarm_parsed 
        WHERE meter_number IN ({meter_placeholders})
          AND ({date_condition})
        ORDER BY meter_number, alarm_time
        """
        
        params = meter_numbers
        alarms_results = execute_query(alarms_query, params)
        
        # Organize alarms by date
        alarms_by_date = {}
        for date_str in target_dates:
            alarms_by_date[date_str] = []
        
        for row in alarms_results:
            alarm_time, meter_number, alarm_type = row
            alarm_date = alarm_time.strftime('%Y-%m-%d') if isinstance(alarm_time, datetime) else str(alarm_time).split()[0]
            
            if alarm_date in alarms_by_date:
                alarms_by_date[alarm_date].append({
                    'meter_number': meter_number,
                    'alarm_type': alarm_type,
                    'alarm_time': alarm_time
                })
        
        return alarms_by_date
        
    except Exception as e:
        st.error(f"Error fetching alarms data: {str(e)}")
        return {}

def get_all_dates_data(target_dates):
    """
    Fetch SLA data for all dates in optimized queries
    Returns: dict {date: DataFrame}
    """
    try:
        if not target_dates:
            return {}
        
        meter_numbers = [m['meter_number'] for m in FIXED_METERS]
        meter_types = {m['meter_number']: m['type'] for m in FIXED_METERS}
        
        # Placeholders for SQL IN clause
        meter_placeholders = ', '.join(['%s'] * len(meter_numbers))
        date_placeholders = ', '.join(['%s'] * len(target_dates))
        
        # Build server_time conditions for each date
        server_time_conditions = []
        for date_str in target_dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            server_time_conditions.append(f"(DATE(DATETIME_SLOT) = '{date_str}' AND server_time < '{next_day} 04:10:00')")
        
        server_time_condition = ' OR '.join(server_time_conditions)
        
        # OPTIMIZED QUERY 1: Load data without reconciliation
        load_without_recon_query = f"""
        SELECT 
            meter_number,
            DATE(DATETIME_SLOT) as date,
            COUNT(DISTINCT DATETIME_SLOT) as load_count
        FROM sense_hes_demo.amr_load_data
        WHERE meter_number IN ({meter_placeholders})
            AND DATE(DATETIME_SLOT) IN ({date_placeholders})
            AND ({server_time_condition})
        GROUP BY meter_number, DATE(DATETIME_SLOT)
        """
        
        # OPTIMIZED QUERY 2: Load data with reconciliation
        load_with_recon_query = f"""
        SELECT 
            meter_number,
            DATE(DATETIME_SLOT) as date,
            COUNT(DISTINCT DATETIME_SLOT) as load_count
        FROM sense_hes_demo.amr_load_data
        WHERE meter_number IN ({meter_placeholders})
            AND DATE(DATETIME_SLOT) IN ({date_placeholders})
        GROUP BY meter_number, DATE(DATETIME_SLOT)
        """
        
        # Build midnight server_time conditions
        midnight_server_time_conditions = []
        for date_str in target_dates:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            next_day = (date_obj + timedelta(days=1)).strftime('%Y-%m-%d')
            midnight_server_time_conditions.append(f"(DATE(D6_SNAP_DATETIME) = '{date_str}' AND server_time < '{next_day} 04:10:00')")
        
        midnight_server_time_condition = ' OR '.join(midnight_server_time_conditions)
        
        # OPTIMIZED QUERY 3: Midnight without reconciliation
        midnight_without_recon_query = f"""
        SELECT 
            meter_number,
            DATE(D6_SNAP_DATETIME) as date,
            COUNT(DISTINCT D6_SNAP_DATETIME) as midnight_count
        FROM sense_hes_demo.amr_midnight_data
        WHERE meter_number IN ({meter_placeholders})
            AND DATE(D6_SNAP_DATETIME) IN ({date_placeholders})
            AND ({midnight_server_time_condition})
        GROUP BY meter_number, DATE(D6_SNAP_DATETIME)
        """
        
        # OPTIMIZED QUERY 4: Midnight with reconciliation
        midnight_with_recon_query = f"""
        SELECT 
            meter_number,
            DATE(D6_SNAP_DATETIME) as date,
            COUNT(DISTINCT D6_SNAP_DATETIME) as midnight_count
        FROM sense_hes_demo.amr_midnight_data
        WHERE meter_number IN ({meter_placeholders})
            AND DATE(D6_SNAP_DATETIME) IN ({date_placeholders})
        GROUP BY meter_number, DATE(D6_SNAP_DATETIME)
        """
        
        params = meter_numbers + target_dates
        
        # Execute all queries
        st.write("⚡ Executing queries...")
        load_without_recon_results = execute_query(load_without_recon_query, params)
        load_with_recon_results = execute_query(load_with_recon_query, params)
        midnight_without_recon_results = execute_query(midnight_without_recon_query, params)
        midnight_with_recon_results = execute_query(midnight_with_recon_query, params)
        
        # Build lookup dictionaries
        load_without_recon_dict = {(row[0], str(row[1])): row[2] for row in load_without_recon_results}
        load_with_recon_dict = {(row[0], str(row[1])): row[2] for row in load_with_recon_results}
        midnight_without_recon_dict = {(row[0], str(row[1])): row[2] for row in midnight_without_recon_results}
        midnight_with_recon_dict = {(row[0], str(row[1])): row[2] for row in midnight_with_recon_results}
        
        # Build DataFrames for each date
        date_dataframes = {}
        
        for target_date in target_dates:
            date_results = []
            
            for meter_number in meter_numbers:
                key = (meter_number, target_date)
                
                load_without = load_without_recon_dict.get(key, 0)
                load_with = load_with_recon_dict.get(key, 0)
                midnight_without = midnight_without_recon_dict.get(key, 0)
                midnight_with = midnight_with_recon_dict.get(key, 0)
                
                expected_load = 96
                
                # Calculate percentages
                received_percentage = round((load_without / expected_load) * 100, 2) if expected_load > 0 else 0
                received_percentage_with_recon = round((load_with / expected_load) * 100, 2) if expected_load > 0 else 0
                
                date_results.append({
                    'Meter Number': meter_number,
                    'Type': meter_types[meter_number],
                    'Expected Load': expected_load,
                    'Load Received Without Reconcillation': load_without,
                    'Received Load Percentage': received_percentage,
                    'Load Received With Reconcillation': load_with,
                    'Received Load Percentage with Reconcillation': received_percentage_with_recon,
                    'Midnight Received without Reconcillation': midnight_without,
                    'Midnight Received with Reconcillation': midnight_with
                })
            
            date_dataframes[target_date] = pd.DataFrame(date_results)
        
        return date_dataframes
        
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return {}