"""
Smart Data Processor für ControlBot
Erweiterte Version mit automatischer Spaltenerkennung, flexiblen Formaten und KI-Support
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import re
from difflib import get_close_matches

class SmartDataProcessor:
    """Intelligente Datenverarbeitung mit automatischer Erkennung"""
    
    # Spalten-Varianten für automatische Erkennung
    COLUMN_PATTERNS = {
        'projekt_name': [
            'projekt', 'project', 'projektname', 'project_name', 'name', 
            'projektbezeichnung', 'bezeichnung', 'task', 'aufgabe',
            'projektnummer', 'project_no', 'proj', 'psp', 'wbs'
        ],
        'kosten_plan': [
            'plan', 'budget', 'geplant', 'baseline', 'planned', 'soll',
            'kosten_plan', 'cost_plan', 'planned_cost', 'budget_cost',
            'baseline_cost', 'plan_cost', 'soll_kosten', 'plankosten'
        ],
        'kosten_ist': [
            'ist', 'actual', 'tatsächlich', 'aktuell', 'current',
            'kosten_ist', 'cost_actual', 'actual_cost', 'ist_kosten',
            'istkosten', 'tatsaechlich', 'real', 'effective'
        ],
        'kosten_forecast': [
            'forecast', 'prognose', 'hochrechnung', 'projection',
            'estimate', 'eac', 'estimate_at_completion', 'vorschau'
        ],
        'termin_plan': [
            'termin_plan', 'plan_date', 'planned_date', 'soll_termin',
            'baseline_date', 'start', 'end', 'finish', 'deadline',
            'plan_ende', 'geplantes_ende'
        ],
        'termin_ist': [
            'termin_ist', 'actual_date', 'ist_termin', 'tatsächlich',
            'completion_date', 'abschluss', 'fertigstellung'
        ],
        'status': [
            'status', 'state', 'zustand', 'phase', 'stage',
            'projektstatus', 'project_status'
        ],
        'verantwortlich': [
            'verantwortlich', 'owner', 'manager', 'pm', 'projektleiter',
            'project_manager', 'responsible', 'lead', 'leiter'
        ],
        'abteilung': [
            'abteilung', 'department', 'bereich', 'org', 'organization',
            'unit', 'team', 'gruppe', 'division'
        ],
        'prioritaet': [
            'priorität', 'priority', 'prio', 'wichtigkeit', 'importance'
        ],
        'risiko': [
            'risiko', 'risk', 'gefahr', 'threat', 'risk_level'
        ]
    }
    
    # Währungssymbole
    CURRENCY_SYMBOLS = {
        'EUR': ['€', 'EUR', 'Euro'],
        'USD': ['$', 'USD', 'Dollar'],
        'GBP': ['£', 'GBP', 'Pound'],
        'CHF': ['CHF', 'Franken'],
        'JPY': ['¥', 'JPY', 'Yen']
    }
    
    def __init__(self):
        self.df = None
        self.mapping = {}
        self.validation_results = {}
        self.detected_currency = 'EUR'
    
    def detect_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Erkennt automatisch, welche Spalte welchem Zweck dient
        
        Args:
            df: DataFrame mit unbekannten Spalten
            
        Returns:
            Dictionary mit Mapping: standard_name -> actual_column_name
        """
        mapping = {}
        used_columns = set()
        
        # Normalisiere Spalten-Namen für Vergleich
        normalized_columns = {
            col: self._normalize_string(col) 
            for col in df.columns
        }
        
        # Für jedes Standard-Feld
        for standard_field, patterns in self.COLUMN_PATTERNS.items():
            best_match = None
            best_score = 0
            
            # Suche beste Übereinstimmung
            for actual_col, normalized in normalized_columns.items():
                if actual_col in used_columns:
                    continue
                    
                # Exakte Übereinstimmung
                if normalized in patterns:
                    best_match = actual_col
                    best_score = 100
                    break
                
                # Fuzzy Match
                matches = get_close_matches(normalized, patterns, n=1, cutoff=0.6)
                if matches and len(matches) > 0:
                    score = self._similarity_score(normalized, matches[0])
                    if score > best_score:
                        best_match = actual_col
                        best_score = score
                
                # Substring Match
                for pattern in patterns:
                    if pattern in normalized or normalized in pattern:
                        score = 70
                        if score > best_score:
                            best_match = actual_col
                            best_score = score
            
            # Wenn gute Übereinstimmung gefunden
            if best_match and best_score > 50:
                mapping[standard_field] = best_match
                used_columns.add(best_match)
        
        return mapping
    
    def _normalize_string(self, s: str) -> str:
        """Normalisiert String für Vergleich"""
        s = str(s).lower()
        s = s.replace('_', '').replace('-', '').replace(' ', '')
        s = s.replace('ä', 'a').replace('ö', 'o').replace('ü', 'u').replace('ß', 'ss')
        return s
    
    def _similarity_score(self, s1: str, s2: str) -> float:
        """Berechnet Ähnlichkeit zwischen zwei Strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, s1, s2).ratio() * 100
    
    def parse_number(self, value: Any) -> Optional[float]:
        """
        Parsed verschiedene Zahlenformate
        
        Unterstützt:
        - 150000
        - 150.000 (Deutsch)
        - 150,000 (Englisch)
        - €150.000
        - $150,000
        - 150k
        - 150K
        - 1.5M
        """
        if pd.isna(value):
            return None
        
        # Bereits eine Zahl?
        if isinstance(value, (int, float)):
            return float(value)
        
        # String-Verarbeitung
        value_str = str(value).strip()
        
        # Entferne Währungssymbole
        for currency, symbols in self.CURRENCY_SYMBOLS.items():
            for symbol in symbols:
                value_str = value_str.replace(symbol, '')
        
        value_str = value_str.strip()
        
        # Handle k/K/m/M Suffixe
        multiplier = 1
        if value_str.endswith('k') or value_str.endswith('K'):
            multiplier = 1000
            value_str = value_str[:-1]
        elif value_str.endswith('m') or value_str.endswith('M'):
            multiplier = 1000000
            value_str = value_str[:-1]
        
        # Entferne Leerzeichen
        value_str = value_str.replace(' ', '')
        
        # Erkenne Format
        # Deutsche Notation: 1.234.567,89
        if ',' in value_str and '.' in value_str:
            if value_str.rindex(',') > value_str.rindex('.'):
                # Deutsches Format
                value_str = value_str.replace('.', '').replace(',', '.')
            else:
                # Englisches Format
                value_str = value_str.replace(',', '')
        # Nur Komma: könnte Deutsch oder Dezimaltrenner sein
        elif ',' in value_str:
            # Wenn mehr als ein Komma: Tausender-Trenner
            if value_str.count(',') > 1:
                value_str = value_str.replace(',', '')
            else:
                # Ansonsten: Dezimaltrenner (Deutsch)
                value_str = value_str.replace(',', '.')
        # Nur Punkt: könnte Englisch oder Deutsch sein
        elif '.' in value_str:
            # Wenn mehr als ein Punkt: Tausender-Trenner (Deutsch)
            if value_str.count('.') > 1:
                value_str = value_str.replace('.', '')
            # Sonst: Dezimaltrenner (Englisch)
        
        # Versuche zu parsen
        try:
            number = float(value_str) * multiplier
            return number
        except ValueError:
            return None
    
    def parse_date(self, value: Any) -> Optional[datetime]:
        """
        Parsed verschiedene Datumsformate
        
        Unterstützt:
        - 31.12.2024 (Deutsch)
        - 2024-12-31 (ISO)
        - 12/31/24 (US)
        - 31-12-2024
        - Dezember 2024
        """
        if pd.isna(value):
            return None
        
        if isinstance(value, datetime):
            return value
        
        if isinstance(value, pd.Timestamp):
            return value.to_pydatetime()
        
        value_str = str(value).strip()
        
        # Verschiedene Formate versuchen
        date_formats = [
            '%d.%m.%Y',      # 31.12.2024
            '%d.%m.%y',      # 31.12.24
            '%Y-%m-%d',      # 2024-12-31
            '%d-%m-%Y',      # 31-12-2024
            '%m/%d/%Y',      # 12/31/2024
            '%m/%d/%y',      # 12/31/24
            '%d/%m/%Y',      # 31/12/2024
            '%Y/%m/%d',      # 2024/12/31
            '%B %Y',         # December 2024
            '%b %Y',         # Dec 2024
            '%Y',            # 2024
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(value_str, fmt)
            except ValueError:
                continue
        
        # Pandas versuchen (sehr flexibel)
        try:
            return pd.to_datetime(value_str, dayfirst=True)
        except:
            return None
    
    def validate_and_clean(self, df: pd.DataFrame, mapping: Dict[str, str]) -> Tuple[pd.DataFrame, Dict]:
        """
        Validiert und bereinigt Daten mit ausführlichem Report
        """
        df_clean = df.copy()
        validation_report = {
            'total_rows': len(df),
            'issues': [],
            'warnings': [],
            'infos': [],
            'cleaned_rows': 0,
            'removed_rows': 0
        }
        
        # Standard-Spalten erstellen
        for standard_col, actual_col in mapping.items():
            if actual_col not in df.columns:
                continue
            
            # Kosten-Felder
            if 'kosten' in standard_col:
                df_clean[f'{standard_col}_original'] = df_clean[actual_col]
                df_clean[standard_col] = df_clean[actual_col].apply(self.parse_number)
                
                # Validierung
                nulls = df_clean[standard_col].isna().sum()
                if nulls > 0:
                    validation_report['warnings'].append(
                        f"{nulls} Zeilen mit ungültigen Werten in {actual_col} (Spalte: {standard_col})"
                    )
            
            # Datums-Felder
            elif 'termin' in standard_col or 'date' in standard_col:
                df_clean[f'{standard_col}_original'] = df_clean[actual_col]
                df_clean[standard_col] = df_clean[actual_col].apply(self.parse_date)
                
                nulls = df_clean[standard_col].isna().sum()
                if nulls > 0:
                    validation_report['warnings'].append(
                        f"{nulls} Zeilen mit ungültigen Daten in {actual_col}"
                    )
            
            # Text-Felder
            else:
                df_clean[standard_col] = df_clean[actual_col].astype(str).str.strip()
        
        # Pflichtfelder prüfen
        required = ['projekt_name', 'kosten_plan', 'kosten_ist']
        missing_required = [field for field in required if field not in mapping]
        
        if missing_required:
            validation_report['issues'].append(
                f"Fehlende Pflichtfelder: {', '.join(missing_required)}"
            )
        
        # Leere Zeilen entfernen
        rows_before = len(df_clean)
        df_clean = df_clean.dropna(how='all')
        rows_after = len(df_clean)
        validation_report['removed_rows'] = rows_before - rows_after
        
        if validation_report['removed_rows'] > 0:
            validation_report['infos'].append(
                f"{validation_report['removed_rows']} komplett leere Zeilen entfernt"
            )
        
        validation_report['cleaned_rows'] = rows_after
        
        return df_clean, validation_report

    def calculate_deviations(self, df: pd.DataFrame) -> pd.DataFrame:
        """Berechnet Abweichungen"""
        df_calc = df.copy()
        
        if 'kosten_plan' in df.columns and 'kosten_ist' in df.columns:
            df_calc['kosten_abweichung_absolut'] = df_calc['kosten_ist'] - df_calc['kosten_plan']
            
            df_calc['kosten_abweichung_prozent'] = df_calc.apply(
                lambda row: ((row['kosten_ist'] - row['kosten_plan']) / row['kosten_plan'] * 100) 
                if row['kosten_plan'] != 0 else 0,
                axis=1
            )
            
            def categorize_status(pct):
                if pct > 15:
                    return 'Kritisch'
                elif pct > 10:
                    return 'Risiko'
                elif pct > 5:
                    return 'Warnung'
                elif pct > -5:
                    return 'Im Plan'
                else:
                    return 'Unter Plan'
            
            df_calc['kosten_status'] = df_calc['kosten_abweichung_prozent'].apply(categorize_status)
        
        return df_calc
    
    def analyze_projects(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Erweiterte Projektanalyse"""
        df_analyzed = self.calculate_deviations(df)
        
        analysis = {
            'summary': {},
            'top_risk_projects': [],
            'top_performers': [],
            'status_distribution': {},
            'detailed_projects': []
        }
        
        total_projects = len(df_analyzed)
        
        if 'kosten_plan' in df_analyzed.columns:
            analysis['summary'] = {
                'total_projects': total_projects,
                'total_cost_plan': df_analyzed['kosten_plan'].sum(),
                'total_cost_actual': df_analyzed['kosten_ist'].sum() if 'kosten_ist' in df_analyzed.columns else 0,
            }
            
            if 'kosten_ist' in df_analyzed.columns:
                analysis['summary']['total_deviation'] = analysis['summary']['total_cost_actual'] - analysis['summary']['total_cost_plan']
                analysis['summary']['total_deviation_pct'] = (
                    analysis['summary']['total_deviation'] / analysis['summary']['total_cost_plan'] * 100
                    if analysis['summary']['total_cost_plan'] > 0 else 0
                )
                analysis['summary']['avg_cost_deviation_pct'] = df_analyzed['kosten_abweichung_prozent'].mean()
                analysis['summary']['max_cost_deviation_pct'] = df_analyzed['kosten_abweichung_prozent'].max()
                analysis['summary']['min_cost_deviation_pct'] = df_analyzed['kosten_abweichung_prozent'].min()
                
                analysis['summary']['projects_over_budget'] = len(df_analyzed[df_analyzed['kosten_abweichung_prozent'] > 0])
                analysis['summary']['projects_critical'] = len(df_analyzed[df_analyzed['kosten_status'] == 'Kritisch'])
                analysis['summary']['projects_warning'] = len(df_analyzed[df_analyzed['kosten_status'].isin(['Warnung', 'Risiko'])])
                analysis['summary']['projects_on_track'] = len(df_analyzed[df_analyzed['kosten_status'] == 'Im Plan'])
        
        if 'kosten_abweichung_prozent' in df_analyzed.columns:
            top_risks = df_analyzed.nlargest(10, 'kosten_abweichung_prozent')
            analysis['top_risk_projects'] = top_risks.to_dict('records')
            
            top_performers = df_analyzed.nsmallest(10, 'kosten_abweichung_prozent')
            analysis['top_performers'] = top_performers.to_dict('records')
        
        if 'kosten_status' in df_analyzed.columns:
            analysis['status_distribution'] = df_analyzed['kosten_status'].value_counts().to_dict()
        
        analysis['detailed_projects'] = df_analyzed.to_dict('records')
        
        return analysis

if __name__ == "__main__":
    print("Smart Data Processor geladen!")
