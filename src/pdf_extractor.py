import pdfplumber
import re
from typing import Dict, List, Optional
import pandas as pd

class PDFExtractor:
    """Classe pour extraire des données spécifiques depuis des PDF"""
    
    def __init__(self):
        self.data = []
    
    def extract_text(self, pdf_path: str) -> str:
        """Extrait tout le texte d'un PDF"""
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    
    def extract_table(self, pdf_path: str, page_num: int = 0) -> List:
        """Extrait les tableaux d'une page spécifique"""
        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            if page_num < len(pdf.pages):
                tables = pdf.pages[page_num].extract_tables()
        return tables
    
    def extract_with_regex(self, text: str, patterns: Dict[str, str]) -> Dict[str, Optional[str]]:
        """Extrait des informations selon des regex personnalisées"""
        results = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            results[key] = match.group(1) if match else None
        return results
    
    def process_pdf(self, pdf_path: str, patterns: Dict[str, str] = None) -> Dict:
        """Traite un PDF et retourne un dictionnaire de données"""
        
        # Patterns par défaut (à personnaliser selon tes PDF)
        if patterns is None:
            patterns = {
                "Date": r'(\d{2}/\d{2}/\d{4})',
                "Numero_Facture": r'(FAC[-_]?\d{4}[-_]?\d{3,})',
                "Total": r'Total\s*[:=]\s*([\d\.\s]+)\s*[€EUR]',
                "Client": r'Client\s*[:=]\s*(.+?)(?:\n|$)',
                "Reference": r'(REF[-_]?\w{6,})'
            }
        
        result = {
            "Fichier": pdf_path.split("/")[-1],
            "Pages": 0,
            "Texte_Extrait": ""
        }
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                result["Pages"] = len(pdf.pages)
                texte_complet = ""
                
                for page in pdf.pages:
                    texte_complet += page.extract_text() or ""
                
                result["Texte_Extrait"] = texte_complet[:500]  # Aperçu
                
                # Extraction avec regex
                extracted = self.extract_with_regex(texte_complet, patterns)
                result.update(extracted)
                
                result["Statut"] = "✅ Succès"
                
        except Exception as e:
            result["Statut"] = f"❌ Erreur: {str(e)}"
        
        return result
    
    def process_multiple_pdfs(self, pdf_paths: List[str], patterns: Dict[str, str] = None) -> pd.DataFrame:
        """Traite plusieurs PDF et retourne un DataFrame"""
        results = []
        for path in pdf_paths:
            data = self.process_pdf(path, patterns)
            results.append(data)
        
        df = pd.DataFrame(results)
        
        # Réorganiser les colonnes
        cols_order = ["Fichier", "Statut", "Pages", "Date", "Numero_Facture", 
                      "Client", "Reference", "Total", "Texte_Extrait"]
        available_cols = [c for c in cols_order if c in df.columns]
        df = df[available_cols]
        
        return df
