# 📊 ControlBot - KI-Assistent für Projektcontroller

> Intelligentes Projektcontrolling mit KI-gestützten Reports und automatisierten Analysen

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## 🎯 Was ist ControlBot?

ControlBot ist ein **KI-gestützter Assistent für Projektcontroller**, der:
- 📊 Projektdaten automatisch analysiert
- 🤖 Professionelle Reports mit GPT-4 generiert
- ⚠️ Risiko-Projekte frühzeitig identifiziert
- 💡 Handlungsempfehlungen gibt
- 📝 Word-Dokumente automatisch erstellt

**Zeitersparnis:** Bis zu 95% bei der Erstellung von Controlling-Reports!

---

## ✨ Features

### 📤 Daten-Upload
- Excel (.xlsx, .xls) und CSV Support
- Automatische Validierung
- Intelligentes Spalten-Mapping
- Beispieldaten zum Testen

### 📊 Interaktives Dashboard
- KPIs auf einen Blick
- Plan vs. Ist Vergleiche
- Abweichungsanalysen
- Risiko-Projekt-Identifikation
- Farbcodierte Warnungen

### 🤖 KI-Report-Generator
- Management Summaries
- Detaillierte Controlling-Reports
- Executive Briefings
- Mehrsprachig (DE/EN)
- Handlungsempfehlungen
- Word-Export

### 📈 Automatische Analysen
- Kostenabweichungen
- Status-Kategorisierung
- Top 5 Risiko-Projekte
- Top 5 Best Performers
- Umfangreiche Statistiken

---

## 🚀 Quick Start

### Lokale Installation

```bash
# Repository klonen
git clone https://github.com/IHR-USERNAME/controlbot.git
cd controlbot

# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installieren
pip install -r requirements.txt

# OpenAI API Key setzen
export OPENAI_API_KEY="sk-..."  # Windows: set OPENAI_API_KEY=sk-...

# App starten
streamlit run app.py
```

Die App öffnet sich automatisch unter `http://localhost:8501`

### Cloud Deployment (Streamlit Cloud)

1. Forken Sie dieses Repository
2. Gehen Sie zu [share.streamlit.io](https://share.streamlit.io)
3. Wählen Sie Ihr Repository
4. Fügen Sie `OPENAI_API_KEY` als Secret hinzu
5. Deployen Sie!

**Detaillierte Anleitung:** Siehe [DEPLOYMENT_ANLEITUNG.md](DEPLOYMENT_ANLEITUNG.md)

---

## 📋 Voraussetzungen

- Python 3.9 oder höher
- OpenAI API Key ([platform.openai.com](https://platform.openai.com))
- Ca. 1 GB freier Speicher

---

## 🎓 Verwendung

### 1. Daten vorbereiten

Ihre Excel/CSV-Datei sollte mindestens enthalten:
- Projektname/ID
- Kosten Plan
- Kosten Ist
- Optional: Termine, Status, Verantwortliche

**Beispiel:**
| Projektname | Kosten_Plan | Kosten_Ist | Status |
|-------------|-------------|------------|---------|
| CRM System  | 150000      | 165000     | In Progress |
| Website     | 75000       | 72000      | Completed |

### 2. Upload & Analyse

1. Datei hochladen
2. Spalten zuordnen
3. "Daten analysieren" klicken
4. Fertig! ✅

### 3. Dashboard nutzen

- KPIs überprüfen
- Risiko-Projekte identifizieren
- Visualisierungen ansehen

### 4. Report generieren

1. Report-Typ wählen
2. Optionen festlegen
3. "Report generieren" klicken
4. Word-Dokument herunterladen

---

## 🛠️ Technologie

- **Frontend:** Streamlit
- **Backend:** Python 3.9+
- **KI:** OpenAI GPT-4
- **Datenverarbeitung:** Pandas, NumPy
- **Visualisierung:** Plotly, Matplotlib
- **Dokumente:** python-docx

---

## 📦 Projekt-Struktur

```
controlbot/
├── app.py                  # Hauptanwendung
├── data_processor.py       # Datenverarbeitung
├── ai_generator.py         # KI-Integration
├── report_builder.py       # Report-Erstellung
├── requirements.txt        # Dependencies
├── beispieldaten.csv       # Test-Daten
├── .streamlit/
│   └── config.toml        # Streamlit-Konfiguration
└── README.md              # Diese Datei
```

---

## 🔐 Sicherheit

- ✅ Lokale Datenverarbeitung (keine permanente Speicherung)
- ✅ API Keys werden als Secrets gespeichert
- ✅ Keine Daten-Weitergabe an Dritte (außer OpenAI für Reports)
- ⚠️ Für sensible Daten: Projektnamen anonymisieren

---

## 💰 Kosten

### Streamlit Cloud:
- **Hosting:** Kostenlos (Community Cloud)
- **Limits:** 1 GB RAM, 1 CPU Core
- **Uptime:** ~99%

### OpenAI API:
- **Pay-as-you-go:** Nur nutzen, was Sie brauchen
- **Kosten pro Report:** ~€0.10 - €0.50
- **Neue Accounts:** Oft $5 gratis Credits

---

## 📈 Roadmap

### Version 2.0 (geplant)
- [ ] Multi-File-Upload
- [ ] PDF-Export
- [ ] Custom Report-Templates
- [ ] Historische Trend-Analysen
- [ ] Team-Features & User-Management
- [ ] Direkte ERP-Integration (SAP, etc.)
- [ ] Mobile App
- [ ] Predictive Analytics

---

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch (`git checkout -b feature/AmazingFeature`)
3. Committen Sie Ihre Änderungen (`git commit -m 'Add AmazingFeature'`)
4. Pushen Sie den Branch (`git push origin feature/AmazingFeature`)
5. Öffnen Sie einen Pull Request

---

## 📄 Lizenz

© 2024 ControlBot. Alle Rechte vorbehalten.

Diese Software ist für den persönlichen und kommerziellen Gebrauch lizenziert.

---

## 📞 Support & Kontakt

- **E-Mail:** support@controlbot.de
- **Issues:** [GitHub Issues](https://github.com/IHR-USERNAME/controlbot/issues)
- **Dokumentation:** Siehe README und DEPLOYMENT_ANLEITUNG.md

---

## 🙏 Credits

Entwickelt mit:
- [Streamlit](https://streamlit.io)
- [OpenAI GPT-4](https://openai.com)
- [Pandas](https://pandas.pydata.org)
- [Plotly](https://plotly.com)

---

## ⭐ Star History

Wenn Ihnen dieses Projekt gefällt, geben Sie ihm einen Stern! ⭐

---

**Made with ❤️ für Projektcontroller weltweit**
