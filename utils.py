from datetime import datetime, timezone, timedelta

def get_ist_now():
    """Get current datetime in IST (UTC+5:30)"""
    utc_time = datetime.now(timezone.utc)
    ist_time = utc_time + timedelta(hours=5, minutes=30)
    return ist_time

def get_tab_dates():
    """
    Get dates for the three tabs: current day-1, current day-2, current day-3
    Returns list of dates in 'YYYY-MM-DD' format using IST timezone
    """
    try:
        current_date = get_ist_now()
        
        dates = [
            (current_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=2)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=3)).strftime('%Y-%m-%d')
        ]
        
        return dates
    except Exception as e:
        current_date = get_ist_now()
        return [
            (current_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=2)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=3)).strftime('%Y-%m-%d')
        ]

def get_tab_dates_with_names():
    """
    Get dates with display names for tabs using IST timezone
    Returns list of tuples: (display_name, date_string)
    """
    try:
        current_date = get_ist_now()
        
        dates = [
            (f"{(current_date - timedelta(days=1)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=1)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=2)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=2)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=3)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=3)).strftime('%Y-%m-%d'))
        ]
        
        return dates
    except Exception as e:
        current_date = get_ist_now()
        return [
            (f"{(current_date - timedelta(days=1)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=1)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=2)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=2)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=3)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=3)).strftime('%Y-%m-%d'))
        ]

def get_current_year():
    """Get current year as string using IST timezone"""
    return get_ist_now().strftime('%Y')
