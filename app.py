"""
ControlBot v1.1 - KI-Assistent für Projektcontroller
Mit Smart Data Import und automatischer Spalten-Erkennung
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

from data_processor import DataProcessor
from ai_generator import AIReportGenerator
from report_builder import ReportBuilder
import plotly.express as px
import plotly.graph_objects as go

# Seitenkonfiguration
st.set_page_config(
    page_title="ControlBot - Ihr KI-Projektcontrolling-Assistent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialisiere Session State Variablen"""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'analysis_done' not in st.session_state:
        st.session_state.analysis_done = False
    if 'df' not in st.session_state:
        st.session_state.df = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

def main():
    """Hauptfunktion der Anwendung"""
    init_session_state()
    
    # Header
    version = "v1.1 Smart" if SMART_FEATURES else "v1.0"
    st.markdown(f'<div class="main-header">📊 ControlBot {version}</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ihr intelligenter Assistent für Projektcontrolling</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎯 Navigation")
        page = st.radio(
            "Wählen Sie eine Seite:",
            ["📤 Daten Upload", "📊 Dashboard", "📝 Report Generator", "ℹ️ Anleitung"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Einstellungen")
        
        # OpenAI API Key - Prüfe zuerst Streamlit Secrets
        api_key_from_secrets = None
        try:
            api_key_from_secrets = st.secrets.get("OPENAI_API_KEY", None)
        except:
            pass
        
        if api_key_from_secrets:
            os.environ['OPENAI_API_KEY'] = api_key_from_secrets
            st.success("✅ API Key aus Secrets geladen")
        else:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Ihr OpenAI API Key für die KI-Textgenerierung"
            )
            if api_key:
                os.environ['OPENAI_API_KEY'] = api_key
                st.success("✅ API Key gespeichert")
        
        st.markdown("---")
        st.markdown("### 📞 Support")
        st.info("Bei Fragen: support@controlbot.de")
        
        # Feature Info
        if SMART_FEATURES:
            st.markdown("---")
            st.markdown("### ✨ Smart Features")
            st.success("✅ Automatische Spalten-Erkennung")
            st.success("✅ Flexible Format-Parser")
            if TEMPLATE_FEATURES:
                st.success("✅ Template-System aktiv")
    
    # Hauptinhalt
    if page == "📤 Daten Upload":
        show_upload_page()
    elif page == "📊 Dashboard":
        show_dashboard_page()
    elif page == "📝 Report Generator":
        show_report_page()
    elif page == "ℹ️ Anleitung":
        show_help_page()

def show_upload_page():
    """Seite für Daten-Upload mit Smart Features"""
    st.header("📤 Projektdaten hochladen")
    
    # Smart Features Info
    if SMART_FEATURES:
        st.info("🚀 **Smart Import aktiviert:** Automatische Erkennung von 20+ Datenformaten!")
    
    # Template-Auswahl (wenn verfügbar)
    selected_template = None
    if TEMPLATE_FEATURES:
        template_mgr = TemplateManager()
        templates = template_mgr.list_templates()
        
        st.markdown("### 📋 Template wählen (optional)")
        template_options = ["Automatisch erkennen"] + [t['name'] for t in templates]
        selected_template_name = st.selectbox(
            "Datenformat:",
            template_options,
            help="Wählen Sie ein Template für Ihr Datenformat"
        )
        
        if selected_template_name != "Automatisch erkennen":
            # Finde Template-Key
            for t in templates:
                if t['name'] == selected_template_name:
                    selected_template = template_mgr.get_template(list(template_mgr.templates.keys())[templates.index(t)])
                    with st.expander(f"ℹ️ Info zu {selected_template_name}"):
                        st.write(f"**Quelle:** {selected_template.source_system}")
                        st.write(f"**Beschreibung:** {selected_template.description}")
                        st.code(selected_template.example_format, language="text")
                    break
    
    # File Upload
    st.markdown("### 📁 Datei hochladen")
    uploaded_file = st.file_uploader(
        "Wählen Sie eine Excel- oder CSV-Datei",
        type=['xlsx', 'xls', 'csv'],
        help="Unterstützt: .xlsx, .xls, .csv"
    )
    
    # Beispieldaten Download
    st.markdown("### 📥 Beispieldaten")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 Beispieldaten herunterladen"):
            st.info("Beispieldaten sind in der beispieldaten.csv enthalten")
    
    if uploaded_file is not None:
        try:
            # Datei laden
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Datei geladen: {len(df)} Zeilen, {len(df.columns)} Spalten")
            
            # Smart Processing
            if SMART_FEATURES:
                processor = SmartDataProcessor()
                
                # Automatische Spalten-Erkennung
                st.markdown("### 🔍 Automatische Erkennung")
                
                detected_mapping = processor.detect_column_mapping(df)
                
                if detected_mapping:
                    st.success(f"✅ {len(detected_mapping)} Spalten automatisch erkannt!")
                    
                    with st.expander("📋 Erkannte Zuordnungen anzeigen"):
                        for standard, actual in detected_mapping.items():
                            st.write(f"✓ **{actual}** → {standard}")
                    
                    # Daten validieren und bereinigen
                    if st.button("🚀 Daten analysieren", type="primary"):
                        with st.spinner("Verarbeite Daten..."):
                            df_clean, validation = processor.validate_and_clean(df, detected_mapping)
                            
                            # Validierungs-Report
                            st.markdown("### 📊 Validierungs-Ergebnis")
                            st.info(f"✅ {validation['cleaned_rows']} von {validation['total_rows']} Projekten erfolgreich geladen")
                            
                            if validation['warnings']:
                                st.warning("⚠️ **Warnungen:**")
                                for warning in validation['warnings']:
                                    st.write(f"  - {warning}")
                            
                            if validation['infos']:
                                with st.expander("💡 Weitere Informationen"):
                                    for info in validation['infos']:
                                        st.write(f"  - {info}")
                            
                            # Analyse durchführen
                            analysis = processor.analyze_projects(df_clean)
                            
                            # In Session State speichern
                            st.session_state.df = df_clean
                            st.session_state.analysis_results = analysis
                            st.session_state.data_loaded = True
                            st.session_state.analysis_done = True
                            
                            st.success("✅ Analyse abgeschlossen! Gehen Sie zum Dashboard.")
                            st.balloons()
                else:
                    st.warning("⚠️ Keine Spalten automatisch erkannt. Bitte prüfen Sie Ihr Datenformat.")
                    st.info("💡 Tipp: Nutzen Sie eines der vordefinierten Templates oder benennen Sie Spalten um.")
            
            else:
                # Fallback auf alte Methode
                st.warning("Smart Features nicht verfügbar. Verwende Standard-Import.")
                processor = DataProcessor()
                
                st.markdown("### 🔧 Spalten zuordnen")
                mapping = {}
                cols = st.columns(2)
                
                with cols[0]:
                    mapping['Projektname'] = st.selectbox("Projektname:", df.columns)
                    mapping['Kosten_Plan'] = st.selectbox("Kosten Plan:", df.columns)
                
                with cols[1]:
                    mapping['Kosten_Ist'] = st.selectbox("Kosten Ist:", df.columns)
                    mapping['Status'] = st.selectbox("Status (optional):", [''] + list(df.columns))
                
                if st.button("🚀 Daten analysieren", type="primary"):
                    with st.spinner("Analysiere Daten..."):
                        # Standard-Verarbeitung
                        df_processed = df.rename(columns=mapping)
                        st.session_state.df = df_processed
                        st.session_state.data_loaded = True
                        st.success("✅ Daten geladen!")
            
            # Datenvorschau
            with st.expander("👁️ Datenvorschau"):
                st.dataframe(df.head(10))
                
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei: {str(e)}")
            st.info("💡 Tipp: Prüfen Sie, ob die Datei das richtige Format hat.")

def show_dashboard_page():
    """Dashboard mit Visualisierungen"""
    st.header("📊 Projekt-Dashboard")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Bitte laden Sie zuerst Daten hoch!")
        return
    
    df = st.session_state.df
    analysis = st.session_state.analysis_results
    
    if analysis and 'summary' in analysis:
        # KPIs
        st.markdown("### 📈 Kennzahlen")
        cols = st.columns(4)
        
        summary = analysis['summary']
        
        with cols[0]:
            st.metric("Projekte gesamt", summary.get('total_projects', 0))
        
        with cols[1]:
            total_plan = summary.get('total_cost_plan', 0)
            st.metric("Kosten Plan", f"€{total_plan:,.0f}")
        
        with cols[2]:
            total_actual = summary.get('total_cost_actual', 0)
            st.metric("Kosten Ist", f"€{total_actual:,.0f}")
        
        with cols[3]:
            deviation_pct = summary.get('total_deviation_pct', 0)
            st.metric("Abweichung", f"{deviation_pct:.1f}%", 
                     delta=f"{deviation_pct:.1f}%",
                     delta_color="inverse")
        
        # Visualisierungen
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Status-Verteilung")
            if 'status_distribution' in analysis and analysis['status_distribution']:
                status_df = pd.DataFrame(
                    list(analysis['status_distribution'].items()),
                    columns=['Status', 'Anzahl']
                )
                fig = px.pie(status_df, values='Anzahl', names='Status',
                           color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### ⚠️ Top 5 Risiko-Projekte")
            if 'top_risk_projects' in analysis and analysis['top_risk_projects']:
                risk_df = pd.DataFrame(analysis['top_risk_projects'][:5])
                if 'projekt_name' in risk_df.columns and 'kosten_abweichung_prozent' in risk_df.columns:
                    fig = px.bar(risk_df, x='projekt_name', y='kosten_abweichung_prozent',
                               color='kosten_abweichung_prozent',
                               color_continuous_scale='Reds')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Projekt-Tabelle
        st.markdown("### 📋 Alle Projekte")
        if 'detailed_projects' in analysis:
            projects_df = pd.DataFrame(analysis['detailed_projects'])
            display_cols = [col for col in ['projekt_name', 'kosten_plan', 'kosten_ist', 
                                            'kosten_abweichung_prozent', 'kosten_status'] 
                          if col in projects_df.columns]
            if display_cols:
                st.dataframe(projects_df[display_cols], use_container_width=True)
    else:
        st.info("Führen Sie die Analyse auf der Upload-Seite durch.")

def show_report_page():
    """Report Generator Seite"""
    st.header("📝 KI-Report Generator")
    
    if not st.session_state.data_loaded:
        st.warning("⚠️ Bitte laden Sie zuerst Daten hoch!")
        return
    
    # API Key Check
    if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY']:
        st.error("❌ OpenAI API Key fehlt! Bitte in der Sidebar eingeben.")
        return
    
    st.info("🤖 Nutze GPT-4 für intelligente Report-Generierung")
    
    # Report-Optionen
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report-Typ:",
            ["Management Summary", "Detaillierter Controlling-Report", "Executive Briefing"]
        )
    
    with col2:
        language = st.selectbox("Sprache:", ["Deutsch", "English"])
    
    focus_areas = st.multiselect(
        "Fokus-Bereiche:",
        ["Kostenabweichungen", "Risiko-Projekte", "Terminabweichungen", "Handlungsempfehlungen"],
        default=["Kostenabweichungen", "Handlungsempfehlungen"]
    )
    
    if st.button("🚀 Report generieren", type="primary"):
        with st.spinner("Generiere Report mit GPT-4... (30-60 Sekunden)"):
            try:
                generator = AIReportGenerator()
                analysis = st.session_state.analysis_results
                
                report_content = generator.generate_report(
                    analysis,
                    report_type=report_type,
                    language=language,
                    focus_areas=focus_areas
                )
                
                st.success("✅ Report erfolgreich generiert!")
                
                # Report anzeigen
                st.markdown("### 📄 Generierter Report")
                st.markdown(report_content)
                
                # Word-Export
                builder = ReportBuilder()
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"controlbot_report_{timestamp}.docx"
                
                builder.create_report(report_content, analysis, filename)
                
                with open(filename, 'rb') as f:
                    st.download_button(
                        "📥 Report als Word herunterladen",
                        f,
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
            except Exception as e:
                st.error(f"❌ Fehler bei der Report-Generierung: {str(e)}")
                st.info("💡 Prüfen Sie, ob Ihr OpenAI API Key gültig ist und Guthaben vorhanden ist.")

def show_help_page():
    """Anleitung und Hilfe"""
    st.header("ℹ️ Anleitung")
    
    version_info = "v1.1 mit Smart Data Import" if SMART_FEATURES else "v1.0 Standard"
    st.info(f"📌 ControlBot {version_info}")
    
    st.markdown("""
    ## 🚀 Schnellstart
    
    1. **Daten hochladen** - Laden Sie Ihre Excel/CSV-Datei hoch
    2. **Automatische Erkennung** - Das System erkennt Spalten automatisch
    3. **Analyse** - Klicken Sie auf "Daten analysieren"
    4. **Dashboard** - Sehen Sie sich die Visualisierungen an
    5. **Report** - Generieren Sie KI-gestützte Reports
    
    ## 📋 Unterstützte Formate
    """)
    
    if SMART_FEATURES:
        st.success("""
        ✅ **Smart Import aktiviert!**
        - SAP Exporte
        - MS Project
        - Jira
        - Excel (beliebige Formate)
        - Automatische Zahlen- und Datums-Erkennung
        """)
    else:
        st.info("""
        📊 Standard-Import:
        - Excel (.xlsx, .xls)
        - CSV-Dateien
        - Manuelle Spalten-Zuordnung
        """)
    
    st.markdown("""
    ## 💡 Tipps
    
    - **Zahlenformate:** 150000, 150.000, €150k, $1.5M - alles funktioniert!
    - **Daten:** 31.12.2024, 2024-12-31, 12/31/24 - alles wird erkannt!
    - **Templates:** Nutzen Sie vordefinierte Templates für schnellere Verarbeitung
    
    ## 🆘 Probleme?
    
    - **API Key Fehler:** Prüfen Sie Ihren OpenAI Key und Guthaben
    - **Upload Fehler:** Prüfen Sie das Dateiformat
    - **Keine Erkennung:** Nutzen Sie ein vordefiniertes Template
    """)

if __name__ == "__main__":
    main()
