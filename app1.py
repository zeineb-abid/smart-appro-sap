import streamlit as st
import pandas as pd
import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Système Intégré Smart-Appro & SAP EWM",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BASE DE DONNÉES RÉELLES (Extraite de votre onglet DATA) ---
@st.cache_data
def charger_donnees_reelles():
    # Injection directe de vos références et descriptions pour garantir le fonctionnement en live
    donnees_usine = [
        {"Reference": "332011685", "Description": "YAR-PES FTF 1X320216 TM CHINE FONCE HYS", "Catégorie": "RM"},
        {"Reference": "332007206", "Description": "YAR-PES FTF 2X170/48 TM NOIR FIFTY", "Catégorie": "RM"},
        {"Reference": "332014278", "Description": "TWY-PES FTF1X320 TMR CHINE FON 100TS TTG", "Catégorie": "RM"},
        {"Reference": "332002171", "Description": "LAM-NILO NEGRO GRIS 1900MM 4MM", "Catégorie": "FG"},
        {"Reference": "331001767", "Description": "SILICON SERGE NOIR CAL TSC L2000", "Catégorie": "FG"},
        {"Reference": "331001927", "Description": "CURITIBA G282 MISTRAL HZD L1920", "Catégorie": "FG"},
        {"Reference": "331002436", "Description": "NILO GREY L1920", "Catégorie": "FG"},
        {"Reference": "331017466", "Description": "CURITIBA G345BITON BLANC SONIC HWL L1920", "Catégorie": "FG"},
        {"Reference": "332016319", "Description": "YAR-PES FTF 2X177/48 TM BISE ANTEX", "Catégorie": "RM"},
        {"Reference": "332016333", "Description": "TWS-PES FTF2X167chine1NOI/1SlatGray100/S", "Catégorie": "RM"},
        {"Reference": "300424160", "Description": "ENV EC CIRTF 30PES2150TR", "Catégorie": "RM"},
        {"Reference": "331021623", "Description": "ENV BL CIRTF 42PES 2050 TR", "Catégorie": "RM"},
        {"Reference": "350277049", "Description": "LAM-CLIP TITANCHWARZ 1MM VW216", "Catégorie": "FG"},
        {"Reference": "332014315", "Description": "WA-MELLOW 1 X 320 CHINE P231X26 HYS", "Catégorie": "RM"},
        {"Reference": "332014358", "Description": "TWY-PES FTF 3X177 ECRU RECY 150TS-TTG", "Catégorie": "RM"}
    ]
    
    df_clean = pd.DataFrame(donnees_usine)
    
    # Génération automatique des paramètres logistiques pour la démonstration
    df_clean['Adresse SAP'] = [f"EXT-A{i:02d}-R02-N03" for i in range(1, len(df_clean) + 1)]
    df_clean['Zone Physique'] = "Zone Extension"
    df_clean['Statut'] = "Disponible"
    df_clean['Dernier Scan'] = "Système (Initialisé)"
    df_clean['Urgence'] = "NORMAL"
    df_clean['Zone Emettrice'] = "Laminage"
    
    return df_clean

if 'historique_ot' not in st.session_state:
    st.session_state.historique_ot = charger_donnees_reelles()

# --- NAVIGATION DE L'APPLICATION ---
st.sidebar.title("🎮 Navigation Système")
page = st.sidebar.radio("Sélectionnez l'interface à afficher :", ["1. SMART-APPRO v4.0 (Opérateur)", "2. SAP EWM (Manager Dashboard)"])

