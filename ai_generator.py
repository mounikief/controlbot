"""
AI Report Generator für ControlBot
Nutzt OpenAI GPT für intelligente Report-Generierung
"""

import os
from typing import Dict, List, Any
import pandas as pd
from openai import OpenAI

class AIReportGenerator:
    """Klasse für KI-gestützte Report-Generierung"""
    
    def __init__(self):
        """Initialisiert den AI Generator mit OpenAI Client"""
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API Key nicht gefunden. Bitte in Umgebungsvariablen setzen.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"  # Kosteneffektives Model
    
    def generate_report(
        self, 
        analysis_results: Dict[str, Any], 
        df: pd.DataFrame,
        params: Dict[str, Any]
    ) -> str:
        """
        Generiert einen vollständigen Report mit KI
        
        Args:
            analysis_results: Dictionary mit Analyseergebnissen
            df: Original DataFrame mit Projektdaten
            params: Report-Parameter (Typ, Sprache, etc.)
            
        Returns:
            Vollständiger Report als Markdown-Text
        """
        # Extrahiere relevante Daten
        summary = analysis_results['summary']
        risk_projects = analysis_results['top_risk_projects']
        top_performers = analysis_results['top_performers']
        
        # Baue Prompt für GPT
        prompt = self._build_prompt(summary, risk_projects, top_performers, params)
        
        # Rufe OpenAI API auf
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(params)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            report_text = response.choices[0].message.content
            
            # Formatiere den Report
            formatted_report = self._format_report(report_text, params)
            
            return formatted_report
            
        except Exception as e:
            raise Exception(f"Fehler bei OpenAI API Aufruf: {str(e)}")
    
    def _get_system_prompt(self, params: Dict[str, Any]) -> str:
        """
        Erstellt den System Prompt basierend auf Report-Parametern
        
        Args:
            params: Report-Parameter
            
        Returns:
            System Prompt als String
        """
        language = params.get('language', 'Deutsch')
        report_type = params.get('report_type', 'Management Summary')
        detail_level = params.get('detail_level', 'Mittel')
        
        system_prompt = f"""Du bist ein erfahrener Projektcontroller und Business Analyst mit 15+ Jahren Erfahrung.
        
Deine Aufgabe ist es, professionelle Projektcontrolling-Reports zu erstellen.

Sprache: {language}
Report-Typ: {report_type}
Detailgrad: {detail_level}

Schreibstil:
- Professionell aber verständlich
- Faktenbasiert und objektiv
- Handlungsorientiert
- Nutze Bullet Points für bessere Lesbarkeit
- Verwende klare Überschriften
- Hebe wichtige Zahlen hervor

Struktur:
1. Executive Summary (2-3 Sätze)
2. Wichtigste Erkenntnisse (3-5 Punkte)
3. Detailanalyse
4. Handlungsempfehlungen (wenn angefordert)
5. Fazit

WICHTIG: 
- Alle Zahlen präzise aus den Daten übernehmen
- Keine Spekulationen, nur faktenbasierte Aussagen
- Konkrete, umsetzbare Empfehlungen geben
"""
        
        return system_prompt
    
    def _build_prompt(
        self,
        summary: Dict[str, Any],
        risk_projects: List[Dict],
        top_performers: List[Dict],
        params: Dict[str, Any]
    ) -> str:
        """
        Baut den User Prompt mit allen Daten
        
        Args:
            summary: Zusammenfassung der Analyse
            risk_projects: Liste der Risiko-Projekte
            top_performers: Liste der Top-Performer
            params: Report-Parameter
            
        Returns:
            User Prompt als String
        """
        context = params.get('context', '')
        include_recommendations = params.get('include_recommendations', True)
        
        prompt = f"""Erstelle einen professionellen Projektcontrolling-Report basierend auf folgenden Daten:

## GESAMTÜBERSICHT
- Anzahl Projekte: {summary['total_projects']}
- Gesamtkosten Plan: €{summary['total_cost_plan']:,.0f}
- Gesamtkosten Ist: €{summary['total_cost_actual']:,.0f}
- Gesamtabweichung: €{summary['total_deviation']:,.0f} ({summary['total_deviation_pct']:.1f}%)

## PROJEKTSTATUS
- Kritische Projekte (>10% Überschreitung): {summary['projects_critical']}
- Projekte mit Warnung (5-10% Überschreitung): {summary['projects_warning']}
- Projekte im Plan: {summary['projects_on_track']}
- Projekte über Budget: {summary['projects_over_budget']}

## KENNZAHLEN
- Durchschnittliche Kostenabweichung: {summary['avg_cost_deviation_pct']:.1f}%
- Höchste Einzelabweichung: {summary['max_cost_deviation_pct']:.1f}%
- Niedrigste Einzelabweichung: {summary['min_cost_deviation_pct']:.1f}%

## TOP 3 RISIKO-PROJEKTE
"""
        
        for i, project in enumerate(risk_projects[:3], 1):
            prompt += f"""
{i}. {project['projekt_name']}
   - Plan: €{project['kosten_plan']:,.0f}
   - Ist: €{project['kosten_ist']:,.0f}
   - Abweichung: {project['kosten_abweichung_prozent']:.1f}%
   - Status: {project['kosten_status']}
"""
        
        prompt += "\n## TOP 3 BEST PERFORMERS\n"
        
        for i, project in enumerate(top_performers[:3], 1):
            prompt += f"""
{i}. {project['projekt_name']}
   - Plan: €{project['kosten_plan']:,.0f}
   - Ist: €{project['kosten_ist']:,.0f}
   - Abweichung: {project['kosten_abweichung_prozent']:.1f}%
   - Status: {project['kosten_status']}
"""
        
        if context:
            prompt += f"\n## ZUSÄTZLICHER KONTEXT\n{context}\n"
        
        if include_recommendations:
            prompt += """
## ANFORDERUNG
Erstelle einen Report mit folgenden Elementen:
1. Executive Summary
2. Situationsanalyse
3. Kritische Projekte im Detail
4. Konkrete Handlungsempfehlungen für jedes Risiko-Projekt
5. Nächste Schritte und Prioritäten
6. Fazit

Die Handlungsempfehlungen sollten:
- Spezifisch und umsetzbar sein
- Zeitrahmen enthalten
- Verantwortlichkeiten definieren
- Risiken adressieren
"""
        else:
            prompt += """
## ANFORDERUNG
Erstelle einen Report mit folgenden Elementen:
1. Executive Summary
2. Situationsanalyse
3. Kritische Projekte im Detail
4. Fazit
"""
        
        return prompt
    
    def _format_report(self, report_text: str, params: Dict[str, Any]) -> str:
        """
        Formatiert den generierten Report
        
        Args:
            report_text: Von GPT generierter Text
            params: Report-Parameter
            
        Returns:
            Formatierter Report
        """
        # Füge Header hinzu
        from datetime import datetime
        
        header = f"""# ControlBot Projektcontrolling Report
**Erstellt am:** {datetime.now().strftime('%d.%m.%Y um %H:%M Uhr')}
**Report-Typ:** {params.get('report_type', 'Standard')}
**Sprache:** {params.get('language', 'Deutsch')}

---

"""
        
        # Füge Footer hinzu
        footer = """

---

*Dieser Report wurde automatisch mit ControlBot AI generiert.*
*Die Daten basieren auf den hochgeladenen Projektinformationen.*
"""
        
        return header + report_text + footer
    
    def generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generiert nur ein kurzes Executive Summary
        
        Args:
            analysis_results: Dictionary mit Analyseergebnissen
            
        Returns:
            Executive Summary als Text
        """
        summary = analysis_results['summary']
        
        prompt = f"""Erstelle ein kurzes Executive Summary (max. 3 Sätze) für folgende Projektportfolio-Situation:

