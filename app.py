"""
ControlBot v1.2 - KI-Assistent für Projektcontroller
Mit Smart Data Import und Multi-Source Intelligence
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Imports - prüfe ob neue Module verfügbar sind
try:
    from smart_data_processor import SmartDataProcessor
    SMART_FEATURES = True
except ImportError:
    SMART_FEATURES = False
    
try:
    from template_manager import TemplateManager
    TEMPLATE_FEATURES = True
except ImportError:
    TEMPLATE_FEATURES = False

try:
    from multi_file_processor import MultiFileProcessor
    MULTIFILE_FEATURES = True
except ImportError:
    MULTIFILE_FEATURES = False

from data_processor import DataProcessor
from ai_generator import AIReportGenerator
from report_builder import ReportBuilder
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="ControlBot",
    page_icon="📊",
    layout="wide"
)

def init_session_state():
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'multifile_loaded' not in st.session_state:
        st.session_state.multifile_loaded = False
    if 'integrated_data' not in st.session_state:
        st.session_state.integrated_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

def main():
    init_session_state()
    
    version = "v1.2 Multi-Source" if MULTIFILE_FEATURES else "v1.1"
    st.markdown(f'<h1 style="text-align: center; color: #1f77b4;">📊 ControlBot {version}</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #666;">Ihr intelligenter Assistent für Projektcontrolling</p>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Navigation")
        
        pages = ["📤 Daten Upload"]
        if MULTIFILE_FEATURES:
            pages.append("📤 Multi-Source Upload")
        pages.extend(["📊 Dashboard", "📝 Report Generator", "ℹ️ Anleitung"])
        
        page = st.radio("Seite:", pages, label_visibility="collapsed")
        
        st.markdown("---")
        st.markdown("### ⚙️ Einstellungen")
        
        api_key = None
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except:
            pass
        
        if api_key:
            os.environ['OPENAI_API_KEY'] = api_key
            st.success("✅ API Key geladen")
        else:
            user_key = st.text_input("OpenAI API Key", type="password")
            if user_key:
                os.environ['OPENAI_API_KEY'] = user_key
                st.success("✅ Key gespeichert")
        
        st.markdown("---")
        st.markdown("### ✨ Features")
        if SMART_FEATURES:
            st.success("✅ Smart Import")
        if TEMPLATE_FEATURES:
            st.success("✅ Templates")
        if MULTIFILE_FEATURES:
            st.success("✅ Multi-Source")
    
    if page == "📤 Daten Upload":
        show_upload_page()
    elif page == "📤 Multi-Source Upload":
        show_multifile_upload()
    elif page == "📊 Dashboard":
        show_dashboard()
    elif page == "📝 Report Generator":
        show_report_page()
    elif page == "ℹ️ Anleitung":
        show_help_page()

def show_upload_page():
    st.header("📤 Daten Upload (Einzelne Datei)")
    
    if SMART_FEATURES:
        st.info("🚀 Smart Import aktiviert: Automatische Erkennung von 20+ Formaten!")
    
    uploaded_file = st.file_uploader("Excel oder CSV", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ {uploaded_file.name} geladen: {len(df)} Zeilen")
            
            if SMART_FEATURES:
                processor = SmartDataProcessor()
                mapping = processor.detect_column_mapping(df)
                
                if mapping:
                    st.success(f"✅ {len(mapping)} Spalten erkannt!")
                    
                    if st.button("🚀 Analysieren", type="primary"):
                        with st.spinner("Verarbeite..."):
                            df_clean, validation = processor.validate_and_clean(df, mapping)
                            analysis = processor.analyze_projects(df_clean)
                            
                            st.session_state.analysis_results = analysis
                            st.session_state.data_loaded = True
                            
                            st.success("✅ Analyse fertig!")
                            st.balloons()
            
            with st.expander("👁️ Vorschau"):
                st.dataframe(df.head(10))
                
        except Exception as e:
            st.error(f"❌ Fehler: {str(e)}")

def show_multifile_upload():
    st.header("📤 Multi-Source Upload")
    
    st.info("""
    🚀 **Multi-Source Intelligence!**
    
    Laden Sie mehrere Datenquellen für EIN Projekt:
    - 📊 Ressourcen (monatlich)
    - 📋 Ressourcen (Arbeitspakete)
    - 💰 Ist-Kosten
    - 📦 Arbeitspakete
    - 📈 Forecast
    """)
    
    uploaded_files = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Pflicht:**")
        f1 = st.file_uploader("📊 Ressourcen Monatlich", type=['csv','xlsx'], key='res_m')
        if f1:
            uploaded_files['res_m'] = f1
        
        f2 = st.file_uploader("💰 Ist-Kosten", type=['csv','xlsx'], key='ist')
        if f2:
            uploaded_files['ist'] = f2
        
        f3 = st.file_uploader("📦 Arbeitspakete", type=['csv','xlsx'], key='ap')
        if f3:
            uploaded_files['ap'] = f3
    
    with col2:
        st.markdown("**Optional:**")
        f4 = st.file_uploader("📋 Ressourcen AP", type=['csv','xlsx'], key='res_ap')
        if f4:
            uploaded_files['res_ap'] = f4
        
        f5 = st.file_uploader("📈 Forecast", type=['csv','xlsx'], key='fc')
        if f5:
            uploaded_files['fc'] = f5
    
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Dateien", len(uploaded_files))
    with col2:
        required = sum(1 for k in ['res_m','ist','ap'] if k in uploaded_files)
        st.metric("Pflicht", f"{required}/3")
    with col3:
        ready = required >= 3
        st.metric("Status", "✅ Bereit" if ready else "⏳ Warten")
    
    if ready and st.button("🚀 Integrieren", type="primary"):
        with st.spinner("Verarbeite..."):
            try:
                dfs = {}
                for key, file in uploaded_files.items():
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)
                    dfs[file.name] = df
                    st.success(f"✅ {file.name}: {len(df)} Zeilen")
                
                processor = MultiFileProcessor()
                integrated = processor.load_files(dfs)
                
                st.session_state.integrated_data = integrated
                st.session_state.multifile_loaded = True
                
                st.success("🎉 Integration erfolgreich!")
                
                summary = integrated['summary']
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Projekt", summary['project_id'])
                with col2:
                    st.metric("Budget", f"€{summary['total_budget']:,.0f}")
                with col3:
                    st.metric("Ist", f"€{summary['total_ist']:,.0f}")
                with col4:
                    st.metric("Prognose", f"€{summary['projected_total']:,.0f}", 
                             delta=f"{summary['deviation_pct']:+.1f}%")
                
                st.info("👉 Gehen Sie zum Dashboard!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")

def show_dashboard():
    st.header("📊 Dashboard")
    
    if st.session_state.multifile_loaded:
        data = st.session_state.integrated_data
        summary = data['summary']
        
        st.markdown("### 📈 Multi-Source Projekt-Übersicht")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Projekt", summary['project_id'])
        with col2:
            st.metric("Budget", f"€{summary['total_budget']:,.0f}")
        with col3:
            pct = summary['total_ist']/summary['total_budget']*100 if summary['total_budget'] > 0 else 0
            st.metric("Ist-Kosten", f"€{summary['total_ist']:,.0f}", delta=f"{pct:.0f}%")
        with col4:
            st.metric("Prognose", f"€{summary['projected_total']:,.0f}", 
                     delta=f"{summary['deviation_pct']:+.1f}%", delta_color="inverse")
        with col5:
            if 'budget_runway_months' in summary:
                st.metric("Reichweite", f"{summary['budget_runway_months']:.1f} Mon.")
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 💰 Finanzen")
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Budget', x=[''], y=[summary['total_budget']], marker_color='lightblue'))
            fig.add_trace(go.Bar(name='Ist', x=[''], y=[summary['total_ist']], marker_color='orange'))
            fig.add_trace(go.Bar(name='Forecast', x=[''], y=[summary['total_forecast']], marker_color='lightgreen'))
            fig.update_layout(barmode='group', height=300, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📦 Arbeitspakete")
            if data['arbeitspakete']:
                ap = data['arbeitspakete']['summary']
                pie_data = {
                    'Status': ['Fertig', 'In Arbeit', 'Nicht gestartet'],
                    'Anzahl': [ap['completed'], ap['in_progress'], ap['not_started']]
                }
                fig = px.pie(pie_data, values='Anzahl', names='Status',
                           color_discrete_map={'Fertig':'green','In Arbeit':'orange','Nicht gestartet':'gray'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            st.markdown("### 👥 Ressourcen")
            if data['ressourcen_monatlich']:
                res = data['ressourcen_monatlich']['summary']
                st.metric("Ø Mitarbeiter", f"{res['avg_mitarbeiter']:.1f}")
                st.metric("Peak", f"{res['peak_mitarbeiter']} MA")
                st.metric("Stunden", f"{res['total_stunden']:,.0f}h")
        
    elif st.session_state.data_loaded:
        analysis = st.session_state.analysis_results
        if analysis and 'summary' in analysis:
            summary = analysis['summary']
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Projekte", summary.get('total_projects', 0))
            with col2:
                st.metric("Plan", f"€{summary.get('total_cost_plan', 0):,.0f}")
            with col3:
                st.metric("Ist", f"€{summary.get('total_cost_actual', 0):,.0f}")
            with col4:
                st.metric("Abweichung", f"{summary.get('total_deviation_pct', 0):.1f}%")
    else:
        st.warning("⚠️ Keine Daten geladen! Bitte Upload nutzen.")

def show_report_page():
    st.header("📝 KI-Report Generator")
    
    if not st.session_state.data_loaded and not st.session_state.multifile_loaded:
        st.warning("⚠️ Bitte laden Sie zuerst Daten hoch!")
        return
    
    if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY']:
        st.error("❌ API Key fehlt!")
        return
    
    st.info("🤖 GPT-4 Report-Generierung")
    
    if st.button("🚀 Report generieren"):
        st.info("Report-Generierung in Entwicklung...")

def show_help_page():
    st.header("ℹ️ Anleitung")
    
    features = []
    if MULTIFILE_FEATURES:
        features.append("Multi-Source")
    if SMART_FEATURES:
        features.append("Smart Import")
    
    st.info(f"ControlBot mit {', '.join(features) if features else 'Standard'} Features")
    
    st.markdown("""
    ## 🚀 Schnellstart
    
    ### Single File:
    1. Daten Upload → Datei hochladen
    2. System erkennt Spalten automatisch
    3. Analysieren klicken
    4. Dashboard ansehen
    
    ### Multi-Source:
    1. Multi-Source Upload → 3-5 Dateien hochladen
    2. Integrieren klicken
    3. Dashboard ansehen
    
    ## 📋 Mock-Daten
    
    Im `mock_data/` Ordner finden Sie Beispiel-Dateien:
    - Ressourcen_Monatlich.csv
    - Ist_Kosten.csv
    - Arbeitspakete.csv
    - Ressourcen_Arbeitspakete.csv
    - Forecast.csv
    
    **Wichtig:** Alle Dateien müssen gleiche Projekt_ID haben!
    """)

if __name__ == "__main__":
    main()