# ==============================================================================
# INTERFACE 1 : SMART-APPRO V4.0 (STYLE OPÉRATEUR)
# ==============================================================================
if page == "1. SMART-APPRO v4.0 (Opérateur)":
    
    st.title("🚀 SMART-APPRO v4.0")
    st.write("### Flux automatique : Production ➡️ Entrepôt Extension")
    
    with st.form("form_appro"):
        # 1. ZONE ÉMETTRICE
        st.write("**1. ZONE ÉMETTRICE**")
        zone_emettrice = st.radio("Sélectionnez l'atelier demandeur", ["Laminage", "Tissage"], horizontal=True)
        
        # 2. SÉLECTION VISUELLE DE LA CATÉGORIE
        st.write("**2. FILTRAGE DU TYPE DE PRODUIT**")
        choix_icone = st.radio(
            "Sélectionnez le flux indicatif :",
            ["📦 RM (Raw Material / Matières Premières)", "✨ FG (Finished Goods / Produits Finis)"],
            horizontal=True
        )
        
        # 3. BARRE DE RECHERCHE DYNAMIQUE (VRAIES RÉFÉRENCES INTÉGRÉES)
        st.write("**3. 🔍 RÉFÉRENCE ARTICLE (INDEXÉ SAP)**")
        
        df_tous_articles = st.session_state.historique_ot.copy()
        df_tous_articles['Affichage'] = df_tous_articles['Reference'] + " | " + df_tous_articles['Description']
        liste_complete = list(df_tous_articles['Affichage'].dropna().unique())
        
        if len(liste_complete) > 0:
            option_choisie = st.selectbox(
                "👉 Commencez à écrire votre référence ou le nom de l'article :", 
                options=liste_complete,
                index=0,
                help="Saisie interactive : écrivez les premiers chiffres pour filtrer en temps réel."
            )
            
            ref_extraite = option_choisie.split(" | ")[0]
            desc_extraite = option_choisie.split(" | ")[1] if " | " in option_choisie else ""
            
            type_lignes = df_tous_articles[df_tous_articles['Reference'] == ref_extraite]['Catégorie'].values
            type_reel = type_lignes[0] if len(type_lignes) > 0 else "RM"
            st.caption(f"ℹ️ *Type détecté automatiquement dans la base de données : **{type_reel}***")
        else:
            st.warning("⚠️ Base de données vide.")
            ref_extraite, desc_extraite, type_reel = "---", "", "RM"
        
        # 4. QUANTITÉ DEMANDÉE
        st.write("**4. QUANTITÉ DEMANDÉE**")
        quantite = st.number_input("Quantité (Unités de Charge / Rouleaux / Palettes)", min_value=1, value=1)
        
        # 5. NIVEAU D'URGENCE DU FLUX
        st.write("**5. NIVEAU D'URGENCE DU FLUX**")
        urgence = st.radio("Niveau de priorité", ["NORMAL", "URGENT"], horizontal=True)
        
        # BOUTON DE VALIDATION DE L'ENVOI
        submit = st.form_submit_button("VALIDER L'ENVOI VERS SAP EWM")
        
        if submit and ref_extraite != "---":
            nouvel_ordre = {
                "Reference": ref_extraite,
                "Description": desc_extraite,
                "Adresse SAP": "EXT-A01-R" + str(datetime.datetime.now().second % 9 + 1) + "-N02", 
                "Zone Physique": "Extension Warehouse",
                "Statut": "Occupé (Demande reçue)",
                "Dernier Scan": f"Opérateur - {datetime.datetime.now().strftime('%H:%M')}",
                "Urgence": urgence,
                "Catégorie": type_reel,
                "Zone Emettrice": zone_emettrice
            }
            st.session_state.historique_ot = pd.concat([pd.DataFrame([nouvel_ordre]), st.session_state.historique_ot], ignore_index=True)
            st.success(f"✅ Ordre transféré ! {quantite} UDC demandée(s) par l'atelier **{zone_emettrice}** pour l'article **{ref_extraite}**.")

# ==============================================================================
# INTERFACE 2 : SAP EWM (DASHBOARD MANAGER)
# ==============================================================================
elif page == "2. SAP EWM (Manager Dashboard)":
    
    st.title("💻 Extended Warehouse Management (EWM)")
    st.write("### Pilotage Extension — Vue Supervision")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_lignes = len(st.session_state.historique_ot)
    urgents = len(st.session_state.historique_ot[st.session_state.historique_ot['Urgence'] == 'URGENT'])
    taux_service = max(0.0, 100.0 - (urgents * 2.5))
    
    with col1:
        st.metric(label="TAUX DE SERVICE INTERNE", value=f"{taux_service:.1f} %", delta="-2.5%" if urgents > 0 else "Stable")
    with col2:
        st.metric(label="TEMPS MOYEN DE PRÉPARATION", value="11.4 min", delta="Données Chronométrage")
    with col3:
        st.metric(label="LIGNES DE STOCK ENREGISTRÉES", value=f"{total_lignes}")
    with col4:
        total_refs = len(st.session_state.historique_ot['Reference'].unique())
        st.metric(label="RÉFÉRENCES TOTALES CHARGÉES", value=f"{total_refs}")
        
    st.write("---")
    
    col_gauche, col_droite = st.columns([2, 1])
    
    with col_gauche:
        st.write("#### 1. CARTOGRAPHIE NUMÉRIQUE & ADRESSAGE SAP (FLUX LIVE)")
        colonnes_affichage = ['Reference', 'Catégorie', 'Zone Emettrice', 'Adresse SAP', 'Zone Physique', 'Statut', 'Urgence', 'Dernier Scan']
        st.dataframe(st.session_state.historique_ot[colonnes_affichage], use_container_width=True)
        
    with col_droite:
        st.write("#### 2. ALERTES DE PRÉLÈVEMENT (MAGASINIERS)")
        for index, row in st.session_state.historique_ot.head(5).iterrows():
            if row['Urgence'] == "URGENT":
                st.error(f"🚨 **Urgence {row['Zone Emettrice']}**\n\nMouvement immédiat requis ({row['Catégorie']}) - Article : **{row['Reference']}**.")
            else:
                st.info(f"📦 **Flux Standard ({row['Zone Emettrice']})**\n\nOrdre normal pour l'article : **{row['Reference']}**.")
