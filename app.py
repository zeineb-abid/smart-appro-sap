import streamlit as pd
import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Système Intégré Smart-Appro & SAP EWM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SIMULATION DE LA BASE DE DONNÉES (DATA) ---
# On initialise un historique des ordres de transfert dans la mémoire de l'application
if 'historique_ot' not in st.session_state:
    st.session_state.historique_ot = pd.DataFrame([
        {
            "Adresse SAP": "EXT-A01-R02-N01", 
            "Zone Physique": "Extension (Allée 01, Niv 01)", 
            "Statut": "Occupé (Palette validée)", 
            "Dernier Scan": "Cariste #04 - 09:52",
            "Urgence": "NORMAL",
            "Catégorie": "Chimie"
        },
        {
            "Adresse SAP": "EXT-A02-R15-N03", 
            "Zone Physique": "Extension (Allée 02, Niv 03)", 
            "Statut": "Vide (Disponible)", 
            "Dernier Scan": "Système (Calcul auto)",
            "Urgence": "NORMAL",
            "Catégorie": "Sèche"
        },
        {
            "Adresse SAP": "BAT-A01-R05-N02", 
            "Zone Physique": "Bâtiment A (Allée 01, Niv 02)", 
            "Statut": "Occupé (Palette validée)", 
            "Dernier Scan": "Cariste #12 - 09:41",
            "Urgence": "URGENT",
            "Catégorie": "Chimie"
        }
    ])

# --- NAVIGATION ENTRE LES DEUX INTERFACES ---
st.sidebar.title("🎮 Navigation Système")
page = st.sidebar.radio("Sélectionnez l'interface à afficher :", ["1. SMART-APPRO v4.0 (Opérateur)", "2. SAP EWM (Manager Dashboard)"])

# ==============================================================================
# INTERFACE 1 : SMART-APPRO V4.0 (STYLE DESIGN SOMBRE)
# ==============================================================================
if page == "1. SMART-APPRO v4.0 (Opérateur)":
    
    # Styles CSS pour appliquer le thème bleu/sombre de votre maquette
    st.markdown("""
        <style>
        .stApp { background-color: #111d33; color: white; }
        .block-container { padding-top: 2rem; }
        div[data-testid="stForm"] { background-color: #172641; border: 1px solid #243b66; border-radius: 10px; }
        h1, h2, h3, label { color: #ffffff !important; }
        </style>
    """, unsafe_allowed_html=True)
    
    st.title("🚀 SMART-APPRO v4.0")
    st.caption("Flux automatique : Production ➡️ Entrepôt Extension | Connecté")
    
    with st.form("form_appro"):
        st.write("### 1. ZONE ÉMETTRICE (FIXE)")
        st.info("🏭 Section Laminage [🔒 BLOQUÉ]")
        
        st.write("### 2. CATÉGORIE DE LA MATIÈRE PREMIÈRE")
        categorie = st.radio("Sélection", ["Chimie (Fûts / IBC)", "Sèche (Rouleaux)"], horizontal=True)
        
        st.write("### 3. RÉFÉRENCE ARTICLE (INDEXÉ SAP)")
        ref_article = st.selectbox(
            "Référence", 
            ["CHM-042-GLUE | Colle forte industrielle (IBC 1000L)", "TEX-089-ROLL | Rouleau textile technique"]
        )
        
        st.write("### 4. QUANTITÉ DEMANDÉE (UNITÉS DE CHARGE)")
        quantite = st.number_input("Nombre d'UDC (Limite de sécurité fixée à 5 UDC max)", min_value=1, max_value=5, value=2)
        
        st.write("### 5. NIVEAU D'URGENCE DU FLUX")
        urgence = st.radio("Niveau", ["NORMAL", "URGENT"], horizontal=True)
        
        submit = st.form_submit_button("VALIDER L'ENVOI VERS SAP EWM")
        
        if submit:
            # Action lors du clic : On génère une nouvelle ligne dans la table DATA partagée
            nouvel_ordre = {
                "Adresse SAP": "EXT-A01-R02-N04" if "Colle" in ref_article else "EXT-A02-R15-N05",
                "Zone Physique": "Extension (Allée 01, Niv 04)" if "Colle" in ref_article else "Extension (Allée 02, Niv 05)",
                "Statut": "Occupé (Palette validée)",
                "Dernier Scan": f"Opérateur - {datetime.datetime.now().strftime('%H:%M')}",
                "Urgence": urgence,
                "Catégorie": "Chimie" if "CHM" in ref_article else "Sèche"
            }
            # Enregistrement dans notre DataFrame global
            st.session_state.historique_ot = pd.concat([pd.DataFrame([nouvel_ordre]), st.session_state.historique_ot], ignore_index=True)
            st.success(f"✅ Ordre transféré ! {quantite} UDC de l'article spécifié ont été envoyées vers SAP.")

