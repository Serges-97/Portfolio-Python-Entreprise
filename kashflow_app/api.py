# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 1 SUR 10)
# =====================================================================
import sqlite3
import os
import secrets
import sys

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Sécurité d'arborescence pour serveur Linux
DOSSIER_DU_FICHIER = os.path.dirname(os.path.abspath(__file__))
if DOSSIER_DU_FICHIER not in sys.path:
    sys.path.insert(0, DOSSIER_DU_FICHIER)

import data_base

data_base.initialisation_systeme()

app = FastAPI(
    title="KashFlow Cloud v5.5",
    description="Moteur réseau et interface de supervision mobile du gérant."
)
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 2 SUR 10)
# =====================================================================

origines_autorisees = [
    origine.strip()
    for origine in os.environ.get("KASHFLOW_CORS_ORIGINS", "").split(",")
    if origine.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not origines_autorisees else origines_autorisees,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

class VenteSchemaReseau(BaseModel):
    reference_locale: str
    client: str
    article: str
    description_unique: str
    prix_ht: float
    quantite: int
    caissiere: str
    applique_tva: bool | None = None
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 3 SUR 10)
# =====================================================================

def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


# =====================================================================
# 📱 INTERFACE VISUELLE MAJESTUEUSE POUR LE TÉLÉPHONE DU PATRON
# =====================================================================
@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie une application web mobile sublime avec boutons tactiles et CDN stables."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Supervision - {nom_boutique}</title>
        <!-- Version universelle et FontAwesome pour smartphone -->
        <script src="https://jsdelivr.net"></script>
        <link rel="stylesheet" href="https://cloudflare.com">
    </head>
    <body class="bg-slate-100 font-sans text-slate-800 pb-12">
        
        <div class="bg-indigo-900 text-white text-center py-6 shadow-md sticky top-0 z-50">
            <h1 class="text-xl font-black tracking-wider"><i class="fa-solid fa-store text-emerald-400 mr-2"></i>{nom_boutique.upper()}</h1>
            <p class="text-xs text-indigo-200 mt-1">KashFlow Cloud Manager v5.5 • Espace Patron</p>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 4 SUR 10)
