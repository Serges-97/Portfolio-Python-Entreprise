import sqlite3

# on defini une constante global ,  c'est le nom du fichier qui vas contenire tout nos transactions
la_caisse = "gestion_caise.db"

# || initialisation de la base (lancement de l'usine ) ||
def initialisation_systeme():
    
    # Connexion à la base de données (elle sera créée si elle n'existe pas)
    connexion = sqlite3.connect(la_caisse)
    curseur = connexion.cursor()

    """on vas stocker l'id"""
    curseur.execute("""
    CREATE TABLE IF NOT EXISTS ventes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_client TEXT NOT NULL,
        nom_article TEXT NOT NULL ,
        montant_ht REAL NOT NULL,
        tva REAL NOT NULL ,
        total_ttc REAL NOT NULL,
        date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP      
    )
    """)

    connexion.commit()
    connexion.close()

def enregistrer_vente_sql(nom_client , nom_article , montant_ht , tva , total_ttc ) :
    try :
        connexion = sqlite3.connect(la_caisse)
        curseur = connexion.cursor()

        """requete d'insertion ,  les ?? sont indispenssable en entreprise pour eviter les piratages par injection"""
        curseur.execute("""
        INSERT INTO ventes (nom_client , nom_article , montant_ht , tva , total_ttc )
        VALUES (?,?,?,?,?)
         """, ( nom_client , nom_article , montant_ht , tva , total_ttc )) 
        connexion.commit()
        connexion.close()

        return True
    except Exception as e:
        print(f"[ERREUR SQL] impossible d'enregistrer la transaction:{e} ")
        return False

""" la fonction qui recupere toutes les ventes , ce qui """
def recuper_tout_les_ventes():
    # on recuper tout l'historique des ventes 
    connexion = sqlite3.connect(la_caisse)
    curseur = connexion.cursor()

    curseur.execute("SELECT id, nom_client , nom_article , montant_ht , tva , total_ttc  FROM ventes")
    # on ramene tous les lignes extraits sous forme de liste de lifne (tuples) pour python
    lignes = curseur.fetchall()
    connexion.close()

    # on renvoie cette liste sompleteau programme principal pour l'afficharge.
    return lignes


    