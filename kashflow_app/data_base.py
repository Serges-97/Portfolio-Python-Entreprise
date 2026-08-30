# =====================================================================
# MODULE DE STOCKAGE INDUSTRIEL : data_base.py (Version 5.0)
# =====================================================================
import sqlite3
import os

# On récupère le dossier où se trouve précisément ce fichier data_base.py
DOSSIER_ACTUEL = os.path.dirname(os.path.abspath(__file__))

# On soude le chemin pour que la base de données soit TOUJOURS dans le même dossier que le code
DB_NAME = os.path.join(DOSSIER_ACTUEL, "gestion_caisse.db")

def initialisation_systeme():
    """Crée les tables des ventes (avec IMEI et Synchro), du personnel et des stocks."""
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    
    # 1. TABLE DES VENTES AVANCÉE (Avec Sécurité IMEI et Suivi de Synchro Cloud)
    curseur.execute("""
    CREATE TABLE IF NOT EXISTS ventes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client TEXT NOT NULL,
        article TEXT NOT NULL,
        imei TEXT NOT NULL,
        montant_ht REAL NOT NULL,
        tva REAL NOT NULL,
        total_ttc REAL NOT NULL,
        synchro INTEGER DEFAULT 0, -- 0 = Uniquement sur le PC / 1 = Envoyé en direct au Patron
        date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. TABLE DU PERSONNEL (Inchangée)
    curseur.execute("""
    CREATE TABLE IF NOT EXISTS employes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        identifiant TEXT UNIQUE NOT NULL,
        mot_de_passe TEXT NOT NULL
    )
    """)
    curseur.execute("INSERT OR IGNORE INTO employes (identifiant, mot_de_passe) VALUES (?, ?)", ("gerant", "serge2026"))
    
    # 3. TABLE DE CONFIGURATION DU NOM DE LA BOUTIQUE (Inchangée)
    curseur.execute("""
    CREATE TABLE IF NOT EXISTS configuration (
        cle TEXT PRIMARY KEY,
        valeur TEXT NOT NULL
    )
    """)
    
    # 4. EXCLUSIVITÉ V5.0 : TABLE DE GESTION DES STOCKS DE TÉLÉPHONES
    curseur.execute("""
    CREATE TABLE IF NOT EXISTS stocks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        modele TEXT UNIQUE NOT NULL,
        quantite_dispo INTEGER NOT NULL,
        seuil_alerte INTEGER DEFAULT 2 -- Alerte le patron s'il reste moins de 2 smartphones
    )
    """)
    
    # Injection de quelques faux téléphones pour les simulations de vente de Serge
    curseur.execute("INSERT OR IGNORE INTO stocks (modele, quantite_dispo) VALUES (?, ?)", ("iPhone 15 Pro", 10))
    curseur.execute("INSERT OR IGNORE INTO stocks (modele, quantite_dispo) VALUES (?, ?)", ("Samsung A55", 15))
    curseur.execute("INSERT OR IGNORE INTO stocks (modele, quantite_dispo) VALUES (?, ?)", ("Tecno Camon 30", 5))

    connexion.commit()
    connexion.close()


# =====================================================================
# ZONE DE LOGIQUE : MOTEUR DES STOCKS (RASSURE LE PATRON)
# =====================================================================

def verifier_et_reduire_stock(modele_phone, qte_vendue):
    """Vérifie s'il y a assez de téléphones et réduit le stock en base SQL."""
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    
    # On regarde combien il reste de ce modèle
    curseur.execute("SELECT quantite_dispo, seuil_alerte FROM stocks WHERE modele = ?", (modele_phone,))
    resultat = curseur.fetchone()
    
    if resultat is None:
        connexion.close()
        return {"autorise": False, "raison": "Ce modèle de téléphone n'est pas répertorié en stock."}
        
    stock_actuel, seuil = resultat
    
    if stock_actuel < qte_vendue:
        connexion.close()
        return {"autorise": False, "raison": f"Stock insuffisant ! Il ne reste que {stock_actuel} appareils."}
        
    # Logique Série C : On soustrait la quantité vendue
    nouveau_stock = stock_actuel - qte_vendue
    curseur.execute("UPDATE stocks SET quantite_dispo = ? WHERE modele = ?", (nouveau_stock, modele_phone))
    
    # On vérifie si on a atteint la zone critique d'alerte rupture
    alerte_declenchee = nouveau_stock <= seuil
    
    connexion.commit()
    connexion.close()
    
    return {
        "autorise": True, 
        "restant": nouveau_stock, 
        "alerte_patron": alerte_declenchee
    }


# =====================================================================
# ZONE DE LOGIQUE : COMPTOIR DE VENTE & SYNCHRONISATION CLOUD
# =====================================================================

def enregistrer_vente_sql(client, article, imei, mnt_ht, tva, ttc):
    """Insère une vente avec sa sécurité IMEI. Retourne l'ID unique."""
    try:
        connexion = sqlite3.connect(DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("""
        INSERT INTO ventes (client, article, imei, montant_ht, tva, total_ttc, synchro)
        VALUES (?, ?, ?, ?, ?, ?, 0) -- '0' car la vente vient de naître localement sur le PC
        """, (client, article, imei, mnt_ht, tva, ttc))
        
        numero_facture = curseur.lastrowid
        connexion.commit()
        connexion.close()
        return numero_facture
    except Exception as e:
        print(f"[ERREUR SQL INSERER] : {e}")
        return None

def recuperer_ventes_non_synchro():
    """Extrait toutes les ventes qui ne sont pas encore sur l'ordinateur du patron."""
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    # On cible uniquement les lignes où synchro = 0
    curseur.execute("SELECT id, client, article, imei, montant_ht, tva, total_ttc FROM ventes WHERE synchro = 0")
    lignes = curseur.fetchall()
    connexion.close()
    return lignes

def marquer_comme_synchronisee(id_facture):
    """Passe le statut à 1 pour dire que le patron a bien reçu la donnée."""
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("UPDATE ventes SET synchro = 1 WHERE id = ?", (id_facture,))
    connexion.commit()
    connexion.close()


# =====================================================================
# ZONE DE LOGIQUE : SÉCURITÉ STANDARD (Inchangée)
# =====================================================================

def recuper_tout_les_ventes():
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT id, client, article, total_ttc, date_vente FROM ventes")
    lignes = curseur.fetchall()
    connexion.close()
    return lignes

def verifier_identifiants_sql(utilisateur, code_secret):
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT * FROM employes WHERE identifiant = ? AND mot_de_passe = ?", (utilisateur, code_secret))
    trouve = curseur.fetchone()
    connexion.close()
    return trouve is not None

def recuperer_nom_boutique_sql():
    connexion = sqlite3.connect(DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT valeur FROM configuration WHERE cle = 'nom_boutique'")
    ligne = curseur.fetchone()
    connexion.close()
    return ligne if ligne else None

def enregistrer_nom_boutique_sql(nom_magasin):
    try:
        connexion = sqlite3.connect(DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("INSERT OR REPLACE INTO configuration (cle, valeur) VALUES ('nom_boutique', ?)", (nom_magasin,))
        connexion.commit()
        connexion.close()
        return True
    except Exception:
        return False