- {summary['total_projects']} Projekte im Portfolio
- Gesamtbudget Plan: €{summary['total_cost_plan']:,.0f}
- Gesamtkosten Ist: €{summary['total_cost_actual']:,.0f}
- Abweichung: {summary['total_deviation_pct']:.1f}%
- {summary['projects_critical']} kritische Projekte

Das Summary sollte die wichtigste Botschaft vermitteln und zum Handeln auffordern, falls nötig.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Du bist ein erfahrener Projektcontroller. Erstelle prägnante Executive Summaries."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Executive Summary konnte nicht generiert werden: {str(e)}"
    
    def generate_recommendations(self, risk_projects: List[Dict]) -> List[str]:
        """
        Generiert spezifische Handlungsempfehlungen für Risiko-Projekte
        
        Args:
            risk_projects: Liste der Risiko-Projekte
            
        Returns:
            Liste mit Handlungsempfehlungen
        """
        recommendations = []
        
        for project in risk_projects[:5]:  # Top 5 Risiken
            prompt = f"""Gib eine konkrete, umsetzbare Handlungsempfehlung für folgendes Projekt:

Projektname: {project['projekt_name']}
Geplante Kosten: €{project['kosten_plan']:,.0f}
Tatsächliche Kosten: €{project['kosten_ist']:,.0f}
Abweichung: {project['kosten_abweichung_prozent']:.1f}%
Status: {project['kosten_status']}

Die Empfehlung sollte:
- In 2-3 Sätzen formuliert sein
- Konkrete Maßnahmen enthalten
- Einen Zeitrahmen nennen
- Priorität angeben (Hoch/Mittel/Niedrig)

Format: "[PRIORITÄT] Empfehlung: ..."
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "Du bist ein erfahrener Projektmanagement-Berater."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.6,
                    max_tokens=150
                )
                
                recommendation = response.choices[0].message.content
                recommendations.append(f"{project['projekt_name']}: {recommendation}")
                
            except Exception as e:
                recommendations.append(f"{project['projekt_name']}: Empfehlung konnte nicht generiert werden")
        
        return recommendations

if __name__ == "__main__":
    # Test des Moduls (erfordert OPENAI_API_KEY in Umgebung)
    print("AI Report Generator Module geladen.")
    print("Für Tests OPENAI_API_KEY als Umgebungsvariable setzen.")
