import streamlit as st
import anthropic
import base64
import json
import io
import re
from excel_generator import generate_excel

st.set_page_config(
    page_title="PDF → Excel Financier",
    page_icon="📊",
    layout="wide"
)

# ── CSS styling ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a3a5c 0%, #2d6a9f 100%);
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 2.2rem; margin: 0; }
    .main-header p  { font-size: 1rem; opacity: .85; margin-top:.5rem; }

    .step-card {
        background: #f8fafd;
        border: 1px solid #d0e3f5;
        border-left: 4px solid #2d6a9f;
        border-radius: 8px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }
    .step-card h4 { color: #1a3a5c; margin: 0 0 .3rem 0; }

    .success-box {
        background: #e8f5e9;
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 1rem;
        color: #1b5e20;
    }
    .info-box {
        background: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 8px;
        padding: 1rem;
        color: #0d47a1;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📊 PDF → Excel Financier</h1>
    <p>Extraction intelligente par IA · Bilan · CPC · Tableau de financement</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Clé API Anthropic", type="password",
                            help="Obtenez votre clé sur console.anthropic.com")

    st.markdown("---")
    st.subheader("📋 Données à extraire")
    extract_bilan    = st.checkbox("Bilan Actif / Passif", value=True)
    extract_cpc      = st.checkbox("Compte de Produits et Charges", value=True)
    extract_ratios   = st.checkbox("Ratios financiers calculés", value=True)
    extract_tresorerie = st.checkbox("Trésorerie", value=True)

    st.markdown("---")
    st.markdown("""
    <div class='info-box'>
    <b>💡 Formats supportés</b><br>
    Bilans comptables marocains, états financiers OHADA, liasses fiscales IS, CPC modèle normal/simplifié.
    </div>
    """, unsafe_allow_html=True)

# ── Main area ─────────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📂 Import du PDF")
    uploaded_file = st.file_uploader(
        "Glissez votre fichier PDF ici",
        type=["pdf"],
        help="Bilan, CPC, liasse fiscale IS..."
    )

    if uploaded_file:
        st.markdown(f"""
        <div class='success-box'>
        ✅ <b>{uploaded_file.name}</b> chargé avec succès<br>
        Taille : {uploaded_file.size/1024:.1f} Ko
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        sections = []
        if extract_bilan:      sections.append("Bilan Actif & Passif")
        if extract_cpc:        sections.append("CPC (Produits & Charges)")
        if extract_ratios:     sections.append("Ratios financiers")
        if extract_tresorerie: sections.append("Trésorerie")

        st.markdown("**Sections sélectionnées :**")
        for s in sections:
            st.markdown(f"• {s}")

with col2:
    st.subheader("ℹ️ Guide d'utilisation")
    steps = [
        ("1️⃣", "Entrez votre clé API Anthropic dans la barre latérale"),
        ("2️⃣", "Choisissez les sections à extraire"),
        ("3️⃣", "Importez votre PDF financier"),
        ("4️⃣", "Cliquez sur « Extraire & Générer Excel »"),
        ("5️⃣", "Téléchargez votre fichier Excel coloré"),
    ]
    for icon, text in steps:
        st.markdown(f"""
        <div class='step-card'>
        <h4>{icon} {text}</h4>
        </div>
        """, unsafe_allow_html=True)

# ── Extract button ────────────────────────────────────────────────────────────
st.markdown("---")

if st.button("🚀 Extraire & Générer Excel", type="primary", use_container_width=True):
    if not api_key:
        st.error("❌ Veuillez entrer votre clé API Anthropic dans la barre latérale.")
    elif not uploaded_file:
        st.error("❌ Veuillez importer un fichier PDF.")
    else:
        sections_wanted = []
        if extract_bilan:       sections_wanted.append("bilan_actif_passif")
        if extract_cpc:         sections_wanted.append("cpc")
        if extract_ratios:      sections_wanted.append("ratios")
        if extract_tresorerie:  sections_wanted.append("tresorerie")

        # ── Step 1 : call Claude API ─────────────────────────────────────────
        with st.spinner("🤖 Analyse IA en cours..."):
            try:
                pdf_bytes  = uploaded_file.read()
                pdf_base64 = base64.standard_b64encode(pdf_bytes).decode("utf-8")

                prompt = f"""
Tu es un expert-comptable spécialisé en finances d'entreprise marocaines.
Analyse ce document PDF financier et extrais TOUTES les données des sections suivantes : {sections_wanted}.

Retourne UNIQUEMENT un objet JSON valide (sans markdown, sans backtick) structuré ainsi :

{{
  "entreprise": {{
    "raison_sociale": "...",
    "identifiant_fiscal": "...",
    "exercice": "...",
    "date_cloture": "..."
  }},
  "bilan_actif": [
    {{"poste": "...", "brut": 0, "amortissements": 0, "net_exercice": 0, "net_precedent": 0}}
  ],
  "bilan_passif": [
    {{"poste": "...", "exercice": 0, "precedent": 0}}
  ],
  "cpc": [
    {{"designation": "...", "exercice": 0, "precedent": 0}}
  ],
  "tresorerie": {{
    "actif_tresorerie": 0,
    "passif_tresorerie": 0,
    "tresorerie_nette": 0
  }},
  "ratios": [
    {{"ratio": "...", "formule": "...", "valeur": 0, "interpretation": "..."}}
  ]
}}

Calcule les ratios financiers clés :
- Ratio de liquidité générale = Actif circulant / Dettes CT
- Ratio d'autonomie financière = Capitaux propres / Total passif
- Ratio de rentabilité nette = Résultat net / Chiffre d'affaires
- Ratio d'endettement = Dettes totales / Capitaux propres
- Fonds de roulement = Capitaux permanents - Actif immobilisé
- BFR = Stocks + Créances - Dettes fournisseurs

Extrais UNIQUEMENT les sections demandées : {sections_wanted}
Si une section n'est pas demandée, mets un tableau vide [].
"""

                client   = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=4096,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_base64,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }],
                )

                raw = response.content[0].text.strip()
                # strip potential markdown fences
                raw = re.sub(r"^```[a-z]*\n?", "", raw)
                raw = re.sub(r"\n?```$", "", raw)
                data = json.loads(raw)

                st.success("✅ Extraction IA réussie !")

            except json.JSONDecodeError as e:
                st.error(f"❌ Erreur de parsing JSON : {e}")
                with st.expander("Réponse brute de l'IA"):
                    st.code(raw)
                st.stop()
            except Exception as e:
                st.error(f"❌ Erreur API : {e}")
                st.stop()

        # ── Step 2 : preview ─────────────────────────────────────────────────
        with st.expander("🔍 Aperçu des données extraites", expanded=False):
            info = data.get("entreprise", {})
            c1, c2, c3 = st.columns(3)
            c1.metric("Entreprise", info.get("raison_sociale", "—"))
            c2.metric("Exercice",   info.get("exercice", "—"))
            c3.metric("IF",         info.get("identifiant_fiscal", "—"))
            st.json(data)

        # ── Step 3 : generate Excel ───────────────────────────────────────────
        with st.spinner("📊 Génération du fichier Excel..."):
            try:
                excel_buffer = generate_excel(data, sections_wanted)
                fname = f"Bilan_{info.get('exercice','2017')}_{info.get('raison_sociale','Entreprise').replace(' ','_')[:30]}.xlsx"

                st.download_button(
                    label="📥 Télécharger le fichier Excel",
                    data=excel_buffer,
                    file_name=fname,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )
                st.markdown("""
                <div class='success-box'>
                🎉 <b>Excel généré avec succès !</b><br>
                Le fichier contient des feuilles colorées et formatées selon les standards comptables marocains.
                </div>
                """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Erreur génération Excel : {e}")
                st.exception(e)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:.85rem'>"
    "📊 PDF → Excel Financier · Propulsé par Claude AI (Anthropic)"
    "</div>",
    unsafe_allow_html=True
)