# =====================================================================

    html_content += """
        <div class="max-w-md mx-auto px-4 mt-6">
            <!-- Grille des boutons tactiles du smartphone -->
            <div class="grid grid-cols-2 gap-4" style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <button onclick="chargerStocks()" style="background: white; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; text-align: center; cursor: pointer;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📦</div>
                    <span class="text-xs font-bold text-slate-700">État des Stocks</span>
                </button>

                <button onclick="chargerStatistiques()" style="background: white; padding: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; text-align: center; cursor: pointer;">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📊</div>
                    <span class="text-xs font-bold text-slate-700">Chiffre d'Affaires</span>
                </button>
            </div>

            <!-- Bouton large pour voir tout le registre -->
            <button onclick="chargerToutHistorique()" style="width: 100%; background: white; padding: 1rem; margin-top: 1rem; border-radius: 0.75rem; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: space-between; cursor: pointer;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="font-size: 1.25rem;">📋</div>
                    <div style="text-align: left;">
                        <p style="margin: 0; font-size: 0.875rem; font-weight: bold; color: #1e293b;">Registre Général</p>
                        <p style="margin: 0; font-size: 0.75rem; color: #94a3b8;">Transactions de la boutique</p>
                    </div>
                </div>
                <span style="color: #cbd5e1; font-weight: bold;">&gt;</span>
            </button>

            <!-- ÉCRAN D'AFFICHAGE DYNAMIQUE -->
            <div id="zone-affichage" class="mt-6 bg-white rounded-2xl p-4 shadow-sm border border-slate-200 hidden" style="margin-top: 1.5rem; background: white; border-radius: 1rem; padding: 1rem; border: 1px solid #e2e8f0; display: none;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 0.75rem; margin-bottom: 1rem;">
                    <h3 id="titre-section" style="margin: 0; font-size: 0.875rem; font-weight: bold; color: #1e293b;">SECTION</h3>
                    <span onclick="fermerZone()" style="background: #f1f5f9; color: #64748b; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; cursor: pointer; font-weight: bold;">X</span>
                </div>
                <div id="contenu-section" class="overflow-x-auto text-xs"></div>
            </div>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 5 SUR 10)
# =====================================================================

    html_content += """
        <script>
            const API_KEY = localStorage.getItem('KASHFLOW_KEY') || "";
            
            if(!API_KEY) {
                const key = prompt("Sécurité d'accès d'usine\\n\\nVeuillez saisir la clé de sécurité API de votre boutique :");
                if(key) {
                    localStorage.setItem('KASHFLOW_KEY', key.trim());
                    window.location.reload();
                }
            }

            function fermerZone() {
                document.getElementById('zone-affichage').style.display = 'none';
            }

            async function chargerStocks() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📦 ÉTAT GLOBAL DE L'INVENTAIRE";
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Lecture du stock central...</p>";
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 6 SUR 10)
# =====================================================================

    html_content += """
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let html = "<table style='width:100%; text-align:left; border-collapse:collapse;'><thead><tr style='color:#94a3b8; font-size:0.75rem; border-bottom:1px solid #e2e8f0;'><th style='padding:0.5rem 0;'>Article</th><th style='text-align:center;'>Reste</th><th style='text-align:right;'>Statut</th></tr></thead><tbody>";
                    
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'color:#b91c1c; background:#fee2e2;' : 'color:#047857; background:#dcfce7;';
                        html += `<tr style='border-bottom:1px solid #f1f5f9;'>
                            <td style='padding:0.75rem 0; font-weight:bold; color:#334155;'>${i.article_modele}</td>
                            <td style='text-align:center; font-weight:900;'>${i.quantite_restante} pcs</td>
                            <td style='text-align:right;'><span style='padding:0.25rem 0.5rem; border-radius:9999px; font-size:0.70rem; font-weight:bold; ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table>";
                    el.innerHTML = html;
                } catch(e) {
                    el.innerHTML = "<p style='color:#ef4444; font-weight:bold; text-align:center;'>❌ Échec de liaison ou clé API incorrecte.</p>";
                }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 7 SUR 10)
# =====================================================================

    html_content += """
            async function chargerStatistiques() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📊 ANALYSE DU CHIFFRE D'AFFAIRES";
                document.getElementById('zone-affichage').style.display = 'block';
                
                let cible = prompt("Analyse financière du jour\\n\\nTapez la date cible au format J/M/AAAA (ex: 7/9/2026) :");
                if(!cible) return;

                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Calcul des performances...</p>";
                
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    el.innerHTML = `
                        <div style='background:#dcfce7; border:1px solid #bbf7d0; border-radius:0.75rem; padding:1rem; text-align:center; margin-bottom:1rem; color:#14532d;'>
                            <p style='margin:0; font-size:0.75rem; font-weight:bold; text-transform:uppercase;'>Chiffre d'Affaires du ${cible}</p>
                            <p style='margin:0.25rem 0 0 0; font-size:1.5rem; font-weight:900;'>${res.chiffre_affaires_ttc} <span style='font-size:0.875rem;'>FCFA</span></p>
                        </div>
                        <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:0.75rem; padding:0.75rem; font-size:0.75rem;'>
                            <p style='margin:0 0 0.5rem 0;'>🔥 <b>Article Star :</b> <span style='font-weight:bold; color:#1e3a8a;'>${res.article_le_plus_vendu}</span></p>
                            <p style='margin:0.5rem 0 0 0; padding-top:0.5rem; border-top:1px solid #e2e8f0; color:#475569; font-style:italic;'>📈 ${res.comparatif_performance_n_1}</p>
                        </div>
                    `;
                } catch(e) {
                    el.innerHTML = "<p style='color:#ef4444; font-weight:bold; text-align:center;'>❌ Échec du calcul comptable.</p>";
                }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 8 SUR 10)
