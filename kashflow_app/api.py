# =====================================================================
# PASSERELLE CLOUD PATRON : api.py (Version 5.0 - Version Finale)
# =====================================================================
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import data_base

# Initialisation du serveur web de centralisation
app = FastAPI(
    title="KashFlow Cloud - Espace Patron",
    description="Passerelle réseau pour suivre la caisse de la boutique en temps réel."
)

# Structure obligatoire de validation pour recevoir une vente à distance
class VenteFormulaire(BaseModel):
    client: str
    article: str
    imei: str
    prix_ht: float
    quantite: int


# --- ROUTE N°1 : DIAGNOSTIC DE LIGNE ---
@app.get("/")
def verifier_api():
    """Permet au patron de vérifier sur son navigateur si le serveur est allumé."""
    return {"statut": "Serveur Patron en ligne", "projet": "KashFlow Manager V5.0"}


# --- ROUTE N°2 : RECEPTION DE VENTE DEPUIS LA BOUTIQUE ---
@app.post("/ventes/enregistrer")
def api_enregistrer_vente(donnees: VenteFormulaire):
    """Reçoit la vente envoyée par le réseau et l'inscrit dans la base centrale."""
    try:
        # Calcul automatique du TTC en direct pour le serveur du gérant
        prix_total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = prix_total_ht * (19.25 / 100)
        ttc = prix_total_ht + tva_calculee
        
        # Insertion sécurisée dans le coffre-fort SQL
        succes = data_base.enregistrer_vente_sql(
            donnees.client, donnees.article, donnees.imei, prix_total_ht, tva_calculee, ttc
        )
        if not succes:
            raise HTTPException(status_code=500, detail="Erreur d'écriture sur le stockage central.")
            
        return {"statut": "Succes", "message": "Vente synchronisee avec le cloud du patron."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTE N°3 : HISTORIQUE D'AUDIT SUR LE TÉLÉPHONE DU PATRON ---
@app.get("/ventes/historique")
def api_recuperer_historique():
    """Extrait toutes les lignes SQL et les envoie sur l'écran du smartphone."""
    ventes_sql = data_base.recuper_tout_les_ventes()
    
    # Sécurité : Si le magasin n'a encore rien vendu, on renvoie une structure vide propre
    if not ventes_sql:
        return {"chiffre_affaires_global_fcfa": 0.0, "ventes": []}
        
    liste_propres = []
    ca_total = 0.0
    
    # 🔑 LA BOUCLE LOGIQUE ALIGNÉE SUR LES INDEX DU FICHIER DATA_BASE.PY
    for ligne in ventes_sql:
        # Index 3 correspond exactement au montant total_ttc calculé en SQL
        ca_total += float(ligne[3]) 
        
        liste_propres.append({
            "facture_no": ligne[0],      # Index 0 = id
            "client": ligne[1],          # Index 1 = client
            "article": ligne[2],         # Index 2 = article
            "total_ttc_fcfa": float(ligne[3]), # Index 3 = total_ttc
            "date": ligne[4]             # Index 4 = date_vente
        })
        
    # On éjecte le bilan financier global formaté pour l'affichage mobile
    return {
        "chiffre_affaires_global_fcfa": round(ca_total, 2),
        "ventes": liste_propres
    } 
