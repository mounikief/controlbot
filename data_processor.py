"""
Data Processor für ControlBot
Verarbeitet und analysiert Projektdaten
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any

class DataProcessor:
    """Klasse für Datenverarbeitung und -analyse"""
    
    def __init__(self):
        self.df = None
        self.analysis_results = {}
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Lädt Daten aus Excel oder CSV
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            DataFrame mit den geladenen Daten
        """
        if file_path.endswith('.csv'):
            self.df = pd.read_csv(file_path)
        else:
            self.df = pd.read_excel(file_path)
        
        return self.df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validiert die Daten auf Vollständigkeit und Korrektheit
        
        Args:
            df: DataFrame zum Validieren
            
        Returns:
            Dictionary mit Validierungsergebnissen
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'info': {}
        }
        
        # Prüfe erforderliche Spalten
        required_columns = ['projekt_name', 'kosten_plan', 'kosten_ist']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            validation_results['is_valid'] = False
            validation_results['errors'].append(f"Fehlende Spalten: {', '.join(missing_columns)}")
        
        # Prüfe auf leere Werte
        for col in required_columns:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                if null_count > 0:
                    validation_results['warnings'].append(
                        f"Spalte '{col}' hat {null_count} leere Werte"
                    )
        
        # Prüfe Datentypen
        numeric_columns = ['kosten_plan', 'kosten_ist']
        for col in numeric_columns:
            if col in df.columns:
                try:
                    pd.to_numeric(df[col], errors='coerce')
                except:
                    validation_results['errors'].append(
                        f"Spalte '{col}' enthält nicht-numerische Werte"
                    )
        
        # Info über Datensatz
        validation_results['info'] = {
            'row_count': len(df),
            'column_count': len(df.columns),
            'completeness': f"{(df.notna().sum().sum() / (df.shape[0] * df.shape[1]) * 100):.1f}%"
        }
        
        return validation_results
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Bereinigt die Daten
        
        Args:
            df: DataFrame zum Bereinigen
            
        Returns:
            Bereinigter DataFrame
        """
        df_clean = df.copy()
        
        # Entferne Duplikate
        df_clean = df_clean.drop_duplicates()
        
        # Konvertiere numerische Spalten
        numeric_columns = ['kosten_plan', 'kosten_ist']
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
        
        # Fülle fehlende Werte mit 0 (nur für numerische Spalten)
        for col in numeric_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].fillna(0)
        
        # Bereinige Text-Spalten
        if 'projekt_name' in df_clean.columns:
            df_clean['projekt_name'] = df_clean['projekt_name'].astype(str).str.strip()
        
        return df_clean
    
    def calculate_deviations(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Berechnet Abweichungen zwischen Plan und Ist
        
        Args:
            df: DataFrame mit Plan- und Ist-Werten
            
        Returns:
            DataFrame mit berechneten Abweichungen
        """
        df_calc = df.copy()
        
        # Kostenabweichung absolut
        df_calc['kosten_abweichung_absolut'] = df_calc['kosten_ist'] - df_calc['kosten_plan']
        
        # Kostenabweichung prozentual
        df_calc['kosten_abweichung_prozent'] = (
            (df_calc['kosten_ist'] - df_calc['kosten_plan']) / df_calc['kosten_plan'] * 100
        ).fillna(0)
        
        # Status-Kategorisierung basierend auf Abweichung
        def categorize_status(pct):
            if pct > 10:
                return 'Kritisch'
            elif pct > 5:
                return 'Warnung'
            elif pct > -5:
                return 'Im Plan'
            else:
                return 'Unter Plan'
        
        df_calc['kosten_status'] = df_calc['kosten_abweichung_prozent'].apply(categorize_status)
        
        return df_calc
    
    def analyze_projects(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Führt umfassende Projektanalyse durch
        
        Args:
            df: DataFrame mit Projektdaten
            
        Returns:
            Dictionary mit Analyseergebnissen
        """
        # Daten bereinigen
        df_clean = self.clean_data(df)
        
        # Abweichungen berechnen
        df_analyzed = self.calculate_deviations(df_clean)
        
        # Gesamtstatistiken berechnen
        total_projects = len(df_analyzed)
        projects_over_budget = len(df_analyzed[df_analyzed['kosten_abweichung_prozent'] > 0])
        projects_critical = len(df_analyzed[df_analyzed['kosten_status'] == 'Kritisch'])
        projects_warning = len(df_analyzed[df_analyzed['kosten_status'] == 'Warnung'])
        projects_on_track = len(df_analyzed[df_analyzed['kosten_status'] == 'Im Plan'])
        
        # Finanzielle Kennzahlen
        total_cost_plan = df_analyzed['kosten_plan'].sum()
        total_cost_actual = df_analyzed['kosten_ist'].sum()
        total_deviation = total_cost_actual - total_cost_plan
        total_deviation_pct = (total_deviation / total_cost_plan * 100) if total_cost_plan > 0 else 0
        
        avg_cost_deviation_pct = df_analyzed['kosten_abweichung_prozent'].mean()
        max_cost_deviation_pct = df_analyzed['kosten_abweichung_prozent'].max()
        min_cost_deviation_pct = df_analyzed['kosten_abweichung_prozent'].min()
        
        # Top 5 Risiko-Projekte (höchste Überschreitung)
        top_risk_projects = df_analyzed.nlargest(5, 'kosten_abweichung_prozent')[
            ['projekt_name', 'kosten_plan', 'kosten_ist', 'kosten_abweichung_prozent', 'kosten_status']
        ].to_dict('records')
        
        # Top 5 Best Performer (größte Unterschreitung oder im Plan)
        top_performers = df_analyzed.nsmallest(5, 'kosten_abweichung_prozent')[
            ['projekt_name', 'kosten_plan', 'kosten_ist', 'kosten_abweichung_prozent', 'kosten_status']
        ].to_dict('records')
        
        # Verteilung nach Status
        status_distribution = df_analyzed['kosten_status'].value_counts().to_dict()
        
        # Erstelle Analyseergebnis
        analysis_results = {
            'summary': {
                'total_projects': total_projects,
                'projects_over_budget': projects_over_budget,
                'projects_critical': projects_critical,
                'projects_warning': projects_warning,
                'projects_on_track': projects_on_track,
                'total_cost_plan': total_cost_plan,
                'total_cost_actual': total_cost_actual,
                'total_deviation': total_deviation,
                'total_deviation_pct': total_deviation_pct,
                'avg_cost_deviation_pct': avg_cost_deviation_pct,
                'max_cost_deviation_pct': max_cost_deviation_pct,
                'min_cost_deviation_pct': min_cost_deviation_pct
            },
            'top_risk_projects': top_risk_projects,
            'top_performers': top_performers,
            'status_distribution': status_distribution,
            'detailed_projects': df_analyzed.to_dict('records')
        }
        
        self.analysis_results = analysis_results
        return analysis_results
    
    def get_insights(self, analysis_results: Dict[str, Any]) -> List[str]:
        """
        Generiert automatische Insights aus den Analyseergebnissen
        
        Args:
            analysis_results: Dictionary mit Analyseergebnissen
            
        Returns:
            Liste mit Insight-Texten
        """
        insights = []
        summary = analysis_results['summary']
        
        # Insight 1: Gesamtbudget-Situation
        if summary['total_deviation_pct'] > 10:
            insights.append(
                f"⚠️ KRITISCH: Das Gesamtportfolio liegt {summary['total_deviation_pct']:.1f}% "
                f"über dem geplanten Budget (€{abs(summary['total_deviation']):,.0f} Überschreitung)."
            )
        elif summary['total_deviation_pct'] > 0:
            insights.append(
                f"⚡ ACHTUNG: Leichte Budgetüberschreitung von {summary['total_deviation_pct']:.1f}% "
                f"(€{abs(summary['total_deviation']):,.0f})."
            )
        else:
            insights.append(
                f"✅ POSITIV: Portfolio liegt {abs(summary['total_deviation_pct']):.1f}% unter Budget "
                f"(€{abs(summary['total_deviation']):,.0f} Einsparung)."
            )
        
        # Insight 2: Anzahl kritischer Projekte
        critical_pct = (summary['projects_critical'] / summary['total_projects'] * 100) if summary['total_projects'] > 0 else 0
        if summary['projects_critical'] > 0:
            insights.append(
                f"🚨 {summary['projects_critical']} von {summary['total_projects']} Projekten "
                f"({critical_pct:.0f}%) sind kritisch (>10% Überschreitung)."
            )
        
        # Insight 3: Durchschnittliche Abweichung
        if summary['avg_cost_deviation_pct'] > 5:
            insights.append(
                f"📊 Die durchschnittliche Kostenabweichung beträgt {summary['avg_cost_deviation_pct']:.1f}%. "
                f"Dies deutet auf systematische Planungsprobleme hin."
            )
        
        # Insight 4: Extremwerte
        if summary['max_cost_deviation_pct'] > 20:
            insights.append(
                f"⚠️ Größte Einzelabweichung: {summary['max_cost_deviation_pct']:.1f}%. "
                f"Sofortige Eskalation empfohlen."
            )
        
        # Insight 5: Positive Performer
        if summary['min_cost_deviation_pct'] < -10:
            insights.append(
                f"💡 Best Practice: Ein Projekt liegt {abs(summary['min_cost_deviation_pct']):.1f}% unter Budget. "
                f"Lessons Learned dokumentieren."
            )
        
        return insights
    
    def export_summary(self, analysis_results: Dict[str, Any], file_path: str) -> None:
        """
        Exportiert Analyseergebnisse als Excel
        
        Args:
            analysis_results: Dictionary mit Analyseergebnissen
            file_path: Pfad für Export-Datei
        """
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # Summary Sheet
            summary_df = pd.DataFrame([analysis_results['summary']])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Risiko-Projekte
            if analysis_results['top_risk_projects']:
                risk_df = pd.DataFrame(analysis_results['top_risk_projects'])
                risk_df.to_excel(writer, sheet_name='Risiko-Projekte', index=False)
            
            # Top Performer
            if analysis_results['top_performers']:
                performer_df = pd.DataFrame(analysis_results['top_performers'])
                performer_df.to_excel(writer, sheet_name='Top-Performer', index=False)
            
            # Alle Projekte
            if analysis_results['detailed_projects']:
                detailed_df = pd.DataFrame(analysis_results['detailed_projects'])
                detailed_df.to_excel(writer, sheet_name='Alle-Projekte', index=False)

if __name__ == "__main__":
    # Test des Moduls
    processor = DataProcessor()
    
    # Erstelle Test-Daten
    test_data = pd.DataFrame({
        'projekt_name': ['Projekt A', 'Projekt B', 'Projekt C'],
        'kosten_plan': [100000, 200000, 150000],
        'kosten_ist': [110000, 190000, 175000]
    })
    
    # Analysiere
    results = processor.analyze_projects(test_data)
    
    # Zeige Ergebnisse
    print("Analyse abgeschlossen:")
    print(f"Gesamt Projekte: {results['summary']['total_projects']}")
    print(f"Über Budget: {results['summary']['projects_over_budget']}")
    print(f"Durchschnittliche Abweichung: {results['summary']['avg_cost_deviation_pct']:.2f}%")