# =====================================================================

    html_content += """
            async function chargerToutHistorique() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📋 TRANSACTIONS EN DIRECT";
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Chargement du registre...</p>";
                
                let caissiere = prompt("Entrez l'identifiant exact de la caissière à auditer :");
                if(!caissiere) return;

                try {
                    const r = await fetch(`/ventes/caissiere/${caissiere.trim().toLowerCase()}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    if(res.total_ventes_effectuees === 0) {
                        el.innerHTML = "<p style='text-align:center; padding:1rem; color:#94a3b8;'>Aucune opération enregistrée pour ce profil.</p>";
                        return;
                    }

                    let html = `<p style='font-weight:bold; color:#1e3a8a; margin-bottom:0.75rem;'>Total : ${res.total_ventes_effectuees} factures</p><div style='display:flex; flex-direction:column; gap:0.75rem;'>`;
                    
                    res.liste_ventes.forEach(v => {
                        html += `<div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:0.75rem; padding:0.75rem; display:flex; justify-content:space-between; align-items:center;'>
                            <div>
                                <div style='font-weight:bold; color:#1e293b;'>Facture #00${v.facture_no}</div>
                                <div style='font-size:0.65rem; color:#64748b;'>Client : ${v.client.toUpperCase()}</div>
                                <div style='font-size:0.60rem; color:#94a3b8; margin-top:0.25rem;'>🕒 ${v.date} à ${v.heure}</div>
                            </div>
                            <div style='text-align:right;'>
                                <div style='font-weight:900; color:#1d4ed8;'>${v.montant_ttc}</div>
                                <div style='font-size:0.65rem; color:#64748b;'>${v.article}</div>
                            </div>
                        </div>`;
                    });
                    html += "</div>";
                    el.innerHTML = html;
                } catch(e) {
                    el.innerHTML = "<p style='color:#ef4444; font-weight:bold; text-align:center;'>❌ Erreur d'accès aux transactions.</p>";
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 9 SUR 10)
# =====================================================================

@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """Intercepte, calcule la TVA et centralise la vente du magasin."""
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

        regime_tva = int(donnees.applique_tva) if donnees.applique_tva is not None else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
        
        num_facture = data_base.enregistrer_vente_sql(
            client=donnees.client, article=donnees.article, desc_unique=donnees.description_unique,
            mnt_ht=total_ht, tva=tva_calculee, ttc=total_ttc, caissiere=donnees.caissiere, reference_locale=donnees.reference_locale
        )
        if num_facture is None:
            raise HTTPException(status_code=500, detail="Échec d'écriture Cloud.")
            
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 10 SUR 10)
# =====================================================================

@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """Calcule le CA et le produit star de la période pour l'écran mobile."""
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {
            "chiffre_affaires_ttc": analyse["ca_total"],
            "article_le_plus_vendu": str(analyse["produit_phare"]).replace("{", "").replace("}", ""),
            "comparatif_performance_n_1": analyse["message_performance"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Extrait l'audit des ventes d'une vendeuse pour l'affichage mobile du patron."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes: 
            return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            liste_formatee.append({
                "facture_no": v[0], "client": v[1], "article": str(v[2]).replace("{", "").replace("}", ""),
                "montant_ttc": f"{v[3]} FCFA", "date": v[4], "heure": v[5]
            })
        return {"total_ventes_effectuees": len(liste_formatee), "liste_ventes": liste_formatee}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
    """Vérifie l'état d'inventaire et renvoie le statut avec seuil dynamique 10/5."""
    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT modele, quantite_dispo, ventes_cumulees FROM stocks")
        lignes = curseur.fetchall()
        
        curseur.execute("SELECT MAX(ventes_cumulees) FROM stocks")
        max_v_row = curseur.fetchone()
        max_v = max_v_row[0] if max_v_row and max_v_row[0] is not None else 0
        connexion.close()
        
        rapport_stock = []
        for l in lignes:
            seuil = 10 if l[2] == max_v else 5
            string_modele = str(l[0]).replace("{", "").replace("}", "")
            etat_alerte = "🚨 RUPTURE PROCHE" if l[1] <= seuil else "🟢 Stock Confortable"
            rapport_stock.append({
                "article_modele": string_modele,
                "quantite_restante": l[1],
                "ventes_totales": l[2],
                "seuil_alerte_applique": seuil,
                "statut_commande": etat_alerte
            })
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# =====================================================================
# 🕵️‍♂️ SÉCURITÉ GÉRANT : EXTRACTION DE LA LISTE DES EMPLOYÉS DU MAGASIN
# =====================================================================
@app.get("/employes/liste", dependencies=[Depends(verifier_cle_api)])
def api_liste_des_employes():
    """Extrait la liste unique des caissières enregistrées pour alimenter le smartphone du patron."""
    try:
        # Connexion directe à ton moteur de base de données d'origine
        liste_employes = data_base.recuperer_liste_tous_employes()
        
        # Si la base est neuve et qu'aucune caissière n'est créée, on met des profils de démo
        if not liste_employes:
            return {"employes": ["caissiere1", "caissiere2"]}
            
        # On renvoie la liste nettoyée en minuscules pour le JavaScript du téléphone
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
