"""
Multi-File Upload UI für ControlBot
Ermöglicht Upload und Integration mehrerer Datenquellen
"""

import streamlit as st
import pandas as pd
from multi_file_processor import MultiFileProcessor

def show_multifile_upload():
    """Multi-File Upload Interface"""
    
    st.header("📤 Multi-Source Project Upload")
    
    st.info("""
    🚀 **Neu: Multi-Source Intelligence!**
    
    Laden Sie mehrere Datenquellen für EIN Projekt hoch:
    - 📊 Ressourcen (monatlich)
    - 📋 Ressourcen (pro Arbeitspaket)
    - 💰 Ist-Kosten
    - 📦 Arbeitspakete
    - 📈 Forecast
    
    ControlBot integriert alle Quellen automatisch!
    """)
    
    # File Uploaders
    st.markdown("### 📁 Datenquellen hochladen")
    
    uploaded_files = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Pflicht-Dateien:**")
        
        file1 = st.file_uploader(
            "📊 Ressourcen Monatlich",
            type=['csv', 'xlsx'],
            key='res_monthly',
            help="Monatliche Ressourcen-Übersicht"
        )
        if file1:
            uploaded_files['res_monthly'] = file1
        
        file2 = st.file_uploader(
            "💰 Ist-Kosten",
            type=['csv', 'xlsx'],
            key='ist_costs',
            help="Tatsächliche Kosten nach Monat"
        )
        if file2:
            uploaded_files['ist_costs'] = file2
        
        file3 = st.file_uploader(
            "📦 Arbeitspakete",
            type=['csv', 'xlsx'],
            key='work_packages',
            help="Arbeitspakete mit Status und Budget"
        )
        if file3:
            uploaded_files['work_packages'] = file3
    
    with col2:
        st.markdown("**Optional:**")
        
        file4 = st.file_uploader(
            "📋 Ressourcen Arbeitspakete",
            type=['csv', 'xlsx'],
            key='res_ap',
            help="Ressourcen-Zuordnung pro Arbeitspaket"
        )
        if file4:
            uploaded_files['res_ap'] = file4
        
        file5 = st.file_uploader(
            "📈 Forecast",
            type=['csv', 'xlsx'],
            key='forecast',
            help="Kosten-Prognose für kommende Quartale"
        )
        if file5:
            uploaded_files['forecast'] = file5
    
    # Status
    st.markdown("---")
    st.markdown("### 📊 Upload-Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Dateien hochgeladen", len(uploaded_files))
    with col2:
        required = 3  # res_monthly, ist_costs, work_packages
        has_required = sum(1 for k in ['res_monthly', 'ist_costs', 'work_packages'] if k in uploaded_files)
        st.metric("Pflicht-Dateien", f"{has_required}/{required}")
    with col3:
        can_process = has_required >= required
        st.metric("Status", "✅ Bereit" if can_process else "⏳ Warten")
    
    # Dateien anzeigen
    if uploaded_files:
        with st.expander("📋 Hochgeladene Dateien"):
            for key, file in uploaded_files.items():
                st.write(f"✓ {file.name} ({file.size:,} bytes)")
    
    # Verarbeiten
    if can_process and st.button("🚀 Daten integrieren und analysieren", type="primary"):
        with st.spinner("Verarbeite und integriere Datenquellen..."):
            try:
                # Lade alle Dateien
                dataframes = {}
                for key, file in uploaded_files.items():
                    if file.name.endswith('.csv'):
                        df = pd.read_csv(file)
                    else:
                        df = pd.read_excel(file)
                    dataframes[file.name] = df
                    st.success(f"✅ {file.name} geladen: {len(df)} Zeilen")
                
                # Verarbeite mit MultiFileProcessor
                processor = MultiFileProcessor()
                integrated_data = processor.load_files(dataframes)
                
                # Speichere in Session State
                st.session_state.integrated_data = integrated_data
                st.session_state.multifile_loaded = True
                
                # Erfolgs-Meldung
                st.success("🎉 Daten erfolgreich integriert!")
                
                # Summary anzeigen
                st.markdown("### 📊 Integrations-Übersicht")
                
                summary = integrated_data['summary']
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Projekt-ID", summary['project_id'])
                with col2:
                    st.metric("Datenquellen", summary['data_sources'])
                with col3:
                    st.metric("Budget", f"€{summary['total_budget']:,.0f}")
                with col4:
                    st.metric(
                        "Prognose", 
                        f"€{summary['projected_total']:,.0f}",
                        delta=f"{summary['deviation_pct']:+.1f}%",
                        delta_color="inverse"
                    )
                
                # Details
                with st.expander("🔍 Integrations-Details"):
                    st.write("**Geladene Datenquellen:**")
                    for source in integrated_data['files_loaded']:
                        if source != 'unknown':
                            st.write(f"✓ {source}")
                    
                    st.write("\n**Finanz-Übersicht:**")
                    st.write(f"- Budget gesamt: €{summary['total_budget']:,.0f}")
                    st.write(f"- Ist-Kosten: €{summary['total_ist']:,.0f}")
                    st.write(f"- Forecast: €{summary['total_forecast']:,.0f}")
                    st.write(f"- Prognose gesamt: €{summary['projected_total']:,.0f}")
                    st.write(f"- Abweichung: €{summary['deviation']:,.0f} ({summary['deviation_pct']:+.1f}%)")
                    
                    if 'burn_rate' in summary:
                        st.write(f"\n**Burn Rate:**")
                        st.write(f"- Durchschnitt: €{summary['burn_rate']:,.0f}/Monat")
                        st.write(f"- Budget-Reichweite: {summary.get('budget_runway_months', 0):.1f} Monate")
                
                st.info("👉 Gehen Sie zum **Multi-Source Dashboard** um die integrierte Ansicht zu sehen!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Fehler bei der Verarbeitung: {str(e)}")
                st.info("💡 Tipp: Stellen Sie sicher, dass alle Dateien eine Projekt_ID Spalte haben!")
    
    elif not can_process:
        st.warning("⚠️ Bitte laden Sie mindestens die 3 Pflicht-Dateien hoch!")
    
    # Download Beispiel-Dateien
    st.markdown("---")
    st.markdown("### 📥 Beispiel-Dateien")
    
    st.info("""
    💡 **Neu hier?** Laden Sie unsere Beispiel-Dateien herunter, um das Format zu sehen!
    
    Die Beispiel-Dateien zeigen ein realistisches ICE-Modernisierungs-Projekt.
    """)
    
    if st.button("📦 Beispiel-Daten als ZIP herunterladen"):
        st.info("Beispiel-Dateien sind in Ihrem Download-Ordner verfügbar!")

if __name__ == "__main__":
    show_multifile_upload()
