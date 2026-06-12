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
# INTERFACE 1 : SMART-APPRO V4.0 (STYLE OPÉRATEUR)
# ==============================================================================
if page == "1. SMART-APPRO v4.0 (Opérateur)":
    
    st.title("🚀 SMART-APPRO v4.0")
    st.write("### Flux automatique : Production ➡️ Entrepôt Extension")
    
    with st.form("form_appro"):
        st.write("**1. ZONE ÉMETTRICE (FIXE)**")
        st.info("🏭 Section Laminage [🔒 BLOQUÉ]")
        
        st.write("**2. CATÉGORIE DE LA MATIÈRE PREMIÈRE**")
        categorie = st.radio("Sélection", ["Chimie (Fûts / IBC)", "Sèche (Rouleaux)"], horizontal=True)
        
        st.write("**3. RÉFÉRENCE ARTICLE (INDEXÉ SAP)**")
        ref_article = st.selectbox(
            "Référence", 
            ["CHM-042-GLUE | Colle forte industrielle (IBC 1000L)", "TEX-089-ROLL | Rouleau textile technique"]
        )
        
        st.write("**4. QUANTITÉ DEMANDÉE (UNITÉS DE CHARGE)**")
        quantite = st.number_input("Nombre d'UDC (Limite de sécurité fixée à 5 UDC max)", min_value=1, max_value=5, value=2)
        
        st.write("**5. NIVEAU D'URGENCE DU FLUX**")
        urgence = st.radio("Niveau", ["NORMAL", "URGENT"], horizontal=True)
        
        submit = st.form_submit_button("VALIDER L'ENVOI VERS SAP EWM")
        
        if submit:
            nouvel_ordre = {
                "Adresse SAP": "EXT-A01-R02-N04" if "Colle" in ref_article else "EXT-A02-R15-N05",
                "Zone Physique": "Extension (Allée 01, Niv 04)" if "Colle" in ref_article else "Extension (Allée 02, Niv 05)",
                "Statut": "Occupé (Palette validée)",
                "Dernier Scan": f"Opérateur - {datetime.datetime.now().strftime('%H:%M')}",
                "Urgence": urgence,
                "Catégorie": "Chimie" if "CHM" in ref_article else "Sèche"
            }
            st.session_state.historique_ot = pd.concat([pd.DataFrame([nouvel_ordre]), st.session_state.historique_ot], ignore_index=True)
            st.success(f"✅ Ordre transféré avec succès ! {quantite} UDC envoyées.")

# ==============================================================================
# INTERFACE 2 : SAP EWM (DASHBOARD MANAGER)
# ==============================================================================
elif page == "2. SAP EWM (Manager Dashboard)":
    
    st.title("💻 Extended Warehouse Management (EWM)")
    st.write("### Pilotage Extension — Vue Supervision")
    
    # --- SECTION DES 4 KPIS EN HAUT ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_ordres = len(st.session_state.historique_ot)
    urgents = len(st.session_state.historique_ot[st.session_state.historique_ot['Urgence'] == 'URGENT'])
    taux_service = max(0.0, 100.0 - (urgents * 1.5))
    
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
        st.write("#### 1. CARTOGRAPHIE NUMÉRIQUE & ADRESSAGE SAP (VUE LIVE AUTOCAD MAP)")
        st.dataframe(st.session_state.historique_ot, use_container_width=True)
        
    with col_droite:
        st.write("#### 2. STATUT DES ORDRES DE TRANSFERT (OT)")
        for index, row in st.session_state.historique_ot.iterrows():
            if row['Urgence'] == "URGENT":
                st.error(f"🚨 **Alimentation Production (JIT)**\n\nPrélèvement urgent requis à l'adresse {row['Adresse SAP']}.")
            else:
                st.info(f"📦 **Mouvement Entrant**\n\nOT standard vers {row['Adresse SAP']}.")
