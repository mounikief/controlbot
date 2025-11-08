"""
Multi-Source Dashboard für ControlBot
Zeigt integrierte Ansicht aller Datenquellen
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def show_multifile_dashboard():
    """Multi-Source Dashboard Interface"""
    
    st.header("📊 Multi-Source Project Dashboard")
    
    # Check if data loaded
    if not st.session_state.get('multifile_loaded', False):
        st.warning("⚠️ Keine Daten geladen! Bitte gehen Sie zu 'Multi-Source Upload'.")
        return
    
    data = st.session_state.integrated_data
    summary = data['summary']
    
    # Header KPIs
    st.markdown("### 📈 Projekt-Übersicht")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Projekt", summary['project_id'])
    
    with col2:
        st.metric("Budget", f"€{summary['total_budget']:,.0f}")
    
    with col3:
        ist_pct = (summary['total_ist'] / summary['total_budget'] * 100) if summary['total_budget'] > 0 else 0
        st.metric(
            "Ist-Kosten", 
            f"€{summary['total_ist']:,.0f}",
            delta=f"{ist_pct:.0f}% verbraucht"
        )
    
    with col4:
        st.metric(
            "Prognose Total",
            f"€{summary['projected_total']:,.0f}",
            delta=f"{summary['deviation_pct']:+.1f}%",
            delta_color="inverse"
        )
    
    with col5:
        if 'budget_runway_months' in summary:
            runway = summary['budget_runway_months']
            st.metric(
                "Reichweite",
                f"{runway:.1f} Mon.",
                delta="Budget" if runway > 3 else "⚠️ Knapp"
            )
    
    st.markdown("---")
    
    # 3-Spalten Layout
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        st.markdown("### 💰 Finanz-Status")
        
        # Budget Breakdown
        fig_budget = go.Figure()
        
        fig_budget.add_trace(go.Bar(
            name='Budget',
            x=['Gesamt'],
            y=[summary['total_budget']],
            marker_color='lightblue'
        ))
        
        fig_budget.add_trace(go.Bar(
            name='Ist',
            x=['Gesamt'],
            y=[summary['total_ist']],
            marker_color='orange'
        ))
        
        fig_budget.add_trace(go.Bar(
            name='Forecast',
            x=['Gesamt'],
            y=[summary['total_forecast']],
            marker_color='lightgreen'
        ))
        
        fig_budget.update_layout(
            barmode='group',
            height=300,
            showlegend=True,
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        st.plotly_chart(fig_budget, use_container_width=True)
        
        # Financial Summary Table
        st.markdown("**Details:**")
        fin_data = {
            'Kategorie': ['Budget', 'Ist-Kosten', 'Verbleibend', 'Forecast', 'Prognose Total', 'Abweichung'],
            'Betrag': [
                f"€{summary['total_budget']:,.0f}",
                f"€{summary['total_ist']:,.0f}",
                f"€{summary['total_budget'] - summary['total_ist']:,.0f}",
                f"€{summary['total_forecast']:,.0f}",
                f"€{summary['projected_total']:,.0f}",
                f"€{summary['deviation']:,.0f}"
            ]
        }
        st.dataframe(fin_data, hide_index=True, use_container_width=True)
    
    with col2:
        st.markdown("### 📦 Arbeitspakete")
        
        if data['arbeitspakete']:
            ap_summary = data['arbeitspakete']['summary']
            
            # Status Pie Chart
            status_data = {
                'Status': ['Fertig', 'In Arbeit', 'Nicht gestartet'],
                'Anzahl': [
                    ap_summary['completed'],
                    ap_summary['in_progress'],
                    ap_summary['not_started']
                ]
            }
            
            fig_status = px.pie(
                status_data,
                values='Anzahl',
                names='Status',
                color='Status',
                color_discrete_map={
                    'Fertig': 'green',
                    'In Arbeit': 'orange',
                    'Nicht gestartet': 'lightgray'
                }
            )
            
            fig_status.update_layout(
                height=300,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            
            st.plotly_chart(fig_status, use_container_width=True)
            
            # AP Summary
            st.markdown("**Übersicht:**")
            st.write(f"- Gesamt: {ap_summary['total_ap']} Arbeitspakete")
            st.write(f"- Fortschritt: {ap_summary['avg_progress']:.0f}%")
            st.write(f"- Budget: €{ap_summary['total_budget']:,.0f}")
            st.write(f"- Verbraucht: €{ap_summary['total_ist']:,.0f}")
        else:
            st.info("Keine Arbeitspaket-Daten verfügbar")
    
    with col3:
        st.markdown("### 👥 Ressourcen")
        
        if data['ressourcen_monatlich']:
            res_summary = data['ressourcen_monatlich']['summary']
            
            # Ressourcen Metrics
            st.metric("Ø Mitarbeiter", f"{res_summary['avg_mitarbeiter']:.1f}")
            st.metric("Peak", f"{res_summary['peak_mitarbeiter']} MA")
            st.metric("Gesamt Stunden", f"{res_summary['total_stunden']:,.0f}h")
            
            if res_summary['peak_month']:
                peak_str = res_summary['peak_month'].strftime('%B %Y')
                st.info(f"📊 Peak-Monat: **{peak_str}**")
        else:
            st.info("Keine Ressourcen-Daten verfügbar")
    
    st.markdown("---")
    
    # Zeitreihen-Analysen
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Kosten über Zeit")
        
        if data['ist_kosten']:
            ist_df = data['ist_kosten']['data']
            
            # Gruppiere nach Monat
            monthly = ist_df.groupby('Monat')['Kosten_Ist'].sum().reset_index()
            
            fig_timeline = px.line(
                monthly,
                x='Monat',
                y='Kosten_Ist',
                markers=True,
                title='Ist-Kosten pro Monat'
            )
            
            # Burn Rate Linie
            if 'burn_rate' in summary:
                fig_timeline.add_hline(
                    y=summary['burn_rate'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Ø Burn Rate: €{summary['burn_rate']:,.0f}"
                )
            
            fig_timeline.update_layout(height=350)
            st.plotly_chart(fig_timeline, use_container_width=True)
        else:
            st.info("Keine Ist-Kosten Daten verfügbar")
    
    with col2:
        st.markdown("### 👥 Ressourcen über Zeit")
        
        if data['ressourcen_monatlich']:
            res_df = data['ressourcen_monatlich']['data']
            
            fig_res = go.Figure()
            
            fig_res.add_trace(go.Scatter(
                x=res_df['Monat'],
                y=res_df['Mitarbeiter'],
                mode='lines+markers',
                name='Mitarbeiter',
                line=dict(color='blue', width=3)
            ))
            
            fig_res.update_layout(
                title='Mitarbeiter pro Monat',
                height=350,
                yaxis_title='Anzahl Mitarbeiter'
            )
            
            st.plotly_chart(fig_res, use_container_width=True)
        else:
            st.info("Keine Ressourcen-Daten verfügbar")
    
    st.markdown("---")
    
    # Detaillierte Tabellen
    with st.expander("📋 Arbeitspakete Details"):
        if data['arbeitspakete']:
            ap_df = data['arbeitspakete']['data']
            display_cols = ['AP_Name', 'Status', 'Fortschritt', 'Budget', 'Ist', 'Verantwortlich']
            st.dataframe(ap_df[display_cols], use_container_width=True)
        else:
            st.info("Keine Daten")
    
    with st.expander("💰 Kosten nach Kategorie"):
        if data['ist_kosten']:
            ist_df = data['ist_kosten']['data']
            category_summary = ist_df.groupby('Kategorie')['Kosten_Ist'].sum().reset_index()
            category_summary.columns = ['Kategorie', 'Gesamt Kosten']
            category_summary['Gesamt Kosten'] = category_summary['Gesamt Kosten'].apply(lambda x: f"€{x:,.0f}")
            st.dataframe(category_summary, hide_index=True, use_container_width=True)
        else:
            st.info("Keine Daten")
    
    with st.expander("📊 Ressourcen pro Arbeitspaket"):
        if data['ressourcen_arbeitspakete']:
            res_ap_df = data['ressourcen_arbeitspakete']['data']
            ap_agg = res_ap_df.groupby('AP_Name').agg({
                'Ressourcen': 'sum',
                'Stunden': 'sum',
                'Kosten': 'sum'
            }).reset_index()
            st.dataframe(ap_agg, hide_index=True, use_container_width=True)
        else:
            st.info("Keine Daten")

if __name__ == "__main__":
    show_multifile_dashboard()
