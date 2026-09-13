# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 1 SUR 10)
# =====================================================================
import sqlite3
import os
import secrets
import sys
import json
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 🔑 SÉCURITÉ CONSTRUCTEUR : Forcer Render à cibler le bon dossier physique
DOSSIER_DU_FICHIER = os.path.dirname(os.path.abspath(__file__))
if DOSSIER_DU_FICHIER not in sys.path:
    sys.path.insert(0, DOSSIER_DU_FICHIER)

import data_base

# On s'assure que l'API pointe sur la MEME chaîne de base de données que l'application
data_base.initialisation_systeme()
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 2 SUR 10)
# =====================================================================

app = FastAPI(
    title="KashFlow Cloud v5.5",
    description="Moteur réseau et interface de supervision mobile du gérant."
)

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
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 3 SUR 10)
# =====================================================================

def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie l'application web mobile calquée au millimètre près sur les dessins de Serge."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    # 🎨 STYLE INTEGRALEMENT EMBARQUÉ ET VERIFIE POUR GOOGLE PIXEL
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nom_boutique}</title>
        <style>
            body {{ background-color: #cbd5e1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; display: flex; align-items: center; justify-content: center; min-height: 100vh; -webkit-font-smoothing: antialiased; }}
            .smartphone-container {{ width: 100%; max-width: 380px; background-color: #ffffff; border-radius: 32px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); padding: 25px 20px; min-height: 720px; position: relative; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; }}
            header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
            h1 {{ font-size: 22px; font-weight: 800; color: #334155; margin: 0; text-transform: lowercase; letter-spacing: -0.5px; }}
            .cloche-btn {{ background-color: #fef3c7; color: #d97706; border: none; padding: 10px 12px; border-radius: 9999px; font-size: 16px; cursor: pointer; position: relative; display: flex; align-items: center; justify-content: center; }}
            .badge-num {{ position: absolute; top: -6px; right: -6px; background-color: #dc2626; color: white; font-size: 10px; font-weight: 900; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); animation: pulse 2s infinite; }}
            .action-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }}
            .card-action {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px; display: flex; flex-direction: column; align-items: center; gap: 10px; cursor: pointer; transition: all 0.2s; text-align: center; }}
            .card-action:active {{ transform: scale(0.96); background-color: #f1f5f9; }}
            .card-action-title {{ font-size: 13px; font-weight: 700; color: #475569; }}
            .panel-registre {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 28px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center; }}
            .panel-registre h2 {{ font-size: 16px; font-weight: 800; color: #1e293b; margin: 6px 0 2px 0; }}
            .panel-registre p {{ font-size: 11px; color: #64748b; margin: 0; }}
            .section-caissieres h3 {{ font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }}
            .macarons-flex {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .macaron-btn {{ background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 9999px; padding: 8px 18px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; text-transform: capitalize; display: flex; align-items: center; gap: 6px; }}
            .macaron-btn:active {{ background-color: #1d4ed8; color: white; }}
            .modal-dossier {{ display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255,255,255,0.98); padding: 20px; border-radius: 32px; z-index: 50; flex-direction: column; overflow-y: auto; box-sizing: border-box; }}
            .modal-dossier.flex {{ display: flex !important; }}
            .bandeau-bleu {{ background-color: #1c355e; color: white; border-radius: 16px; padding: 14px; display: flex; align-items: center; gap: 12px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); text-align: left; }}
            .bandeau-title {{ font-size: 12px; font-weight: 900; text-transform: uppercase; line-height: 1.3; }}
            .tiroir-box {{ background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; border-radius: 12px; padding: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700; margin-bottom: 16px; box-sizing: border-box; }}
            .close-btn {{ background: none; border: none; color: #dc2626; font-size: 22px; cursor: pointer; padding: 0 5px; font-weight: bold; }}
            .card-facture-beige {{ background-color: #faf6f0; border: 1px solid #ebdccf; border-radius: 16px; margin-bottom: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
            .card-facture-header {{ background-color: #f8fafc; padding: 12px 16px; border-bottom: 1px solid #ebdccf; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 800; color: #1e293b; }}
            .card-facture-body {{ padding: 16px; text-align: left; }}
            .details-section {{ margin-bottom: 12px; }}
            .details-label {{ font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 2px; }}
            .details-val {{ font-size: 13px; color: #475569; font-weight: 600; }}
            .montant-flash {{ background-color: #f0fdf4; border: 1px dashed #bbf7d0; color: #166534; border-radius: 12px; padding: 12px; text-align: center; font-size: 20px; font-weight: 900; margin: 12px 0; }}
            .hidden {{ display: none !important; }}
            @keyframes pulse {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.08); }} }}
        </style>
    </head>
    <body>
        <div class="smartphone-container">
            <header>
                <h1>{nom_boutique.lower()}</h1>
                <button class="cloche-btn" onclick="ouvrirAlerteStocks()">
                    <div id="badge-cloche" class="hidden badge-num">0</div>
                    <span>🔔</span>
                </button>
            </header>
    """
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 4 SUR 10)
# =====================================================================

    html_content += """
            <!-- ACTIONS PRINCIPALES -->
            <div class="action-grid">
                <div class="card-action" onclick="chargerStocks()">
                    <span style="font-size: 24px;">📦</span>
                    <span class="card-action-title">État des Stocks</span>
                </div>
                <div class="card-action" onclick="chargerStatistiques()">
                    <span style="font-size: 24px;">📊</span>
                    <span class="card-action-title">Chiffre d'Affaires</span>
                </div>
            </div>

            <!-- PANNEAU CENTRAL REGISTRE -->
            <div class="panel-registre">
                <span style="font-size: 32px;">📋</span>
                <h2>Registre Général</h2>
                <p>Transactions de la boutique par caissière</p>
                <span style="font-size: 12px; color: #94a3b8; margin-top: 10px;">➔</span>
            </div>

            <!-- SECTION SÉLECTION CAISSIÈRES -->
            <div class="section-caissieres">
                <h3>Sélectionnez une caissière à auditer :</h3>
                <div id="liste-boutons-caissieres" class="macaron-flex"></div>
            </div>

            <!-- 📱 VERITABLE FENÊTRE POP-UP (MODALE PREMIUM CACHÉE) -->
            <div id="modal-facturation" class="modal-dossier">
                <!-- En-tête bleu nuit -->
                <div class="bandeau-bleu">
                    <span style="font-size: 20px;">📂</span>
                    <div class="bandeau-title">
                        DOSSIER FACTURES :<br>
                        <span id="nom-caissiere-titre" style="color: #34d399; font-size: 15px;">--</span>
                    </div>
                </div>

                <!-- Tiroir Caisse et Bouton de Fermeture Rouge -->
                <div class="tiroir-box">
                    <span id="compteur-factures-tiroir">Tiroir-Caisse : 0 facture(s)</span>
                    <button class="close-btn" onclick="fermerModal()">×</button>
                </div>

                <!-- Zone où s'empilent tes fiches factures beiges -->
                <div id="contenu-factures-modale" style="display: flex; flex-direction: column;"></div>
            </div>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 5 SUR 10)
# =====================================================================

    html_content += """
        <script>
            const API_KEY = localStorage.getItem('KASHFLOW_KEY') || "";
            let listeStocksGlobaux = [];
            
            if(!API_KEY) {
                const key = prompt("Sécurité d'accès d'usine\\n\\nVeuillez saisir la clé de sécurité API de votre boutique :");
                if(key) {
                    localStorage.setItem('KASHFLOW_KEY', key.trim());
                    window.location.reload();
                }
            }

            if(API_KEY) {
                verifierAlertesStocksEnArrierePlan();
                chargerProfilsCaissieresTactiles();
                setInterval(verifierAlertesStocksEnArrierePlan, 20000);
            }

            function fermerModal() {
                const modal = document.getElementById('modal-facturation');
                modal.classList.remove('flex');
            }

            // --- 🔔 SCRUTATION DE SÉCURITÉ DES STOCKS ---
            async function verifierAlertesStocksEnArrierePlan() {
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    listeStocksGlobaux = res.inventaire_magasin || [];
                    
                    const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                    const badge = document.getElementById('badge-cloche');
                    
                    if(articlesEnAlerte.length > 0) {
                        badge.innerText = articlesEnAlerte.length;
                        badge.classList.remove('hidden');
                    } else {
                        badge.classList.add('hidden');
                    }
                } catch(e) { console.error("Erreur cloche:", e); }
            }

            function ouvrirAlerteStocks() {
                const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "STOCKS CRITIQUES";
                document.getElementById('compteur-factures-tiroir').innerHTML = `<span>Alerte : ${articlesEnAlerte.length} produit(s)</span>`;
                modal.classList.add('flex');
                contenu.innerHTML = "";
                
                if(articlesEnAlerte.length === 0) {
                    contenu.innerHTML = "<div class='card-facture-beige' style='padding:20px; text-align:center; color:green; font-weight:bold;'>🟢 Aucun produit sous le seuil d'alerte.</div>";
                    return;
                }
                
                let html = "";
                articlesEnAlerte.forEach(i => {
                    html += `
                    <div class='card-facture-beige' style='padding:15px; display:flex; justify-content:space-between; align-items:center; font-weight:bold; color:#b91c1c;'>
                        <div>⚠️ ${i.article_modele.toUpperCase()}</div>
                        <div style='background:white; padding:4px 10px; border-radius:8px; border:1px solid #fecaca;'>Reste : ${i.quantite_restante} pcs</div>
                    </div>`;
                });
                contenu.innerHTML = html;
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 6 SUR 10)
# =====================================================================

    html_content += """
            // --- 📋 CHARGEMENT DES COMPTES DES CAISSIÈRES ---
            async function chargerProfilsCaissieresTactiles() {
                const conteneur = document.getElementById('liste-boutons-caissieres');
                try {
                    const r = await fetch('/employes/liste', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    conteneur.innerHTML = "";
                    res.employes.forEach(emp => {
                        const bouton = document.createElement('button');
                        bouton.className = "macaron-btn";
                        bouton.innerHTML = `<span style="font-size:12px;">👤</span> ${emp}`;
                        bouton.onclick = () => chargerHistoriqueCaissiereDirect(emp);
                        conteneur.appendChild(bouton);
                    });
                } catch(e) { conteneur.innerHTML = "<p style='color:red; font-size:12px;'>❌ Base de données injoignable.</p>"; }
            }

            // --- 📱 OUVERTURE INTERACTIVE DE TON DOSSIER FACTURES (MAQUETTE 2) ---
            async function chargerHistoriqueCaissiereDirect(caissiere) {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = caissiere.toUpperCase();
                modal.classList.add('flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-8'>Calcul des dossiers du tiroir...</p>";

                try {
                    const r = await fetch(`/ventes/caissiere/${encodeURIComponent(caissiere)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let cumulCA = 0;
                    res.liste_ventes.forEach(v => {
                        cumulCA += parseFloat(String(v.montant_ttc).replace(/[^0-9.]/g, '')) || 0;
                    });
                    
                    document.getElementById('compteur-factures-tiroir').innerHTML = `
                        <span>Tiroir-Caisse : ${res.total_ventes_effectuees} facture(s)</span>
                        <span style="background:white; padding:3px 10px; border-radius:8px; border:1px solid #bfdbfe; color:#1e40af; font-size:11px;">CA : ${cumulCA.toLocaleString()} FCFA</span>
                    `;
                    
                    if(!res.liste_ventes || res.liste_ventes.length === 0) {
                        contenu.innerHTML = `<div class='card-facture-beige' style='padding:20px; text-align:center; color:#94a3b8;'>Tiroir-Caisse vierge pour ${caissiere.toUpperCase()}.</div>`;
                        return;
                    }

                    let html = "";
                    // Dessin chirurgical au format exact de ton dessin beige
                    res.liste_ventes.forEach(v => {
                        html += `
                        <div class="card-facture-beige">
                            <div class="card-facture-header">
                                <span>Facture #00${v.facture_no}</span>
                                <span style="color:#94a3b8; font-size:12px;">⚙️</span>
                            </div>
                            <div class="card-facture-body">
                                <div class="details-section">
                                    <div class="details-label">Détails du Client</div>
                                    <div class="details-val">👤 Client : ${v.client.toUpperCase()}</div>
                                </div>
                                <div class="details-section" style="border-top:1px dashed #ebdccf; padding-top:8px; margin-top:8px;">
                                    <div class="details-label">Détails de la Transaction</div>
                                    <div class="details-val">🕒 ${v.date} à ${v.heure}</div>
                                </div>
                                <div class="montant-flash">
                                    ${v.montant_ttc}
                                </div>
                                <div class="details-section">
                                    <div class="details-label">Produit</div>
                                    <div class="details-val" style="font-size:14px; font-weight:800; color:#1e293b; text-transform:uppercase;">${v.article}</div>
                                </div>
                            </div>
                        </div>`;
                    });
                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p style='color:red; text-align:center; padding:10px;'>❌ Panne réseau d'audit.</p>"; }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 7 SUR 10)
# =====================================================================

    html_content += """
            async function chargerStocks() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "INVENTAIRE DES STOCKS";
                document.getElementById('compteur-factures-tiroir').innerText = "État Centralisé";
                modal.classList.add('flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-8'>Lecture du stock central...</p>";
                
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let html = "<div class='card-facture-beige' style='padding:15px; overflow-x:auto;'><table style='width:100%; text-align:left; font-size:12px; border-collapse:collapse;'><thead><tr style='color:#94a3b8; border-b:1px solid #f1f5f9; font-weight:bold;'><th style='pb:8px;'>Article</th><th style='text-align:center; pb:8px;'>Reste</th><th style='text-align:right; pb:8px;'>Statut</th></tr></thead><tbody>";
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'background:#fef2f2; color:#b91c1c; border-color:#fecaca;' : 'background:#f0fdf4; color:#166534; border-color:#bbf7d0';
                        html += `<tr style='border-bottom:1px solid #f8fafc;'>
                            <td style='py:10px; font-weight:bold; color:#334155; text-transform:uppercase;'>${i.article_modele}</td>
                            <td style='text-align:center; font-weight:900;'>${i.quantite_restante} pcs</td>
                            <td style='text-align:right;'><span style='padding:2px 8px; border-radius:9999px; border:1px solid; font-size:10px; font-weight:bold; ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table></div>";
                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p style='color:red; text-align:center;'>❌ Échec de synchronisation.</p>"; }
            }

            async function chargerStatistiques() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                let cible = prompt("Tapez la date au format J/M/AAAA (ex: 12/9/2026) :");
                if(!cible) return;
                
                document.getElementById('nom-caissiere-titre').innerText = "AUDIT COMPTABLE";
                document.getElementById('compteur-factures-tiroir').innerText = `Date : ${cible}`;
                modal.classList.add('flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-8'>Calcul des balances financières...</p>";
                
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    contenu.innerHTML = `
                        <div style='display:flex; flex-direction:column; gap:15px;'>
                            <div class='card-facture-beige' style='background:#f0fdf4; border-color:#bbf7d0; padding:20px; text-align:center; color:#166534;'>
                                <p style='margin:0; font-size:10px; font-weight:bold; color:#15803d; text-transform:uppercase; letter-spacing:0.5px;'>Chiffre d'Affaires du ${cible}</p>
                                <p style='margin:5px 0 0 0; font-size:24px; font-weight:900;'>${res.chiffre_affaires_ttc} FCFA</p>
                            </div>
                            <div class='card-facture-beige' style='padding:15px; font-size:12px; color:#475569;'>
                                <p style='margin:0 0 8px 0;'>🔥 <b>Article Star :</b> <span style='color:#1e293b; font-weight:800; text-transform:uppercase;'>${res.article_le_plus_vendu}</span></p>
                                <p style='margin:0; border-top:1px solid #ebdccf; padding-top:8px; font-style:italic; color:#94a3b8;'>📈 ${res.comparatif_performance_n_1}</p>
                            </div>
                        </div>`;
                } catch(e) { contenu.innerHTML = "<p style='color:red; text-align:center;'>❌ Impossible de générer la statistique.</p>"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 8 SUR 10)
# =====================================================================


@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """Intercepte, calcule la TVA et centralise la vente du magasin."""
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(
                status_code=422, detail="Prix ou quantité invalide."
            )
        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute(
            "SELECT id FROM ventes WHERE reference_locale = ?",
            (donnees.reference_locale,),
        ).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}
        regime_tva = (
            int(donnees.applique_tva)
            if donnees.applique_tva is not None
            else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        )
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
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
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """Calcule le CA et le produit star de la période pour l'écran mobile."""
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {
            "chiffre_affaires_ttc": analyse["ca_total"],
            "article_le_plus_vendu": str(analyse["produit_phare"])
            .replace("{", "")
            .replace("}", ""),
            "comparatif_performance_n_1": analyse["message_performance"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 9 SUR 10)
# =====================================================================


@app.get(
    "/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)]
)
def api_historique_caissiere(nom_caissiere: str):
    """Extrait l'audit des ventes d'une vendeuse pour l'affichage mobile du patron."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes:
            return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            # 🟢 DÉPAQUETAGE DES TUPLES SQLITE D'ORIGINE
            liste_formatee.append(
                {
                    "facture_no": v[0],
                    "client": v[1],
                    "article": str(v[2]).replace("{", "").replace("}", ""),
                    "montant_ttc": f"{v[3]:,.0f} FCFA",
                    "date": v[4],
                    "heure": v[5],
                }
            )
        return {
            "total_ventes_effectuees": len(liste_formatee),
            "liste_ventes": liste_formatee,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
    """Vérifie l'état d'inventaire et renvoie le statut avec seuil dynamique 10/5."""
    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute(
            "SELECT modele, quantite_dispo, ventes_cumulees FROM stocks"
        )
        lignes = curseur.fetchall()
        curseur.execute("SELECT MAX(ventes_cumulees) FROM stocks")
        max_v_row = curseur.fetchone()
        max_v = max_v_row[0] if max_v_row and max_v_row[0] is not None else 0
        connexion.close()

        rapport_stock = []
        for l in lignes:
            seuil = 10 if l[2] == max_v else 5
            string_modele = str(l[0]).replace("{", "").replace("}", "")
            etat_alerte = (
                "🚨 RUPTURE PROCHE" if l[1] <= seuil else "🟢 Stock Confortable"
            )
            # 🟢 DÉPAQUETAGE DES TUPLES SQLITE D'ORIGINE
            rapport_stock.append(
                {
                    "article_modele": string_modele,
                    "quantite_restante": l[1],
                    "ventes_totales": l[2],
                    "seuil_alerte_applique": seuil,
                    "statut_commande": etat_alerte,
                }
            )
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version Unifiée Pixel - ÉTAPE 10 SUR 10)
# =====================================================================


@app.get("/employes/liste", dependencies=[Depends(verifier_cle_api)])
def api_liste_des_employes():
    """Extrait la liste unique des caissières enregistrées pour alimenter le smartphone du patron."""
    try:
        liste_employes = data_base.recuperer_liste_tous_employes()
        if not liste_employes:
            return {"employes": ["caissiere1", "caissiere2"]}
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
