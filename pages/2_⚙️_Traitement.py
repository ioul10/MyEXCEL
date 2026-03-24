import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime

# Ajout du chemin src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.pdf_extractor import PDFExtractor
from src.excel_exporter import ExcelExporter

# Configuration page
st.set_page_config(
    page_title="Traitement - PDF to Excel",
    page_icon="⚙️",
    layout="wide"
)

# Création des dossiers
os.makedirs("uploads", exist_ok=True)
os.makedirs("downloads", exist_ok=True)

# Header
st.title("⚙️ Page de Traitement - PDF vers Excel")
st.markdown("---")

# Initialisation session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'extraction_patterns' not in st.session_state:
    st.session_state.extraction_patterns = {
        "Date": r'(\d{2}/\d{2}/\d{4})',
        "Numero_Facture": r'(FAC[-_]?\d{4}[-_]?\d{3,})',
        "Total": r'Total\s*[:=]\s*([\d\.\s]+)\s*[€EUR]',
        "Client": r'Client\s*[:=]\s*(.+?)(?:\n|$)',
        "Reference": r'(REF[-_]?\w{6,})'
    }

# Sidebar - Configuration
with st.sidebar:
    st.header("🔧 Configuration")
    
    st.subheader("📝 Patterns d'Extraction")
    st.caption("Expressions régulières pour extraire les données")
    
    # Éditeur de patterns
    new_patterns = {}
    for key, default_pattern in st.session_state.extraction_patterns.items():
        new_patterns[key] = st.text_input(
            f"{key}",
            value=default_pattern,
            help=f"Regex pour extraire {key}"
        )
    
    if st.button("💾 Sauvegarder Patterns", use_container_width=True):
        st.session_state.extraction_patterns = new_patterns
        st.success("Patterns sauvegardés !")
    
    st.markdown("---")
    
    st.subheader("ℹ️ Aide Regex")
    st.markdown("""
    - `\\d` = chiffre
    - `[A-Za-z]` = lettre
    - `+` = 1 ou plusieurs
    - `*` = 0 ou plusieurs
    - `?` = optionnel
    - `()` = groupe capturant
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Upload des PDF")
    
    uploaded_files = st.file_uploader(
        "Choisissez vos fichiers PDF",
        type=["pdf"],
        accept_multiple_files=True,
        help="Vous pouvez sélectionner plusieurs fichiers à la fois"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} fichier(s) sélectionné(s)")
        
        # Affichage des fichiers
        st.markdown("**Fichiers sélectionnés :**")
        for f in uploaded_files:
            st.caption(f"📄 {f.name} ({f.size / 1024:.1f} KB)")

with col2:
    st.subheader("⚡ Options de Traitement")
    
    extract_tables = st.checkbox("📊 Extraire les tableaux", value=False)
    extract_text = st.checkbox("📝 Extraire le texte complet", value=True)
    preview_mode = st.checkbox("👁️ Mode aperçu (premier PDF seulement)", value=False)
    
    process_button = st.button(
        "🚀 Lancer le Traitement",
        type="primary",
        use_container_width=True,
        disabled=not uploaded_files
    )

st.markdown("---")

# Zone de traitement
if process_button and uploaded_files:
    with st.spinner("🔄 Traitement en cours..."):
        
        # Sauvegarde temporaire des fichiers
        saved_paths = []
        for uploaded_file in uploaded_files:
            temp_path = os.path.join("uploads", uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            saved_paths.append(temp_path)
        
        # Extraction
        extractor = PDFExtractor()
        
        if preview_mode:
            saved_paths = saved_paths[:1]
            st.info("👁️ Mode aperçu activé - Seul le premier fichier sera traité")
        
        df_results = extractor.process_multiple_pdfs(
            saved_paths,
            st.session_state.extraction_patterns
        )
        
        st.session_state.processed_data = df_results
        
        # Nettoyage fichiers temporaires
        for path in saved_paths:
            os.remove(path)

# Affichage des résultats
if st.session_state.processed_data is not None:
    df = st.session_state.processed_data
    
    st.subheader("📊 Résultats de l'Extraction")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Fichiers Traités", len(df))
    with col2:
        st.metric("Succès", len(df[df["Statut"].str.contains("✅", na=False)]))
    with col3:
        st.metric("Échecs", len(df[df["Statut"].str.contains("❌", na=False)]))
    with col4:
        st.metric("Colonnes", len(df.columns))
    
    # Aperçu du DataFrame
    st.markdown("### Aperçu des Données")
    st.dataframe(df, use_container_width=True)
    
    # Export
    st.markdown("### 📥 Export Excel")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Export simple
        excel_buffer = ExcelExporter(df).get_download_buffer()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📊 Télécharger Excel (Simple)",
            data=excel_buffer,
            file_name=f"export_pdf_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # Export avec détails
        if st.checkbox("Inclure texte extrait", value=False):
            cols_to_export = [c for c in df.columns if c != "Texte_Extrait"]
            df_export = df[cols_to_export]
        else:
            df_export = df
        
        excel_buffer = ExcelExporter(df_export).get_download_buffer()
        
        st.download_button(
            label="📊 Télécharger Excel (Complet)",
            data=excel_buffer,
            file_name=f"export_complet_{timestamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Reset
    if st.button("🔄 Nouveau Traitement", use_container_width=True):
        st.session_state.processed_data = None
        st.rerun()

# Footer aide
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: gray;">
    <p>💡 <strong>Astuce :</strong> Personnalisez les patterns regex dans la sidebar pour adapter l'extraction à vos PDF</p>
</div>
""", unsafe_allow_html=True)
