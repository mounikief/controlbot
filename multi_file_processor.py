"""
Multi-File Data Processor für ControlBot
Integriert mehrere Datenquellen zu einem Projekt
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple

class MultiFileProcessor:
    """Verarbeitet und integriert mehrere Datenquellen"""
    
    def __init__(self):
        self.project_data = {}
        self.validation_results = {}
    
    def detect_file_type(self, df: pd.DataFrame) -> str:
        """
        Erkennt automatisch den Dateityp anhand der Spalten
        """
        columns = [col.lower() for col in df.columns]
        
        # Ressourcen Monatlich
        if any('mitarbeiter' in col for col in columns) and any('monat' in col for col in columns):
            if not any('ap' in col or 'arbeitspaket' in col for col in columns):
                return 'ressourcen_monatlich'
        
        # Ressourcen Arbeitspakete
        if any('ap' in col or 'arbeitspaket' in col for col in columns) and any('ressourcen' in col for col in columns):
            return 'ressourcen_arbeitspakete'
        
        # Ist-Kosten
        if any('ist' in col and 'kosten' in col for col in columns) and any('kategorie' in col for col in columns):
            return 'ist_kosten'
        
        # Arbeitspakete
        if any('status' in col for col in columns) and any('fortschritt' in col for col in columns):
            return 'arbeitspakete'
        
        # Forecast
        if any('forecast' in col for col in columns) and any('quartal' in col for col in columns):
            return 'forecast'
        
        return 'unknown'
    
    def extract_project_id(self, df: pd.DataFrame) -> str:
        """
        Extrahiert die Projekt-ID aus dem DataFrame
        """
        # Suche nach Projekt_ID Spalte
        for col in df.columns:
            if 'projekt' in col.lower() and 'id' in col.lower():
                # Nimm die erste Projekt-ID
                return str(df[col].iloc[0])
        
        return None
    
    def load_files(self, files_dict: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Lädt und verarbeitet mehrere Dateien
        
        Args:
            files_dict: Dictionary mit {filename: DataFrame}
            
        Returns:
            Integrierte Projekt-Daten
        """
        project_id = None
        categorized_files = {}
        
        # Kategorisiere Dateien
        for filename, df in files_dict.items():
            file_type = self.detect_file_type(df)
            
            # Extrahiere Projekt-ID
            pid = self.extract_project_id(df)
            if pid:
                if project_id is None:
                    project_id = pid
                elif project_id != pid:
                    raise ValueError(f"Verschiedene Projekt-IDs gefunden: {project_id} vs {pid}")
            
            categorized_files[file_type] = df
        
        if project_id is None:
            raise ValueError("Keine Projekt-ID gefunden!")
        
        # Integriere Daten
        integrated_data = self.integrate_data(project_id, categorized_files)
        
        return integrated_data
    
    def integrate_data(self, project_id: str, files: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Integriert alle Datenquellen zu einem Master-View
        """
        integrated = {
            'project_id': project_id,
            'files_loaded': list(files.keys()),
            'ressourcen_monatlich': None,
            'ressourcen_arbeitspakete': None,
            'ist_kosten': None,
            'arbeitspakete': None,
            'forecast': None,
            'summary': {}
        }
        
        # Verarbeite jeden Dateityp
        if 'ressourcen_monatlich' in files:
            integrated['ressourcen_monatlich'] = self._process_ressourcen_monatlich(
                files['ressourcen_monatlich']
            )
        
        if 'ressourcen_arbeitspakete' in files:
            integrated['ressourcen_arbeitspakete'] = self._process_ressourcen_arbeitspakete(
                files['ressourcen_arbeitspakete']
            )
        
        if 'ist_kosten' in files:
            integrated['ist_kosten'] = self._process_ist_kosten(
                files['ist_kosten']
            )
        
        if 'arbeitspakete' in files:
            integrated['arbeitspakete'] = self._process_arbeitspakete(
                files['arbeitspakete']
            )
        
        if 'forecast' in files:
            integrated['forecast'] = self._process_forecast(
                files['forecast']
            )
        
        # Berechne Summary
        integrated['summary'] = self._calculate_summary(integrated)
        
        return integrated
    
    def _process_ressourcen_monatlich(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verarbeitet monatliche Ressourcen-Daten"""
        df_clean = df.copy()
        
        # Konvertiere Monat zu datetime
        if 'Monat' in df_clean.columns:
            df_clean['Monat'] = pd.to_datetime(df_clean['Monat'])
        
        summary = {
            'total_months': len(df_clean),
            'avg_mitarbeiter': df_clean['Mitarbeiter'].mean() if 'Mitarbeiter' in df_clean.columns else 0,
            'total_stunden': df_clean['Stunden'].sum() if 'Stunden' in df_clean.columns else 0,
            'total_kosten_plan': df_clean['Kosten_Plan'].sum() if 'Kosten_Plan' in df_clean.columns else 0,
            'peak_month': df_clean.loc[df_clean['Mitarbeiter'].idxmax(), 'Monat'] if 'Mitarbeiter' in df_clean.columns else None,
            'peak_mitarbeiter': df_clean['Mitarbeiter'].max() if 'Mitarbeiter' in df_clean.columns else 0
        }
        
        return {
            'data': df_clean,
            'summary': summary
        }
    
    def _process_ressourcen_arbeitspakete(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verarbeitet Ressourcen pro Arbeitspaket"""
        df_clean = df.copy()
        
        if 'Monat' in df_clean.columns:
            df_clean['Monat'] = pd.to_datetime(df_clean['Monat'])
        
        # Gruppiere nach Arbeitspaket
        ap_summary = df_clean.groupby('AP_Name').agg({
            'Ressourcen': 'sum',
            'Stunden': 'sum',
            'Kosten': 'sum'
        }).to_dict('index')
        
        return {
            'data': df_clean,
            'summary': ap_summary
        }
    
    def _process_ist_kosten(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verarbeitet Ist-Kosten"""
        df_clean = df.copy()
        
        if 'Monat' in df_clean.columns:
            df_clean['Monat'] = pd.to_datetime(df_clean['Monat'])
        
        # Gruppiere nach Monat
        monthly_total = df_clean.groupby('Monat')['Kosten_Ist'].sum()
        
        # Kategorien
        category_total = df_clean.groupby('Kategorie')['Kosten_Ist'].sum()
        
        summary = {
            'total_ist': df_clean['Kosten_Ist'].sum(),
            'avg_monthly': monthly_total.mean(),
            'months_tracked': len(monthly_total),
            'by_category': category_total.to_dict(),
            'burn_rate': monthly_total.mean()  # Durchschnittliche monatliche Kosten
        }
        
        return {
            'data': df_clean,
            'monthly_total': monthly_total,
            'summary': summary
        }
    
    def _process_arbeitspakete(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verarbeitet Arbeitspakete"""
        df_clean = df.copy()
        
        # Konvertiere Daten
        if 'Start' in df_clean.columns:
            df_clean['Start'] = pd.to_datetime(df_clean['Start'])
        if 'Ende' in df_clean.columns:
            df_clean['Ende'] = pd.to_datetime(df_clean['Ende'])
        
        # Konvertiere Fortschritt
        if 'Fortschritt' in df_clean.columns:
            df_clean['Fortschritt_Num'] = df_clean['Fortschritt'].str.rstrip('%').astype('float')
        
        summary = {
            'total_ap': len(df_clean),
            'completed': len(df_clean[df_clean['Status'] == 'Done']),
            'in_progress': len(df_clean[df_clean['Status'] == 'In Progress']),
            'not_started': len(df_clean[df_clean['Status'] == 'Not Started']),
            'total_budget': df_clean['Budget'].sum() if 'Budget' in df_clean.columns else 0,
            'total_ist': df_clean['Ist'].sum() if 'Ist' in df_clean.columns else 0,
            'avg_progress': df_clean['Fortschritt_Num'].mean() if 'Fortschritt_Num' in df_clean.columns else 0
        }
        
        return {
            'data': df_clean,
            'summary': summary
        }
    
    def _process_forecast(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Verarbeitet Forecast-Daten"""
        df_clean = df.copy()
        
        summary = {
            'total_forecast': df_clean['Kosten_Forecast'].sum() if 'Kosten_Forecast' in df_clean.columns else 0,
            'quarters': len(df_clean),
            'avg_confidence': df_clean['Konfidenz'].str.rstrip('%').astype('float').mean() if 'Konfidenz' in df_clean.columns else 0
        }
        
        return {
            'data': df_clean,
            'summary': summary
        }
    
    def _calculate_summary(self, integrated: Dict[str, Any]) -> Dict[str, Any]:
        """Berechnet Gesamt-Summary über alle Datenquellen"""
        summary = {
            'project_id': integrated['project_id'],
            'data_sources': len([f for f in integrated['files_loaded'] if f != 'unknown'])
        }
        
        # Budget-Zahlen
        total_budget = 0
        total_ist = 0
        total_forecast = 0
        
        # Aus Arbeitspaketen
        if integrated['arbeitspakete']:
            total_budget = integrated['arbeitspakete']['summary']['total_budget']
            total_ist = integrated['arbeitspakete']['summary']['total_ist']
        
        # Aus Ist-Kosten (überschreibt wenn verfügbar)
        if integrated['ist_kosten']:
            total_ist = integrated['ist_kosten']['summary']['total_ist']
        
        # Aus Forecast
        if integrated['forecast']:
            total_forecast = integrated['forecast']['summary']['total_forecast']
        
        summary['total_budget'] = total_budget
        summary['total_ist'] = total_ist
        summary['total_forecast'] = total_forecast
        summary['projected_total'] = total_ist + total_forecast
        summary['deviation'] = summary['projected_total'] - total_budget
        summary['deviation_pct'] = (summary['deviation'] / total_budget * 100) if total_budget > 0 else 0
        
        # Burn Rate
        if integrated['ist_kosten']:
            summary['burn_rate'] = integrated['ist_kosten']['summary']['burn_rate']
            months_remaining = (total_budget - total_ist) / summary['burn_rate'] if summary['burn_rate'] > 0 else 0
            summary['budget_runway_months'] = max(0, months_remaining)
        
        return summary

if __name__ == "__main__":
    print("Multi-File Processor geladen!")
