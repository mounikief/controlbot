"""
Template Manager für ControlBot
Verwaltet vordefinierte Templates für verschiedene Datenquellen
"""

import json
from typing import Dict, List, Any
from dataclasses import dataclass, asdict

@dataclass
class DataTemplate:
    """Repräsentiert ein Daten-Template"""
    name: str
    description: str
    source_system: str
    column_mapping: Dict[str, str]
    expected_columns: List[str]
    special_handling: Dict[str, str]
    example_format: str

class TemplateManager:
    """Verwaltet Templates für verschiedene Datenquellen"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
    
    def _load_default_templates(self) -> Dict[str, DataTemplate]:
        """Lädt vordefinierte Templates"""
        templates = {}
        
        # Template 1: SAP Export
        templates['sap'] = DataTemplate(
            name="SAP Projekt-Export",
            description="Standard-Export aus SAP PS/PPM",
            source_system="SAP",
            column_mapping={
                'projekt_name': 'Projektdefinition',
                'kosten_plan': 'Plankosten',
                'kosten_ist': 'Istkosten',
                'kosten_forecast': 'Forecast',
                'termin_plan': 'Basisendtermin',
                'termin_ist': 'Istendtermin',
                'status': 'Systemstatus',
                'verantwortlich': 'Projektleiter',
                'abteilung': 'Buchungskreis'
            },
            expected_columns=[
                'Projektdefinition', 'PSP-Element', 'Plankosten', 
                'Istkosten', 'Systemstatus'
            ],
            special_handling={
                'currency': 'EUR',
                'date_format': 'DD.MM.YYYY',
                'number_format': 'DE'
            },
            example_format="""
Projektdefinition | PSP-Element | Plankosten | Istkosten | Systemstatus
P-12345          | A.1.2.3     | 150.000,00 | 165.000,00| TEIL
            """
        )
        
        # Template 2: MS Project
        templates['msproject'] = DataTemplate(
            name="Microsoft Project Export",
            description="Export aus MS Project",
            source_system="MS Project",
            column_mapping={
                'projekt_name': 'Name',
                'kosten_plan': 'Baseline Cost',
                'kosten_ist': 'Actual Cost',
                'kosten_forecast': 'Cost',
                'termin_plan': 'Baseline Finish',
                'termin_ist': 'Actual Finish',
                'status': 'Status',
                'verantwortlich': 'Resource Names',
                'prioritaet': 'Priority'
            },
            expected_columns=[
                'Name', 'Baseline Cost', 'Actual Cost', 'Cost', 'Status'
            ],
            special_handling={
                'currency': 'USD',
                'date_format': 'MM/DD/YYYY',
                'number_format': 'EN'
            },
            example_format="""
Name     | Baseline Cost | Actual Cost | Cost Variance | Status
Project A| $150,000      | $165,000    | $15,000       | In Progress
            """
        )
        
        # Template 3: Jira/Confluence
        templates['jira'] = DataTemplate(
            name="Jira Export",
            description="Export aus Jira/Confluence",
            source_system="Jira",
            column_mapping={
                'projekt_name': 'Summary',
                'kosten_plan': 'Story Points',
                'kosten_ist': 'Time Spent',
                'status': 'Status',
                'verantwortlich': 'Assignee',
                'prioritaet': 'Priority',
                'abteilung': 'Team'
            },
            expected_columns=[
                'Key', 'Summary', 'Status', 'Assignee'
            ],
            special_handling={
                'use_story_points': True,
                'convert_time_to_cost': True,
                'hourly_rate': 100
            },
            example_format="""