# ==============================================================================
# INTERFACE 2 : SAP EWM (STYLE DESIGN CLAIR MANAGER)
# ==============================================================================
elif page == "2. SAP EWM (Manager Dashboard)":
    
    # Rétablir un style clair professionnel pour le manager
    st.markdown("""
        <style>
        .stApp { background-color: #f8f9fa; color: #333333; }
        </style>
    """, unsafe_allowed_html=True)
    
    st.title("💻 Extended Warehouse Management (EWM) - Pilotage Extension")
    st.caption("Système : PRD_DB01 | LOGS : TEMPS RÉEL")
    
    # --- SECTION DES 4 KPIS EN HAUT ---
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcul dynamique du taux de service en fonction des urgences actuelles
    total_ordres = len(st.session_state.historique_ot)
    urgents = len(st.session_state.historique_ot[st.session_state.historique_ot['Urgence'] == 'URGENT'])
    taux_service = 100.0 - (urgents * 1.5) # Plus il y a d'urgences non traitées, plus il baisse
    
    with col1:
        st.metric(label="TAUX DE SERVICE INTERNE", value=f"{taux_service:.1f} %", delta="+1.2% vs mois dernier")
    with col2:
        st.metric(label="TEMPS MOYEN DE PRÉPARATION", value="11.4 min", delta="-2.1 min (Cible < 15 min)", delta_color="inverse")
    with col3:
        st.metric(label="OPTIMISATION ABC (RACKS)", value="94.5 %", delta="Classe A placé proche quais")
    with col4:
        st.metric(label="PRÉCISION INVENTAIRE PERMANENT", value="99.91 %", delta="Mise à jour par Scans")
        
    st.write("---")
    
    # --- SECTION BASSE : CARTOGRAPHIE ET ORDRES ---
    col_gauche, col_droite = st.columns([2, 1])
    
    with col_gauche:
        st.write("### 1. CARTOGRAPHIE NUMÉRIQUE & ADRESSAGE SAP (VUE LIVE AUTOCAD MAP)")
        st.caption("Chaque adresse correspond à un emplacement physique strict codé sous la forme : [Bâtiment]-[Allée]-[Rangée]-[Niveau]")
        
        # Affichage du tableau de données dynamique issu de l'autre application
        st.dataframe(st.session_state.historique_ot, use_container_width=True)
        
    with col_droite:
        st.write("### 2. STATUT DES ORDRES DE TRANSFERT (OT)")
        
        # Affichage dynamique des alertes
        for index, row in st.session_state.historique_ot.iterrows():
            if row['Urgence'] == "URGENT":
                st.error(f"🚨 **Alimentation Production (JIT)**\n\nPrélèvement urgent requis pour la Ligne Laminage (Catégorie : {row['Catégorie']}).")
            else:
                st.info(f"📦 **Mouvement Entrant**\n\nScan BL Réception ⇒ Création OT vers {row['Adresse SAP']}.")
