# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - PARTIE 1 SUR 2)
# =====================================================================
import sqlite3
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import data_base

data_base.initialisation_systeme()

# Initialisation de la passerelle Cloud d'entreprise
app = FastAPI(
    title="KashFlow Cloud v5.5 - Espace Supervision Patron",
    description="Moteur réseau permettant au gérant de piloter son entreprise à distance."
)

origines_autorisees = [
    origine.strip()
    for origine in os.environ.get("KASHFLOW_CORS_ORIGINS", "").split(",")
    if origine.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Structure de contrôle stricte pour la validation des données réseau arrivant de la caisse
class VenteSchemaReseau(BaseModel):
    reference_locale: str
    client: str
    article: str
    description_unique: str  # IMEI, Numéro de Série, etc.
    prix_ht: float
    quantite: int
    caissiere: str
    applique_tva: bool | None = None


def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    """Refuse l'API tant qu'une clé serveur n'est pas configurée et présentée."""
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        raise HTTPException(status_code=503, detail="Clé API serveur non configurée.")
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/")
def verifier_connexion_cloud():
    """Route de diagnostic rapide pour vérifier si le serveur en ligne répond."""
    return {
        "statut": "Serveur Central en ligne (200 OK)",
        "application": "KashFlow Manager Backend v5.5",
        "auteur": "Ingénieur Serges"
    }


@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """
    Route distante appelée automatiquement en arrière-plan par l'ordinateur 
    de la caissière pour enregistrer une transaction dans le Cloud du patron.
    """
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")

        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute(
            "SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)
        ).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}

        # 1. Extraction du régime fiscal de la caissière enregistré en base de données
        regime_tva = (
            int(donnees.applique_tva)
            if donnees.applique_tva is not None
            else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        )
        
        # 2. Calcul financier de sécurité sur le serveur central
        total_ht = donnees.prix_ht * donnees.quantite
        
        if regime_tva == 1:
            tva_calculee = total_ht * (19.25 / 100) # Grande entreprise
        else:
            tva_calculee = 0.0 # Petite boutique informelle
            
        total_ttc = total_ht + tva_calculee
        
        # 3. Écriture immédiate dans le coffre-fort SQL
        num_facture = data_base.enregistrer_vente_sql(
            client=donnees.client,
            article=donnees.article,
            desc_unique=donnees.description_unique,
            mnt_ht=total_ht,
            tva=tva_calculee,
            ttc=total_ttc,
            caissiere=donnees.caissiere,
            reference_locale=donnees.reference_locale,
        )
        
        if num_facture is None:
            raise HTTPException(status_code=500, detail="Échec critique d'écriture sur le serveur central.")
            
        return {
            "statut": "Synchronisé",
            "facture_id_cloud": num_facture,
            "message": "Transaction répertoriée avec succès sur le terminal du patron."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - PARTIE 2 SUR 2)
# =====================================================================

# --- ROUTE N°4 : AUDIT FINANCIER ET STATISTIQUES COMPARATIVES ---
@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """
    Route analytique permettant au gérant d'obtenir le CA de la journée, 
    du mois ou de l'année, le produit star, et le comparatif de performance.
    - temporalite : 'JOUR', 'MOIS' ou 'ANNEE'
    - cible : 'JJ-MM' (pour jour), 'MM' (pour mois) ou 'AAAA' (pour année)
    """
    if temporalite not in ["JOUR", "MOIS", "ANNEE"]:
        raise HTTPException(status_code=400, detail="Temporalité invalide. Choisissez 'JOUR', 'MOIS' ou 'ANNEE'.")
        
    try:
        # Interrogation directe du moteur analytique de data_base.py
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {
            "statut": "Succes",
            "periode_analysee": temporalite,
            "valeur_cible": cible,
            "chiffre_affaires_ttc": analyse["ca_total"],
            "article_le_plus_vendu": analyse["produit_phare"],
            "comparatif_performance_n_1": analyse["message_performance"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTE N°5 : RAPPORT DE RENDEMENT PAR CAISSIÈRE ---
@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Permet au gérant de voir les ventes effectuées par une vendeuse spécifique."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes:
            return {
                "caissiere": nom_caissiere.upper(),
                "total_ventes_effectuees": 0,
                "liste_ventes": []
            }
            
        liste_formatee = []
        for v in ventes:
            liste_formatee.append({
                "facture_no": v[0],
                "client": v[1],
                "article": v[2],
                "montant_ttc": v[3],
                "date": v[4],
                "heure": v[5]
            })
            
        return {
            "caissiere": nom_caissiere.upper(),
            "total_ventes_effectuees": len(liste_formatee),
            "liste_ventes": liste_formatee
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTE N°6 : RAPPORT DE STOCK CRITIQUE EN TEMPS RÉEL ---
@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
    """Renvoie l'état global du stock de l'entreprise pour la supervision du patron."""
    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT modele, quantite_dispo, ventes_cumulees FROM stocks")
        lignes = curseur.fetchall()
        connexion.close()
        
        rapport_stock = []
        for l in lignes:
            # Règle : Si le produit est un top vente, seuil à 10, sinon 5
            curseur_max = sqlite3.connect(data_base.DB_NAME)
            c = curseur_max.cursor()
            c.execute("SELECT MAX(ventes_cumulees) FROM stocks")
            max_v = c.fetchone()[0] or 0
            curseur_max.close()
            
            seuil = 10 if l[2] == max_v else 5
            etat_alerte = "🚨 RUPTURE PROCHE / COMMANDE" if l[1] <= seuil else "🟢 Stock Confortable"
            
            rapport_stock.append({
                "article_modele": l[0],
                "quantite_restante": l[1],
                "ventes_totales": l[2],
                "seuil_alerte_applique": seuil,
                "statut_commande": etat_alerte
            })
            
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