Key      | Summary    | Story Points | Time Spent | Status
PROJ-123 | CRM System | 89          | 120h       | In Progress
            """
        )
        
        # Template 4: Excel Standard (Zugbranche)
        templates['rail_standard'] = DataTemplate(
            name="Zugbranche Standard",
            description="Standard-Format für Bahnprojekte",
            source_system="Excel",
            column_mapping={
                'projekt_name': 'Projektbezeichnung',
                'kosten_plan': 'Budget',
                'kosten_ist': 'Kosten_Aktuell',
                'kosten_forecast': 'Hochrechnung',
                'termin_plan': 'Fertigstellung_Plan',
                'termin_ist': 'Fertigstellung_Ist',
                'status': 'Projektstatus',
                'verantwortlich': 'PM',
                'abteilung': 'Werk',
                'risiko': 'Risikostufe'
            },
            expected_columns=[
                'Projektbezeichnung', 'Budget', 'Kosten_Aktuell', 
                'Projektstatus', 'Werk'
            ],
            special_handling={
                'currency': 'EUR',
                'date_format': 'DD.MM.YYYY',
                'number_format': 'DE',
                'rail_specific': True
            },
            example_format="""
Projektbezeichnung | Budget      | Kosten_Aktuell | Projektstatus | Werk
ICE Modernisierung | 5.000.000,00| 5.250.000,00   | In Arbeit     | Hamburg
            """
        )
        
        # Template 5: Einfaches Excel
        templates['excel_simple'] = DataTemplate(
            name="Einfaches Excel",
            description="Einfaches Excel-Format ohne spezielle Anforderungen",
            source_system="Excel",
            column_mapping={
                'projekt_name': 'Projektname',
                'kosten_plan': 'Kosten_Plan',
                'kosten_ist': 'Kosten_Ist',
                'status': 'Status',
                'verantwortlich': 'Verantwortlich'
            },
            expected_columns=[
                'Projektname', 'Kosten_Plan', 'Kosten_Ist'
            ],
            special_handling={
                'flexible': True
            },
            example_format="""
Projektname | Kosten_Plan | Kosten_Ist | Status
CRM System  | 150000      | 165000     | Aktiv
            """
        )
        
        return templates
    
    def get_template(self, template_name: str) -> DataTemplate:
        """Gibt ein Template zurück"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[Dict[str, str]]:
        """Listet alle verfügbaren Templates"""
        return [
            {
                'key': key,
                'name': template.name,
                'description': template.description,
                'source_system': template.source_system
            }
            for key, template in self.templates.items()
        ]
    
    def get_template_mapping(self, template_name: str) -> Dict[str, str]:
        """Gibt das Column-Mapping eines Templates zurück"""
        template = self.get_template(template_name)
        return template.column_mapping if template else {}
    
    def add_custom_template(self, key: str, template: DataTemplate):
        """Fügt ein benutzerdefiniertes Template hinzu"""
        self.templates[key] = template
    
    def export_template(self, template_name: str) -> str:
        """Exportiert ein Template als JSON"""
        template = self.get_template(template_name)
        if template:
            return json.dumps(asdict(template), indent=2)
        return None
    
    def import_template(self, json_str: str) -> str:
        """Importiert ein Template aus JSON"""
        try:
            data = json.loads(json_str)
            template = DataTemplate(**data)
            key = data.get('source_system', 'custom').lower() + '_custom'
            self.add_custom_template(key, template)
            return key
        except Exception as e:
            raise ValueError(f"Fehler beim Importieren: {str(e)}")
    
    def suggest_template(self, columns: List[str]) -> str:
        """Schlägt ein passendes Template vor basierend auf Spalten"""
        max_match_score = 0
        best_template = 'excel_simple'
        
        for key, template in self.templates.items():
            score = 0
            # Zähle übereinstimmende Spalten
            for expected_col in template.expected_columns:
                if expected_col in columns:
                    score += 1
            
            # Normalisierte Score
            if len(template.expected_columns) > 0:
                normalized_score = score / len(template.expected_columns)
                if normalized_score > max_match_score:
                    max_match_score = normalized_score
                    best_template = key
        
        return best_template

if __name__ == "__main__":
    manager = TemplateManager()
    print("Template Manager geladen!")
    print(f"Verfügbare Templates: {len(manager.templates)}")
    for template in manager.list_templates():
        print(f"  - {template['name']} ({template['source_system']})")
