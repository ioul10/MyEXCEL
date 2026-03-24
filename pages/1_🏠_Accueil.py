import streamlit as st

# Configuration page
st.set_page_config(
    page_title="Accueil - PDF to Excel",
    page_icon="🏠",
    layout="wide"
)

# Header
st.title("🏠 Accueil - Convertisseur PDF vers Excel")
st.markdown("---")

# Introduction
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### 📋 Bienvenue sur l'Application d'Automatisation PDF
    
    Cette application vous permet de **convertir automatiquement** vos fichiers PDF 
    en tableaux Excel bien organisés, en extrayant uniquement les informations dont vous avez besoin.
    
    #### ✨ Fonctionnalités Principales
    
    - 📤 **Upload multiple** de fichiers PDF
    - 🔍 **Extraction intelligente** avec expressions régulières
    - 📊 **Export Excel** avec mise en forme professionnelle
    - 🔒 **Traitement local** (vos données ne quittent pas le serveur)
    - ⚡ **Rapide et automatisé**
    
    #### 🎯 Cas d'Usage
    
    | Type de Document | Informations Extractibles |
    |-------------------|--------------------------|
    | Factures | Date, Numéro, Total, Client |
    | Bons de Commande | Référence, Quantité, Prix |
    | Relevés Bancaires | Date, Montant, Libellé |
    | Rapports | Titres, Valeurs, Statistiques |
    """)

with col2:
    st.image("https://cdn-icons-png.flaticon.com/512/337/337946.png", width=200)
    st.info("""
    **💡 Conseil**
    
    Pour de meilleurs résultats, assurez-vous que vos PDF contiennent du texte sélectionnable (non scanné).
    """)

st.markdown("---")

# Comment ça marche
st.subheader("🔄 Comment Ça Marche ?")

steps = {
    "1️⃣ Upload": "Téléchargez vos fichiers PDF dans l'application",
    "2️⃣ Configuration": "Définissez les informations à extraire (regex personnalisables)",
    "3️⃣ Traitement": "L'application analyse chaque PDF automatiquement",
    "4️⃣ Export": "Téléchargez le fichier Excel avec toutes les données organisées"
}

cols = st.columns(4)
for i, (step, desc) in enumerate(steps.items()):
    with cols[i]:
        st.markdown(f"**{step}**")
        st.caption(desc)

st.markdown("---")

# Technologies
st.subheader("🛠 Technologies Utilisées")

tech_cols = st.columns(4)
technologies = [
    {"name": "Streamlit", "icon": "📊", "desc": "Interface web interactive"},
    {"name": "Python", "icon": "🐍", "desc": "Langage de programmation"},
    {"name": "pdfplumber", "icon": "📄", "desc": "Extraction PDF précise"},
    {"name": "Pandas", "icon": "📈", "desc": "Manipulation de données"}
]

for i, tech in enumerate(technologies):
    with tech_cols[i]:
        st.markdown(f"### {tech['icon']} {tech['name']}")
        st.caption(tech['desc'])

st.markdown("---")

# Call to Action
st.markdown("""
<div style="text-align: center; margin-top: 30px;">
    <h3>🚀 Prêt à commencer ?</h3>
    <p>Rendez-vous sur la page de traitement pour uploader vos PDF !</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.link_button("➡️ Aller au Traitement", "/Traitement")

# Footer
st.markdown("---")
st.caption("© 2024 - Application PDF to Excel | Développé avec Streamlit")
