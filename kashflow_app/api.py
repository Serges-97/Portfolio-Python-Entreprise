# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 1 SUR 7)
# =====================================================================
import sqlite3
import os
import secrets
import sys

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

app = FastAPI(
    title="KashFlow Cloud v5.5",
    description="Moteur réseau et interface de supervision mobile du gérant."
)
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 2 SUR 7)
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
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 3 SUR 7)
# =====================================================================

def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie l'application mobile avec du style CSS pur embarqué, garanti sans bug sur Google Pixel."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nom_boutique}</title>
        <!-- 🟢 CORRECTIF GOOGLE PIXEL : Plus besoin de CDN internet pour dessiner tes maquettes ! -->
        <style>
            body {{ background-color: #cbd5e1; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; margin: 0; padding: 20px; display: flex; flex-col: column; align-items: center; justify-content: center; min-height: 100vh; }}
            .smartphone-container {{ width: 100%; max-width: 380px; background-color: #ffffff; border-radius: 32px; box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); padding: 25px 20px; min-height: 720px; position: relative; box-sizing: border-box; display: flex; flex-direction: column; overflow: hidden; }}
            header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }}
            h1 {{ font-size: 22px; font-weight: 800; color: #334155; margin: 0; text-transform: uppercase; letter-spacing: 0.5px; }}
            .cloche-btn {{ background-color: #fef3c7; color: #d97706; border: none; padding: 10px 12px; border-radius: 9999px; font-size: 16px; cursor: pointer; position: relative; }}
            .badge-num {{ position: absolute; top: -6px; right: -6px; background-color: #dc2626; color: white; font-size: 10px; font-weight: 900; width: 18px; height: 18px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
            .action-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 24px; }}
            .card-action {{ background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 16px; display: flex; flex-direction: column; align-items: center; gap: 10px; cursor: pointer; transition: all 0.2s; text-align: center; }}
            .card-action:active {{ transform: scale(0.96); background-color: #f1f5f9; }}
            .card-action-title {{ font-size: 13px; font-weight: 700; color: #475569; }}
            .panel-registre {{ background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 28px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); display: flex; flex-direction: column; align-items: center; }}
            .panel-registre h2 {{ font-size: 16px; font-weight: 800; color: #1e293b; margin: 6px 0 2px 0; }}
            .panel-registre p {{ font-size: 11px; color: #64748b; margin: 0; }}
            .section-caissieres h3 {{ font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px; letter-spacing: 0.5px; }}
            .macarons-flex {{ display: flex; flex-wrap: wrap; gap: 10px; }}
            .macaron-btn {{ background-color: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; border-radius: 9999px; padding: 8px 18px; font-size: 13px; font-weight: 700; cursor: pointer; transition: all 0.2s; text-transform: capitalize; }}
            .macaron-btn:active {{ background-color: #1d4ed8; color: white; }}
            
            /* Fenêtre Modale Maquette 2 */
            .modal-dossier {{ display: none; position: absolute; top: 0; left: 0; right: 0; bottom: 0; background-color: rgba(255,255,255,0.98); padding: 20px; border-radius: 32px; z-index: 50; flex-direction: column; overflow-y: auto; box-sizing: border-box; }}
            .modal-dossier.flex {{ display: flex !important; }}
            .bandeau-bleu {{ background-color: #1c355e; color: white; border-radius: 16px; padding: 14px; display: flex; align-items: center; gap: 12px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
            .bandeau-title {{ font-size: 12px; font-weight: 900; tracking-wide: 0.5px; text-transform: uppercase; line-height: 1.3; }}
            .tiroir-box {{ background-color: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; border-radius: 12px; padding: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700; margin-bottom: 16px; }}
            .close-btn {{ background: none; border: none; color: #dc2626; font-size: 22px; cursor: pointer; padding: 0 5px; font-weight: bold; }}
            
            /* Cartes de factures beiges */
            .card-facture-beige {{ background-color: #faf6f0; border: 1px solid #ebdccf; border-radius: 16px; margin-bottom: 16px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.02); }}
            .card-facture-header {{ background-color: #f8fafc; padding: 12px 16px; border-bottom: 1px solid #ebdccf; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 800; color: #1e293b; }}
            .card-facture-body {{ padding: 16px; text-align: left; }}
            .details-section {{ margin-bottom: 12px; }}
            .details-label {{ font-size: 9px; color: #94a3b8; text-transform: uppercase; font-weight: bold; tracking-wide: 0.5px; margin-bottom: 2px; }}
            .details-val {{ font-size: 13px; color: #475569; font-weight: 600; }}
            .montant-flash {{ background-color: #f0fdf4; border: 1px dashed #bbf7d0; color: #166534; border-radius: 12px; padding: 12px; text-align: center; font-size: 20px; font-weight: 900; margin: 12px 0; letter-spacing: -0.5px; }}
        </style>
    </head>
    <body>

        <!-- Container Smartphone dessiné en CSS natif -->
        <div class="smartphone-container">
            
            <!-- HEADER -->
            <header>
                <h1>{nom_boutique.lower()}</h1>
                <button class="cloche-btn" onclick="ouvrirAlerteStocks()">
                    <div id="badge-cloche" class="hidden badge-num">0</div>
                    <span id="icone-cloche">🔔</span>
                </button>
            </header>
    """

# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 4 SUR 7)
# =====================================================================

    html_content += """
            <!-- GRILLE DES ACTIONS DE LA MAQUETTE 1 -->
            <main class="grid grid-cols-2 gap-4 mb-6">
                <div onclick="chargerStocks()" class="bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer active:scale-98 active:bg-slate-100 transition-all shadow-2xs">
                    <i class="text-2xl text-indigo-900 fa-solid fa-box"></i>
                    <span class="text-xs font-black text-slate-600 text-center tracking-tight">État des Stocks</span>
                </div>
                <div onclick="chargerStatistiques()" class="bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer active:scale-98 active:bg-slate-100 transition-all shadow-2xs">
                    <i class="text-2xl text-indigo-900 fa-solid fa-chart-bar"></i>
                    <span class="text-xs font-black text-slate-600 text-center tracking-tight">Chiffre d'Affaires</span>
                </div>
            </main>

            <!-- REGISTRE GÉNÉRAL DE LA MAQUETTE 1 -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 text-center mb-6 shadow-xs flex flex-col items-center">
                <i class="text-3xl text-slate-500 fa-solid fa-clipboard-check mb-2"></i>
                <h2 class="text-base font-black text-slate-800 mb-1">Registre Général</h2>
                <p class="text-2xs text-slate-400 mb-3 font-medium">Transactions de la boutique par caissière</p>
                <i class="text-xs text-slate-300 fa-solid fa-chevron-right animate-pulse"></i>
            </div>

            <!-- SECTION SÉLECTION CAISSIÈRE AVEC LES MACARONS TACTILES -->
            <section class="flex-grow">
                <h3 class="text-2xs font-extrabold text-slate-400 uppercase tracking-wider mb-3">Sélectionnez une caissière à auditer :</h3>
                <div id="liste-boutons-caissieres" class="flex flex-wrap gap-2.5">
                    <!-- Les macarons élégants des vendeuses s'injectent ici automatiquement en JS -->
                </div>
            </section>

            <!-- 📱 FENÊTRE MODALE DES FACTURES (MAQUETTE 2 - CACHÉE AU DÉPART) -->
            <div id="modal-facturation" class="hidden absolute inset-0 bg-white/98 px-5 py-6 rounded-[30px] z-50 flex-col overflow-y-auto transition-all duration-200">
                <!-- Header Dossier Bleu Nuit de ton dessin -->
                <div class="bg-[#1c355e] text-white rounded-2xl p-4 flex items-center gap-4 mb-4 shadow-md">
                    <i class="text-2xl fa-solid fa-folder-open"></i>
                    <div class="text-left font-black tracking-wider text-xs uppercase leading-tight">
                        DOSSIER FACTURES :<br><span id="nom-caissiere-titre" class="text-emerald-400 font-black text-sm">--</span>
                    </div>
                </div>

                <!-- Tiroir Caisse et Bouton de Fermeture -->
                <div class="bg-[#e4effb] border border-[#cbdff4] text-[#1c355e] rounded-xl p-3 flex justify-between items-center text-xs font-bold shadow-3xs mb-4">
                    <span id="compteur-factures-tiroir">Tiroir-Caisse : 0 facture(s)</span>
                    <button onclick="fermerModal()" class="text-rose-600 text-xl px-2 py-0.5 font-black cursor-pointer active:scale-90 transition-transform"><i class="fa-solid fa-xmark"></i></button>
                </div>

                <!-- Conteneur Dynamique pour empiler tes fiches de factures beiges -->
                <div id="contenu-factures-modale" class="space-y-4 pb-6"></div>
            </div>

        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 5 SUR 7)
# =====================================================================

    html_content += """
        <script>
            const API_KEY = localStorage.getItem('KASHFLOW_KEY') || "";
            let listeStocksGlobaux = []; // Stockage temporaire pour la cloche
            
            if(!API_KEY) {
                const key = prompt("Sécurité d'accès d'usine\\n\\nVeuillez saisir la clé de sécurité API de votre boutique :");
                if(key) {
                    localStorage.setItem('KASHFLOW_KEY', key.trim());
                    window.location.reload();
                }
            }

            // --- ALLUMAGE DE SÉCURITÉ EN TÂCHE DE FOND ---
            if(API_KEY) {
                verifierAlertesStocksEnArrierePlan();
                chargerProfilsCaissieresTactiles();
                // La cloche interroge le serveur automatiquement toutes les 20 secondes
                setInterval(verifierAlertesStocksEnArrierePlan, 20000);
            }

            function fermerModal() {
                document.getElementById('modal-facturation').classList.replace('flex', 'hidden');
            }

            // --- 🔔 CLOCHE DE LA MAQUETTE 1 DYNAMIQUE ---
            async function verifierAlertesStocksEnArrierePlan() {
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    listeStocksGlobaux = res.inventaire_magasin || [];
                    
                    const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                    const nombreAlertes = articlesEnAlerte.length;
                    
                    const cloche = document.getElementById('icone-cloche');
                    const badge = document.getElementById('badge-cloche');
                    
                    if(nombreAlertes > 0) {
                        cloche.className = "fa-solid fa-bell text-rose-500 text-lg";
                        badge.innerText = nombreAlertes;
                        badge.classList.remove('hidden');
                    } else {
                        cloche.className = "fa-solid fa-bell text-slate-400";
                        badge.classList.add('hidden');
                    }
                } catch(e) { console.error("Erreur check cloche:", e); }
            }

            function ouvrirAlerteStocks() {
                const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "STOCKS CRITIQUES";
                document.getElementById('compteur-factures-tiroir').innerText = `Alerte : ${articlesEnAlerte.length} produit(s)`;
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "";
                
                if(articlesEnAlerte.length === 0) {
                    contenu.innerHTML = "<div class='bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl p-5 text-center font-bold text-xs shadow-3xs'>🟢 Aucun produit en seuil critique. Tous les stocks sont confortables !</div>";
                    return;
                }
                
                let html = "";
                articlesEnAlerte.forEach(i => {
                    html += `
                    <div class='bg-rose-50 border border-rose-100 text-rose-900 rounded-2xl p-4 flex justify-between items-center font-bold text-xs shadow-3xs'>
                        <div>⚠️ ${i.article_modele.toUpperCase()}</div>
                        <div class='text-right text-rose-700 bg-white px-3 py-1 rounded-xl border border-rose-200 shadow-4xs'>Reste : ${i.quantite_restante} pcs</div>
                    </div>`;
                });
                contenu.innerHTML = html;
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 6.1 SUR 7)
# =====================================================================

    html_content += """
            // --- 📋 ENTRÉE DES EMPLOYÉS ET CRÉATION DES MACARONS TACTILES ---
            async function chargerProfilsCaissieresTactiles() {
                const conteneur = document.getElementById('liste-boutons-caissieres');
                try {
                    const r = await fetch('/employes/liste', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    conteneur.innerHTML = "";
                    res.employes.forEach(emp => {
                        const bouton = document.createElement('button');
                        // Style de tes macarons : bleu clair avec petite icône utilisateur
                        bouton.className = "macaron-btn";
                        bouton.innerHTML = `<i class="fa-solid fa-user text-blue-400"></i> ${emp}`;
                        bouton.onclick = () => chargerHistoriqueCaissiereDirect(emp);
                        conteneur.appendChild(bouton);
                    });
                } catch(e) { conteneur.innerHTML = "<span class='text-rose-500 font-bold text-xs'>❌ Liaison employés coupée.</span>"; }
            }

            // --- 📱 ALLUMAGE CHIRURGICAL DE TON DEUXIÈME DESIGN ---
            async function chargerHistoriqueCaissiereDirect(caissiere) {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = caissiere.toUpperCase();
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Ouverture du dossier comptable...</p>";

                try {
                    const r = await fetch(`/ventes/caissiere/${encodeURIComponent(caissiere)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    document.getElementById('compteur-factures-tiroir').innerText = `Tiroir-Caisse : ${res.total_ventes_effectuees} facture(s)`;
                    
                    if(!res.liste_ventes || res.liste_ventes.length === 0) {
                        contenu.innerHTML = `<div class='bg-slate-50 border border-slate-200 rounded-2xl p-5 text-center text-slate-400 font-bold text-xs shadow-3xs'>Tiroir-Caisse vide. Aucune opération enregistrée pour ${caissiere.toUpperCase()}.</div>`;
                        return;
                    }

                    let html = "";
                    // 3. Dessin rigoureux des cartes de factures beiges de ta maquette 2
                  // 🟢 REMPLACE LA SÉQUENCE TEMPLATE DES FACTURES PAR CELLE-CI :
                    res.liste_ventes.forEach(v => {
                        html += `
                        <div class="card-facture-beige">
                            <div class="card-facture-header">
                                <span>Facture #00${v.facture_no}</span>
                                <span style="color:#94a3b8;">⚙️</span>
                            </div>
                            <div class="card-facture-body">
                                <div class="details-section">
                                    <div class="details-label">Détails du Client</div>
                                    <div class="details-val">👤 Client : ${v.client.toUpperCase()}</div>
                                </div>
                                <div class="details-section" style="border-top: 1px dashed #ebdccf; padding-top: 8px; margin-top: 8px;">
                                    <div class="details-label">Détails de la Transaction</div>
                                    <div class="details-val">&nbsp;🕒 ${v.date} à ${v.heure}</div>
                                </div>
                                <div class="montant-flash">
                                    ${v.montant_ttc}
                                </div>
                                <div class="details-section">
                                    <div class="details-label">Produit</div>
                                    <div class="details-val" style="font-size:14px; color:#1e293b; font-weight:800;">${v.article.toUpperCase()}</div>
                                </div>
                            </div>
                        </div>`;
                    });

                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Erreur de décodage du dossier.</p>"; }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 6.2 SUR 7)
# =====================================================================

    html_content += """
            async function chargerStocks() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "INVENTAIRE DES STOCKS";
                document.getElementById('compteur-factures-tiroir').innerText = "État Centralisé";
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Lecture du stock central...</p>";
                
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let html = "<div class='bg-white border border-slate-200 rounded-2xl p-4 shadow-3xs overflow-x-auto'><table class='w-full text-left text-xs border-collapse'><thead><tr class='text-slate-400 border-b border-slate-100 font-bold'><th class='pb-2'>Article</th><th class='text-center pb-2'>Reste</th><th class='text-right pb-2'>Statut</th></tr></thead><tbody>";
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'bg-red-50 text-red-700 border-red-100' : 'bg-green-50 text-green-700 border-green-100';
                        html += `<tr class='border-b border-slate-50/60'>
                            <td class='py-3 font-bold text-slate-700 uppercase tracking-tight'>${i.article_modele}</td>
                            <td class='text-center font-black text-slate-800'>${i.quantite_restante} pcs</td>
                            <td class='text-right'><span class='px-2 py-0.5 rounded-full border text-[10px] font-black ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table></div>";
                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Erreur de lecture d'inventaire.</p>"; }
            }

            async function chargerStatistiques() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                let cible = prompt("Tapez la date au format J/M/AAAA (ex: 12/9/2026) :");
                if(!cible) return; // 🟢 CORRECTIF CRITIQUE : Syntaxe nettoyée et débloquée
                
                document.getElementById('nom-caissiere-titre').innerText = "RAPPORTS COMPTABLES";
                document.getElementById('compteur-factures-tiroir').innerText = `Date : ${cible}`;
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Analyse des performances financières...</p>";
                
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    contenu.innerHTML = `
                        <div class='space-y-4'>
                            <div class='bg-emerald-50 border border-emerald-200 rounded-2xl p-5 text-center text-emerald-900 shadow-3xs'>
                                <p class='text-[10px] font-black text-emerald-600 uppercase tracking-wider mb-1'>Chiffre d'Affaires du ${cible}</p>
                                <p class='text-2xl font-black tracking-wide'>${res.chiffre_affaires_ttc} FCFA</p>
                            </div>
                            <div class='bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-medium space-y-2 shadow-4xs text-left'>
                                <p class='text-slate-600'>🔥 <b>Article Star :</b> <span class='text-slate-800 font-black uppercase tracking-tight'>${res.article_le_plus_vendu}</span></p>
                                <p class='text-slate-400 border-t border-slate-200/60 pt-2 font-normal italic'>📈 ${res.comparatif_performance_n_1}</p>
                            </div>
                        </div>`;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Échec de calcul financier.</p>"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version Spéciale Google Pixel - ÉTAPE 7 SUR 7)
# =====================================================================

@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """Intercepte, calcule la TVA et centralise la vente du magasin."""
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")
        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute("SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}
        regime_tva = int(donnees.applique_tva) if donnees.applique_tva is not None else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
        num_facture = data_base.enregistrer_vente_sql(client=donnees.client, article=donnees.article, desc_unique=donnees.description_unique, mnt_ht=total_ht, tva=tva_calculee, ttc=total_ttc, caissiere=donnees.caissiere, reference_locale=donnees.reference_locale)
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """Calcule le CA et le produit star de la période pour l'écran mobile."""
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {"chiffre_affaires_ttc": analyse["ca_total"], "article_le_plus_vendu": str(analyse["produit_phare"]).replace("{", "").replace("}", ""), "comparatif_performance_n_1": analyse["message_performance"]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Extrait l'audit des ventes d'une vendeuse pour l'affichage mobile du patron."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes: return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            # 🟢 SÉCURITÉ UNIONS : Extraction propre du tuple SQLite d'origine
            liste_formatee.append({"facture_no": v[0], "client": v[1], "article": str(v[2]).replace("{", "").replace("}", ""), "montant_ttc": f"{v[3]} FCFA", "date": v[4], "heure": v[5]})
        return {"total_ventes_effectuees": len(liste_formatee), "liste_ventes": liste_formatee}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

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
            rapport_stock.append({"article_modele": string_modele, "quantite_restante": l[1], "ventes_totales": l[2], "seuil_alerte_applique": seuil, "statut_commande": etat_alerte})
        return {"inventaire_magasin": rapport_stock}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/employes/liste", dependencies=[Depends(verifier_cle_api)])
def api_liste_des_employes():
    """Extrait la liste unique des caissières enregistrées pour alimenter le smartphone du patron."""
    try:
        liste_employes = data_base.recuperer_liste_tous_employes()
        if not liste_employes: return {"employes": ["caissiere1", "caissiere2"]}
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
