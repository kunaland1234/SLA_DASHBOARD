from datetime import datetime, timedelta

def get_tab_dates():
    """
    Get dates for the three tabs: current day-1, current day-2, current day-3
    Returns list of dates in 'YYYY-MM-DD' format
    """
    try:
        current_date = datetime.now()
        
        dates = [
            (current_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=2)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=3)).strftime('%Y-%m-%d')
        ]
        
        return dates
    except Exception as e:
        current_date = datetime.now()
        return [
            (current_date - timedelta(days=1)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=2)).strftime('%Y-%m-%d'),
            (current_date - timedelta(days=3)).strftime('%Y-%m-%d')
        ]

def get_tab_dates_with_names():
    """
    Get dates with display names for tabs
    Returns list of tuples: (display_name, date_string)
    """
    try:
        current_date = datetime.now()
        
        dates = [
            (f"{(current_date - timedelta(days=1)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=1)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=2)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=2)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=3)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=3)).strftime('%Y-%m-%d'))
        ]
        
        return dates
    except Exception as e:
        current_date = datetime.now()
        return [
            (f"{(current_date - timedelta(days=1)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=1)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=2)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=2)).strftime('%Y-%m-%d')),
            (f"{(current_date - timedelta(days=3)).strftime('%d-%m-%Y')}", (current_date - timedelta(days=3)).strftime('%Y-%m-%d'))
        ]

def get_current_year():
    """Get current year as string"""
    return datetime.now().strftime('%Y')