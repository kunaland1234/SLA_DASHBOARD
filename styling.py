import pandas as pd
import streamlit as st

def create_sample_data():
    """Create sample data"""
    sample_data = {
        'Meter Number': ['AS3313009', 'AS3313010', 'AS3313011', 'AS3313012', 'AS3313013',
                         'AS3313014', 'AS3313015', 'AS3313017', 'AS3313019', 'AS3313020'],
        'Type': ['4G', '4G', 'BLE', 'BLE', 'BLE', 'BLE', '4G', 'BLE', '4G', 'BLE'],
        'Expected Load': [96, 96, 96, 96, 96, 96, 96, 96, 96, 96],
        'Load Received Without Reconcillation': [71, 78, 80, 80, 80, 75, 75, 80, 69, 80],
        'Received Load Percentage': [73.96, 81.25, 83.33, 83.33, 83.33, 78.13, 78.13, 83.33, 71.88, 83.33],
        'Load Received With Reconcillation': [96, 96, 96, 96, 96, 96, 96, 96, 96, 96],
        'Received Load Percentage with Reconcillation': [100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00, 100.00],
        'Midnight Received without Reconcillation': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        'Midnight Received with Reconcillation': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    }
    return pd.DataFrame(sample_data)

def apply_sla_styling(df):
    """Apply enhanced styling to SLA dataframe"""
    try:
        styled_df = df.copy()

        # Format percentage columns
        if 'Received Load Percentage' in styled_df.columns:
            styled_df['Received Load Percentage'] = styled_df['Received Load Percentage'].apply(
                lambda x: f"{float(x):.2f}%" if isinstance(x, (int, float)) else str(x)
            )

        if 'Received Load Percentage with Reconcillation' in styled_df.columns:
            styled_df['Received Load Percentage with Reconcillation'] = styled_df['Received Load Percentage with Reconcillation'].apply(
                lambda x: f"{float(x):.2f}%" if isinstance(x, (int, float)) else str(x)
            )

        # Create styler
        styler = styled_df.style

        # Colors - updated for dark mode compatibility
        header_bg = '#000000'      # Black background for headers
        header_text = '#FFFFFF'    # White text for headers
        data_bg = '#D2FAE2'        # Light green for data
        data_text = '#000000'      # Black text for data
        warning_bg = '#FFD9D9'     # Light red for warnings
        warning_text = '#000000'   # Black text for warnings
        border = '#000000'         # Black borders

        # Table styles
        table_styles = [
            {'selector': '',
             'props': [('border-collapse', 'collapse'), ('width', '100%')]},

            {'selector': 'thead th',
             'props': [('background-color', header_bg),
                       ('color', header_text),
                       ('font-weight', 'bold'),
                       ('border', f'2px solid {border}'),
                       ('text-align', 'center'),
                       ('padding', '14px 10px'),
                       ('font-size', '15px'),
                       ('letter-spacing', '0.5px')]},

            {'selector': 'tbody td',
             'props': [('border', f'2px solid {border}'),
                       ('text-align', 'center'),
                       ('padding', '10px 8px'),
                       ('font-size', '14px'),
                       ('color', data_text),
                       ('font-weight', '500'),
                       ('background-color', data_bg)]},

            {'selector': 'tbody tr:hover',
             'props': [('background-color', '#B8F0D0')]}
        ]

        styler = styler.set_table_styles(table_styles, overwrite=False)

        # Conditional formatting
        def highlight_cells(row):
            styles = [''] * len(row)
            try:
                for i, (col, val) in enumerate(zip(styled_df.columns, row)):
                    base_style = f'border: 2px solid {border}; background-color: {data_bg}; color: {data_text};'
                    warning_style = f'border: 2px solid {border}; background-color: {warning_bg}; color: {warning_text}; font-weight: bold;'

                    if col == 'Load Received Without Reconcillation':
                        styles[i] = warning_style if isinstance(val, (int, float)) and val < 96 else base_style

                    elif col == 'Received Load Percentage':
                        try:
                            perc_val = float(str(val).replace('%', ''))
                            styles[i] = warning_style if perc_val < 100 else base_style
                        except:
                            styles[i] = base_style

                    elif col == 'Load Received With Reconcillation':
                        styles[i] = warning_style if isinstance(val, (int, float)) and val < 96 else base_style

                    elif col == 'Received Load Percentage with Reconcillation':
                        try:
                            perc_val = float(str(val).replace('%', ''))
                            styles[i] = warning_style if perc_val < 100 else base_style
                        except:
                            styles[i] = base_style

                    elif col == 'Midnight Received without Reconcillation':
                        styles[i] = warning_style if isinstance(val, (int, float)) and val < 1 else base_style

                    elif col == 'Midnight Received with Reconcillation':
                        styles[i] = warning_style if isinstance(val, (int, float)) and val < 1 else base_style

                    else:
                        styles[i] = base_style
            except Exception:
                for i in range(len(styles)):
                    styles[i] = f'border: 2px solid {border}; background-color: {data_bg}; color: {data_text};'
            return styles

        styler = styler.apply(highlight_cells, axis=1)
        return styler

    except Exception as e:
        st.error(f"Styling error: {str(e)}")
        return df.style.set_properties(**{
            'background-color': '#D2FAE2',
            'border': '2px solid #000000',
            'text-align': 'center',
            'color': '#000000'
        })

def create_metric_card(title, value, icon, bg_color='#196B24'):
    """Create metric card"""
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {bg_color} 0%, {bg_color}dd 100%);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border: 2px solid #000000;">
        <div style="font-size: 32px; margin-bottom: 8px;">{icon}</div>
        <div style="color: white; font-size: 14px; font-weight: 600; margin-bottom: 8px;">{title}</div>
        <div style="color: white; font-size: 28px; font-weight: bold;">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def create_metric_row(df, display_name, is_real_data=True):
    """Create metrics row"""
    if df.empty:
        st.warning("No data available")
        return

    bg_color = '#196B24' if is_real_data else '#888888'

    # Heading for the metric row (theme-aware via CSS class)
    st.markdown(
        f'<h3 class="section-title">📊 Summary Metrics - {display_name}</h3>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_meters = len(df)
        create_metric_card("Total Meters", total_meters, "📊", bg_color)

    with col2:
        try:
            perc_values = df['Received Load Percentage'].apply(
                lambda x: float(str(x).replace('%', '')) if isinstance(x, str) else float(x)
            )
            avg_without = perc_values.mean()
            create_metric_card("Load Avg Without Recon", f"{avg_without:.1f}%", "📉", bg_color)
        except:
            create_metric_card("Load Avg Without Recon", "N/A", "📉", bg_color)

    with col3:
        try:
            perc_values_recon = df['Received Load Percentage with Reconcillation'].apply(
                lambda x: float(str(x).replace('%', '')) if isinstance(x, str) else float(x)
            )
            avg_with = perc_values_recon.mean()
            create_metric_card("Load Avg With Recon", f"{avg_with:.1f}%", "📈", bg_color)
        except:
            create_metric_card("Load Avg With Recon", "N/A", "📈", bg_color)

    with col4:
        try:
            midnight_ok = (df['Midnight Received with Reconcillation'] >= 1).sum()
            midnight_total = len(df)
            create_metric_card("Midnight Status", f"{midnight_ok}/{midnight_total}", "🌙", bg_color)
        except:
            create_metric_card("Midnight Status", "N/A", "🌙", bg_color)

    st.markdown("<br>", unsafe_allow_html=True)
