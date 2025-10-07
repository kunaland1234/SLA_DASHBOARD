import streamlit as st
import pandas as pd
from datetime import datetime
import database
import utils
import styling

# Configure page
st.set_page_config(
    page_title="SLA Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force light mode by overriding dark mode styles and enforcing light mode throughout
st.markdown("""
<style>
/* Force light mode */
html[data-theme="dark"] {
    background-color: #ffffff !important;
    color: #000000 !important;
}

/* Ensure headings are white in dark mode (remove dark mode altogether) */
html[data-theme="dark"] .section-title,
html[data-theme="dark"] .main-header {
    color: #000000 !important;
}

/* Adjust export button to be at the bottom left */
.export-button {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 9999;
}

/* Adjust refresh button to be at the bottom right */
.refresh-button {
    position: fixed;
    bottom: 20px;
    right: 20px;
    z-index: 9999;
}

/* Remarks section styling */

.remarks-title {
    color: #196B24;
    font-weight: bold;
    margin-bottom: 15px;
}

.remarks-item {
    background-color: #808080;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.no-remarks {
    color: #6c757d;
    font-style: italic;
    text-align: center;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# Cache data loading with error handling
@st.cache_data(ttl=300, show_spinner=False)
def load_all_data(_target_dates):
    """Cache data for 5 minutes with error handling"""
    try:
        sla_data = database.get_all_dates_data(_target_dates)
        alarms_data = database.get_alarms_data(_target_dates)
        return {'sla_data': sla_data, 'alarms_data': alarms_data}
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return {'sla_data': {}, 'alarms_data': {}}

def export_to_csv(dataframe, filename):
    """Helper function to export dataframe to CSV"""
    csv = dataframe.to_csv(index=False)
    return csv.encode('utf-8')

def display_remarks_section(alarms_data, date_string, display_name):
    """Display remarks section with alarms information"""
    st.markdown("---")
    st.markdown('<div class="remarks-container">', unsafe_allow_html=True)
    st.markdown('<h3 class="remarks-title">🔔 Remarks</h3>', unsafe_allow_html=True)
    
    if alarms_data and date_string in alarms_data and alarms_data[date_string]:
        alarms_for_date = alarms_data[date_string]
        
        # Group alarms by meter number
        alarms_by_meter = {}
        for alarm in alarms_for_date:
            meter_number = alarm['meter_number']
            if meter_number not in alarms_by_meter:
                alarms_by_meter[meter_number] = []
            alarms_by_meter[meter_number].append(alarm)
        
        # Display alarms for each meter
        for meter_number, meter_alarms in alarms_by_meter.items():
            st.markdown(f'<div class="remarks-item">', unsafe_allow_html=True)
            st.markdown(f"**{meter_number}**")
            for alarm in meter_alarms:
                alarm_time = alarm['alarm_time']
                if isinstance(alarm_time, datetime):
                    alarm_time_str = alarm_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    alarm_time_str = str(alarm_time)
                
                st.markdown(f"• {alarm['alarm_type']} on {alarm_time_str}")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="no-remarks">No alarms reported for this date</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_tab_content(tab_date_info, all_data, use_real_data):
    """Display content for a tab with enhanced features"""
    display_name, date_string = tab_date_info
    sla_data_dict = all_data.get('sla_data', {})
    alarms_data = all_data.get('alarms_data', {})

    if use_real_data and date_string in sla_data_dict and not sla_data_dict[date_string].empty:
        # Real data
        st.markdown(f'<h2 class="section-title">📈 SLA Report - {display_name}</h2>', unsafe_allow_html=True)
        sla_data = sla_data_dict[date_string]

        # Metrics
        styling.create_metric_row(sla_data, display_name, is_real_data=True)

        # Export button at bottom left without heading
        csv_data = export_to_csv(sla_data, f"sla_report_{date_string}.csv")
        st.markdown(f'<div class="export-button">', unsafe_allow_html=True)
        st.download_button(
            label="📥 Export CSV",
            data=csv_data,
            file_name=f"sla_report_{date_string}.csv",
            mime="text/csv",
            use_container_width=True,
            key=f"download_{date_string}"
        )
        st.markdown('</div>', unsafe_allow_html=True)

        # Detailed table (centered via middle column)
        st.markdown("---")
        st.markdown('<h3 class="section-title">📋 Detailed Meter Performance</h3>', unsafe_allow_html=True)

        styled_df = styling.apply_sla_styling(sla_data)
        # Show more rows: height scales with number of rows, capped for safety
        _table_height = min(38 * (len(sla_data) + 1), 900)  # ~38px per row incl. header
        st.dataframe(styled_df, use_container_width=True, height=_table_height)

        # Summary with additional stats
        total_meters = len(sla_data)
        if 'SLA Status' in sla_data.columns:
            met_sla = len(sla_data[sla_data['SLA Status'] == 'Met'])
            sla_percentage = (met_sla / total_meters * 100) if total_meters > 0 else 0
            st.markdown(
                f'<p style="color: #666666 !important; font-size: 14px;">📊 Total Meters: {total_meters} | '
                f'SLA Met: {met_sla} ({sla_percentage:.1f}%) | Date: {display_name}</p>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<p style="color: #666666 !important; font-size: 14px;">📊 Total Meters: {total_meters} | Date: {display_name}</p>',
                unsafe_allow_html=True
            )
        
        # Display Remarks section
        display_remarks_section(alarms_data, date_string, display_name)
        
    else:
        # Sample data
        st.markdown(f'<h2 class="section-title">🔍 Sample Data - {display_name}</h2>', unsafe_allow_html=True)
        st.info("⚠️ This is sample data. Connect to database for real-time information.")

        sample_data = styling.create_sample_data()
        styling.create_metric_row(sample_data, display_name, is_real_data=False)

        # Detailed table (centered via middle column)
        st.markdown("---")
        st.markdown('<h3 class="section-title">📋 Sample Meter Data</h3>', unsafe_allow_html=True)

        styled_df = styling.apply_sla_styling(sample_data)
        _table_height = min(38 * (len(sample_data) + 1), 900)
        st.dataframe(styled_df, use_container_width=True, height=_table_height)

        st.markdown(
            f'<p style="color: #666666 !important; font-size: 14px;">📊 Sample: {len(sample_data)} meters | Date: {display_name}</p>',
            unsafe_allow_html=True
        )
        
        # Display empty Remarks section for sample data
        display_remarks_section({}, date_string, display_name)

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 SLA Performance Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time SLA Monitoring & Analytics</p>', unsafe_allow_html=True)

    # Current time
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"🕐 **Last Updated:** {current_time}")

    # Database connection test
    with st.expander("🔌 Database Connection Status", expanded=False):
        try:
            if database.test_db_connection():
                st.success("✅ Database connected successfully!")
                use_real_data = True
            else:
                st.error("❌ Database connection failed")
                st.warning("⚠️ Showing sample data instead")
                use_real_data = False
        except Exception as e:
            st.error(f"❌ Database error: {str(e)}")
            st.warning("⚠️ Showing sample data instead")
            use_real_data = False

    # Get dates for tabs
    tab_dates = utils.get_tab_dates_with_names()
    date_strings = [tab_dates[0][1], tab_dates[1][1], tab_dates[2][1]]

    # Info about meters
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.success(f"📋 **Monitoring {len(database.FIXED_METERS)} Fixed Meters**")

    # Load all data at once
    all_data = {}
    if use_real_data:
        with st.spinner("⚡ Loading data for all dates..."):
            all_data = load_all_data(date_strings)
            if all_data and all_data.get('sla_data'):
                loaded_count = len([d for d in all_data['sla_data'].values() if not d.empty])
                if loaded_count > 0:
                    st.success(f"✅ Data loaded successfully for {loaded_count} dates!")
                else:
                    st.warning("⚠️ No data available for selected dates")
                    use_real_data = False

    # Create tabs
    tab1, tab2, tab3 = st.tabs([f"📅 {tab_dates[0][0]}", f"📅 {tab_dates[1][0]}", f"📅 {tab_dates[2][0]}"])

    # Display data in tabs
    with tab1:
        display_tab_content(tab_dates[0], all_data, use_real_data)

    with tab2:
        display_tab_content(tab_dates[1], all_data, use_real_data)

    with tab3:
        display_tab_content(tab_dates[2], all_data, use_real_data)

    # Refresh button at bottom right
    st.markdown('<div class="refresh-button">', unsafe_allow_html=True)
    if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()