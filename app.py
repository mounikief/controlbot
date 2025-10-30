"""
ControlBot - KI-Assistent für Projektcontroller
Hauptanwendung mit Streamlit Web-Interface
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import os
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

# Custom CSS für besseres Design
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
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
    .danger-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
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
    st.markdown('<div class="main-header">📊 ControlBot</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ihr intelligenter Assistent für Projektcontrolling</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=ControlBot", use_container_width=True)
        st.markdown("---")
        st.markdown("### 🎯 Navigation")
        page = st.radio(
            "Wählen Sie eine Seite:",
            ["📤 Daten Upload", "📊 Dashboard", "📝 Report Generator", "ℹ️ Anleitung"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### ⚙️ Einstellungen")
        
        # OpenAI API Key - Prüfe zuerst Streamlit Secrets, dann User Input
        api_key_from_secrets = None
        try:
            # Versuche API Key aus Streamlit Secrets zu laden (für Cloud Deployment)
            api_key_from_secrets = st.secrets.get("OPENAI_API_KEY", None)
        except:
            pass
        
        if api_key_from_secrets:
            # API Key aus Secrets gefunden
            os.environ['OPENAI_API_KEY'] = api_key_from_secrets
            st.success("✅ API Key aus Secrets geladen")
        else:
            # Kein Secret gefunden, User Input ermöglichen
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
        
    # Hauptinhalt basierend auf gewählter Seite
    if page == "📤 Daten Upload":
        show_upload_page()
    elif page == "📊 Dashboard":
        show_dashboard_page()
    elif page == "📝 Report Generator":
        show_report_page()
    elif page == "ℹ️ Anleitung":
        show_help_page()

def show_upload_page():
    """Seite für Daten-Upload"""
    st.header("📤 Projektdaten hochladen")
    
    st.markdown("""
    ### Unterstützte Formate
    - **Excel** (.xlsx, .xls)
    - **CSV** (.csv)
    
    ### Erforderliche Spalten
    Ihre Datei sollte mindestens folgende Spalten enthalten:
    - **Projekt-ID** oder **Projektname**
    - **Kosten Plan** (geplante Kosten)
    - **Kosten Ist** (tatsächliche Kosten)
    - **Termin Plan** (geplanter Termin)
    - **Termin Ist** (tatsächlicher Termin) - optional
    """)
    
    # File Upload
    uploaded_file = st.file_uploader(
        "Wählen Sie eine Datei aus",
        type=['xlsx', 'xls', 'csv'],
        help="Laden Sie Ihre Projektcontrolling-Daten hoch"
    )
    
    if uploaded_file is not None:
        try:
            # Datei laden
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Datei erfolgreich geladen: {uploaded_file.name}")
            
            # Datenvorschau
            st.subheader("📋 Datenvorschau")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Datenstatistiken
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Anzahl Projekte", len(df))
            with col2:
                st.metric("Anzahl Spalten", len(df.columns))
            with col3:
                st.metric("Vollständigkeit", f"{(df.notna().sum().sum() / (df.shape[0] * df.shape[1]) * 100):.1f}%")
            
            # Spalten-Mapping
            st.subheader("🔗 Spalten-Zuordnung")
            st.markdown("Ordnen Sie Ihre Spalten den ControlBot-Feldern zu:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                project_col = st.selectbox("Projekt-ID / Projektname", df.columns, index=0)
                cost_plan_col = st.selectbox("Kosten Plan", [col for col in df.columns if 'plan' in col.lower() or 'soll' in col.lower()] or df.columns)
                cost_actual_col = st.selectbox("Kosten Ist", [col for col in df.columns if 'ist' in col.lower() or 'actual' in col.lower()] or df.columns)
            
            with col2:
                date_plan_col = st.selectbox("Termin Plan", [col for col in df.columns if 'termin' in col.lower() or 'date' in col.lower()] or df.columns)
                date_actual_col = st.selectbox("Termin Ist (optional)", ['Keine'] + list(df.columns))
                status_col = st.selectbox("Status (optional)", ['Keine'] + list(df.columns))
            
            # Daten verarbeiten Button
            if st.button("🚀 Daten analysieren", type="primary", use_container_width=True):
                with st.spinner("Analysiere Projektdaten..."):
                    try:
                        # Daten verarbeiten
                        processor = DataProcessor()
                        
                        # Spalten umbenennen für einheitliche Verarbeitung
                        df_mapped = df.copy()
                        df_mapped['projekt_name'] = df[project_col]
                        df_mapped['kosten_plan'] = pd.to_numeric(df[cost_plan_col], errors='coerce')
                        df_mapped['kosten_ist'] = pd.to_numeric(df[cost_actual_col], errors='coerce')
                        
                        # Analyse durchführen
                        analysis_results = processor.analyze_projects(df_mapped)
                        
                        # In Session State speichern
                        st.session_state.df = df_mapped
                        st.session_state.analysis_results = analysis_results
                        st.session_state.data_loaded = True
                        st.session_state.analysis_done = True
                        
                        st.success("✅ Analyse erfolgreich abgeschlossen!")
                        st.info("👉 Gehen Sie zum **Dashboard** oder **Report Generator**")
                        
                    except Exception as e:
                        st.error(f"❌ Fehler bei der Analyse: {str(e)}")
        
        except Exception as e:
            st.error(f"❌ Fehler beim Laden der Datei: {str(e)}")
    
    # Beispieldaten Download
    st.markdown("---")
    st.subheader("📥 Beispieldaten")
    st.markdown("Sie können unsere Beispieldatei herunterladen, um das Format zu sehen:")
    
    # Erstelle Beispieldaten
    example_data = pd.DataFrame({
        'Projekt_ID': ['PRJ-001', 'PRJ-002', 'PRJ-003', 'PRJ-004', 'PRJ-005'],
        'Projektname': ['Neues CRM System', 'Website Relaunch', 'ERP Upgrade', 'Mobile App', 'Cloud Migration'],
        'Kosten_Plan': [150000, 75000, 200000, 120000, 180000],
        'Kosten_Ist': [165000, 72000, 225000, 135000, 180000],
        'Termin_Plan': ['2024-12-31', '2024-09-30', '2025-03-31', '2024-11-30', '2025-01-31'],
        'Status': ['In Progress', 'Completed', 'At Risk', 'In Progress', 'On Track']
    })
    
    csv = example_data.to_csv(index=False)
    st.download_button(
        label="📥 Beispieldaten herunterladen (CSV)",
        data=csv,
        file_name="controlbot_beispieldaten.csv",
        mime="text/csv"
    )

def show_dashboard_page():
    """Dashboard-Seite mit Visualisierungen"""
    st.header("📊 Projekt-Dashboard")
    
    if not st.session_state.analysis_done:
        st.warning("⚠️ Bitte laden Sie zuerst Daten auf der **Upload-Seite** hoch.")
        return
    
    results = st.session_state.analysis_results
    df = st.session_state.df
    
    # KPI-Übersicht
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_projects = results['summary']['total_projects']
        st.metric("Gesamt Projekte", total_projects)
    
    with col2:
        projects_over_budget = results['summary']['projects_over_budget']
        pct_over = (projects_over_budget / total_projects * 100) if total_projects > 0 else 0
        st.metric("Über Budget", f"{projects_over_budget}", f"{pct_over:.1f}%")
    
    with col3:
        avg_cost_deviation = results['summary']['avg_cost_deviation_pct']
        st.metric("Ø Kostenabweichung", f"{avg_cost_deviation:.1f}%")
    
    with col4:
        total_planned = results['summary']['total_cost_plan']
        total_actual = results['summary']['total_cost_actual']
        st.metric("Gesamtkosten", f"€{total_actual:,.0f}", f"€{total_actual - total_planned:,.0f}")
    
    st.markdown("---")
    
    # Visualisierungen
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Kosten: Plan vs. Ist")
        
        # Balkendiagramm für Kosten
        fig_costs = go.Figure()
        fig_costs.add_trace(go.Bar(
            name='Plan',
            x=df['projekt_name'],
            y=df['kosten_plan'],
            marker_color='lightblue'
        ))
        fig_costs.add_trace(go.Bar(
            name='Ist',
            x=df['projekt_name'],
            y=df['kosten_ist'],
            marker_color='coral'
        ))
        fig_costs.update_layout(
            barmode='group',
            xaxis_title='Projekt',
            yaxis_title='Kosten (€)',
            height=400
        )
        st.plotly_chart(fig_costs, use_container_width=True)
    
    with col2:
        st.subheader("📊 Abweichungsanalyse")
        
        # Berechne Abweichungen
        df['abweichung_pct'] = ((df['kosten_ist'] - df['kosten_plan']) / df['kosten_plan'] * 100)
        
        # Farbcodierung
        colors = ['red' if x > 10 else 'orange' if x > 0 else 'green' for x in df['abweichung_pct']]
        
        fig_deviation = go.Figure(go.Bar(
            x=df['projekt_name'],
            y=df['abweichung_pct'],
            marker_color=colors,
            text=df['abweichung_pct'].round(1).astype(str) + '%',
            textposition='outside'
        ))
        fig_deviation.update_layout(
            xaxis_title='Projekt',
            yaxis_title='Abweichung (%)',
            height=400
        )
        fig_deviation.add_hline(y=0, line_dash="dash", line_color="gray")
        st.plotly_chart(fig_deviation, use_container_width=True)
    
    # Risiko-Projekte
    st.markdown("---")
    st.subheader("⚠️ Risiko-Projekte")
    
    risk_projects = df[df['abweichung_pct'] > 10].copy()
    
    if len(risk_projects) > 0:
        st.markdown('<div class="danger-box">', unsafe_allow_html=True)
        st.markdown(f"**{len(risk_projects)} Projekt(e) mit Kostenüberschreitung > 10%**")
        st.dataframe(
            risk_projects[['projekt_name', 'kosten_plan', 'kosten_ist', 'abweichung_pct']].style.format({
                'kosten_plan': '€{:,.0f}',
                'kosten_ist': '€{:,.0f}',
                'abweichung_pct': '{:.1f}%'
            }),
            use_container_width=True
        )
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("✅ **Keine kritischen Risiko-Projekte identifiziert**")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Projekt-Details-Tabelle
    st.markdown("---")
    st.subheader("📋 Projekt-Details")
    
    display_df = df[['projekt_name', 'kosten_plan', 'kosten_ist', 'abweichung_pct']].copy()
    display_df.columns = ['Projekt', 'Plan (€)', 'Ist (€)', 'Abweichung (%)']
    
    st.dataframe(
        display_df.style.format({
            'Plan (€)': '€{:,.0f}',
            'Ist (€)': '€{:,.0f}',
            'Abweichung (%)': '{:.1f}%'
        }).background_gradient(subset=['Abweichung (%)'], cmap='RdYlGn_r'),
        use_container_width=True
    )

def show_report_page():
    """Report-Generator Seite"""
    st.header("📝 KI-Report Generator")
    
    if not st.session_state.analysis_done:
        st.warning("⚠️ Bitte laden Sie zuerst Daten auf der **Upload-Seite** hoch.")
        return
    
    # Prüfe ob API Key vorhanden
    if 'OPENAI_API_KEY' not in os.environ or not os.environ['OPENAI_API_KEY']:
        st.error("❌ Bitte geben Sie Ihren OpenAI API Key in der Sidebar ein.")
        st.info("💡 Sie benötigen einen OpenAI API Key, um KI-generierte Reports zu erstellen. Registrieren Sie sich auf platform.openai.com")
        return
    
    st.markdown("""
    Generieren Sie einen professionellen Management-Report mit KI-gestützten Analysen und Handlungsempfehlungen.
    """)
    
    # Report-Optionen
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Report-Typ",
            ["Management Summary", "Detaillierter Controlling-Report", "Executive Briefing"]
        )
        
        language = st.selectbox(
            "Sprache",
            ["Deutsch", "Englisch"]
        )
    
    with col2:
        include_recommendations = st.checkbox("Handlungsempfehlungen einschließen", value=True)
        include_charts = st.checkbox("Diagramme einbetten", value=True)
        detail_level = st.select_slider(
            "Detailgrad",
            options=["Kurz", "Mittel", "Ausführlich"],
            value="Mittel"
        )
    
    # Zusätzliche Informationen
    st.subheader("📌 Zusätzliche Kontext-Informationen (optional)")
    context_info = st.text_area(
        "Fügen Sie zusätzliche Informationen hinzu, die im Report berücksichtigt werden sollen:",
        placeholder="z.B. Besondere Herausforderungen, strategische Ziele, bekannte Risiken...",
        height=100
    )
    
    # Report generieren
    if st.button("🚀 Report generieren", type="primary", use_container_width=True):
        with st.spinner("Generiere KI-gestützten Report... Dies kann 30-60 Sekunden dauern."):
            try:
                # AI Generator initialisieren
                ai_generator = AIReportGenerator()
                
                # Report-Parameter
                params = {
                    'report_type': report_type,
                    'language': language,
                    'include_recommendations': include_recommendations,
                    'detail_level': detail_level,
                    'context': context_info
                }
                
                # Report generieren
                report_content = ai_generator.generate_report(
                    st.session_state.analysis_results,
                    st.session_state.df,
                    params
                )
                
                # Report Builder
                report_builder = ReportBuilder()
                
                # Word-Dokument erstellen
                doc_path = report_builder.create_word_report(
                    report_content,
                    st.session_state.df,
                    include_charts
                )
                
                st.success("✅ Report erfolgreich generiert!")
                
                # Vorschau anzeigen
                st.subheader("📄 Report-Vorschau")
                with st.expander("Report-Inhalt anzeigen", expanded=True):
                    st.markdown(report_content)
                
                # Download-Button
                with open(doc_path, 'rb') as file:
                    st.download_button(
                        label="📥 Report als Word-Dokument herunterladen",
                        data=file,
                        file_name=f"ControlBot_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True
                    )
                
            except Exception as e:
                st.error(f"❌ Fehler beim Generieren des Reports: {str(e)}")
                st.info("💡 Tipp: Stellen Sie sicher, dass Ihr OpenAI API Key gültig ist und Sie genug Credits haben.")

def show_help_page():
    """Hilfe und Anleitung"""
    st.header("ℹ️ Anleitung & Hilfe")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Schnellstart", "📊 Datenformat", "🔑 API Setup", "❓ FAQ"])
    
    with tab1:
        st.markdown("""
        ## 🚀 Schnellstart-Anleitung
        
        ### Schritt 1: OpenAI API Key einrichten
        1. Gehen Sie zu [platform.openai.com](https://platform.openai.com)
        2. Erstellen Sie einen Account (falls noch nicht vorhanden)
        3. Navigieren Sie zu API Keys und erstellen Sie einen neuen Key
        4. Geben Sie den Key in der Sidebar ein
        
        ### Schritt 2: Daten hochladen
        1. Gehen Sie zur Seite **"📤 Daten Upload"**
        2. Laden Sie Ihre Excel oder CSV-Datei hoch
        3. Ordnen Sie die Spalten zu
        4. Klicken Sie auf **"Daten analysieren"**
        
        ### Schritt 3: Dashboard anzeigen
        1. Gehen Sie zur Seite **"📊 Dashboard"**
        2. Sehen Sie sich die KPIs und Visualisierungen an
        3. Identifizieren Sie Risiko-Projekte
        
        ### Schritt 4: Report generieren
        1. Gehen Sie zur Seite **"📝 Report Generator"**
        2. Wählen Sie Report-Optionen
        3. Generieren und laden Sie Ihren Report herunter
        """)
    
    with tab2:
        st.markdown("""
        ## 📊 Datenformat-Anforderungen
        
        ### Mindestanforderungen
        Ihre Datei muss mindestens diese Spalten enthalten:
        
        | Spalte | Beschreibung | Beispiel |
        |--------|--------------|----------|
        | Projekt-ID/Name | Eindeutige Kennung | PRJ-001 |
        | Kosten Plan | Geplante Kosten | 150000 |
        | Kosten Ist | Tatsächliche Kosten | 165000 |
        | Termin Plan | Geplanter Abschluss | 2024-12-31 |
        
        ### Optionale Spalten
        - **Termin Ist**: Tatsächlicher Abschluss
        - **Status**: Projektstatus (z.B. "In Progress", "Completed")
        - **Verantwortlich**: Projektleiter
        - **Abteilung**: Zuständige Abteilung
        
        ### Formatierungshinweise
        - **Zahlen**: Verwenden Sie numerische Werte ohne Währungszeichen
        - **Daten**: Format YYYY-MM-DD (z.B. 2024-12-31)
        - **Text**: UTF-8 Kodierung für Umlaute
        
        ### Beispieldatei
        Laden Sie die Beispieldatei auf der Upload-Seite herunter, um das korrekte Format zu sehen.
        """)
    
    with tab3:
        st.markdown("""
        ## 🔑 OpenAI API Setup
        
        ### Was ist ein API Key?
        Ein API Key ist wie ein Passwort, das ControlBot erlaubt, die OpenAI KI-Services zu nutzen.
        
        ### Wie bekomme ich einen API Key?
        1. **Registrierung**: Gehen Sie zu [platform.openai.com](https://platform.openai.com)
        2. **Account erstellen**: Registrieren Sie sich mit Ihrer E-Mail
        3. **Zahlungsmethode**: Fügen Sie eine Zahlungsmethode hinzu (Kreditkarte)
        4. **API Key erstellen**: 
           - Navigieren Sie zu "API Keys"
           - Klicken Sie auf "Create new secret key"
           - Kopieren Sie den Key (er wird nur einmal angezeigt!)
        
        ### Kosten
        - Die OpenAI API ist **pay-as-you-go**
        - Typische Kosten für einen Report: €0.10 - €0.50
        - Sie können Limits setzen, um Kosten zu kontrollieren
        - Neue Accounts erhalten oft $5 gratis Credits
        
        ### Sicherheit
        - ⚠️ **Teilen Sie Ihren API Key niemals** mit anderen
        - Der Key wird nur in Ihrer aktuellen Session gespeichert
        - Bei Verdacht auf Missbrauch: Key sofort bei OpenAI löschen
        """)
    
    with tab4:
        st.markdown("""
        ## ❓ Häufig gestellte Fragen
        
        ### Allgemein
        
        **Q: Ist meine Daten sicher?**  
        A: Ja. Ihre Daten werden nur temporär verarbeitet und nicht gespeichert. Die OpenAI API verarbeitet Daten gemäß ihrer Datenschutzrichtlinien.
        
        **Q: Kann ich ControlBot offline nutzen?**  
        A: Nein, für die KI-Funktionen benötigen Sie eine Internetverbindung zur OpenAI API.
        
        **Q: Welche Dateigröße wird unterstützt?**  
        A: Aktuell bis zu 5.000 Zeilen. Für größere Datensätze kontaktieren Sie uns.
        
        ### Technisch
        
        **Q: Welche Excel-Versionen werden unterstützt?**  
        A: .xlsx (Excel 2007+) und .xls (Excel 97-2003)
        
        **Q: Kann ich mehrere Dateien gleichzeitig hochladen?**  
        A: Im MVP noch nicht, aber diese Funktion ist für Version 2.0 geplant.
        
        **Q: Werden Formeln aus Excel übernommen?**  
        A: Nein, nur die Werte werden verarbeitet.
        
        ### Reports
        
        **Q: Kann ich eigene Report-Templates erstellen?**  
        A: Diese Funktion kommt in Version 2.0.
        
        **Q: In welchen Formaten kann ich Reports exportieren?**  
        A: Aktuell Word (.docx). PDF-Export kommt bald.
        
        ### Support
        
        **Q: Wo kann ich Fehler melden?**  
        A: Per E-Mail an support@controlbot.de
        
        **Q: Gibt es Tutorials?**  
        A: Video-Tutorials sind in Planung und werden auf unserer Website verfügbar sein.
        """)
    
    # Kontakt
    st.markdown("---")
    st.subheader("💬 Weitere Fragen?")
    st.info("Kontaktieren Sie uns: **support@controlbot.de**")

if __name__ == "__main__":
    main()
