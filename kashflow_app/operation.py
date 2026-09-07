# =====================================================================
# MODULE 2 : operation.py (Version 5.5 Pro - PARTIE 1 SUR 2)
# =====================================================================
import os
from fpdf import FPDF

# Taux officiel de la TVA en vigueur au Cameroun (19.25%)
TAUX_TVA_CAMEROUN = 19.25 / 100

def calculer_facture_dynamique(prix_unitaire_ht, quantite, applique_tva):
    """
    Calcule le montant Hors Taxes, la valeur exacte de la TVA (0%  ou 19.25%)
    et le montant toutes taxes comprises (TTC) pour la facture.
    """
    try:
        prix = float(prix_unitaire_ht)
        qt = int(quantite)
        
        # Validation rigoureuse d'ingénierie
        if prix <= 0 or qt <= 0:
            return None
            
        montant_ht = prix * qt
        
        # RÈGLE DU CAHIER DES CHARGES : Gestion des grands et petits commerces
        if int(applique_tva) == 1:
            # Grande entreprise : application stricte de la taxe nationale
            valeur_tva = montant_ht * TAUX_TVA_CAMEROUN
        else:
            # Petite boutique de quartier : vente directe sans facturation fiscale
            valeur_tva = 0.0
            
        montant_ttc = montant_ht + valeur_tva
        
        return {
            "montant_ht": round(montant_ht, 2),
            "valeur_tva": round(valeur_tva, 2),
            "total_ttc": round(montant_ttc, 2)
        }
    except Exception:
        return None
# =====================================================================
# MODULE 2 : operation.py (Version 5.5 Pro - PARTIE 2 SUR 2)
# =====================================================================

def generer_recu_pdf_industriel(nom_boutique, num_facture, nom_client, nom_article, desc_unique, quantite, mnt_ht, valeur_tva, total_ttc, nom_caissiere):
    """Génère une facture PDF hautement sécurisée avec filigrane en diagonale et traçabilité caissière."""
    try:
        from datetime import datetime
        maintenant = datetime.now()
        date_facture = maintenant.strftime("%d/%m/%Y")
        heure_facture = maintenant.strftime("%H:%M")
        
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        
        # =====================================================================
        # 🛡️ 1. FILIGRANE DE SÉCURITÉ EN DIAGONALE (FOND DE FACTURE)
        # =====================================================================
        pdf.set_font("Helvetica", "B", 28)
        # RGB (245, 245, 245) : un gris très clair invisible à la photocopie
        pdf.set_text_color(245, 245, 245)
        
        # Dessin textuel en diagonale au centre de la feuille A4
        pdf.text(x=20, y=130, txt=f"{nom_boutique.upper()} - DOCUMENT AUTHENTIQUE")
        pdf.text(x=20, y=150, txt=f"GARANTIE CONSTRUCTEUR CERTIFIEE")
        
        # Réinitialisation immédiate de la couleur en noir pour les vrais textes
        pdf.set_text_color(0, 0, 0)
        
        # =====================================================================
        # 🏢 2. EN-TÊTE OFFICIEL DE L'ENTREPRISE
        # =====================================================================
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(190, 10, f"{nom_boutique.upper()}", ln=1, align="C")
        
        pdf.set_font("Helvetica", "B", 11)
        # Numéro de facture normalisé sur 4 chiffres (ex: FACTURE N°0045)
        pdf.cell(190, 8, f"FACTURE COMMERCIALE N°{str(num_facture).zfill(4)}", ln=1, align="C")
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(190, 6, f"Émise le {date_facture} à {heure_facture}", ln=1, align="C")
        pdf.ln(5)
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(190, 0, "--------------------------------------------------------------------------------", ln=1, align="C")
        pdf.ln(8)
        
        # =====================================================================
        # 🧑‍💼 3. TRAÇABILITÉ DES ACTEURS (CLIENT & CAISSIÈRE EMETTRICE)
        # =====================================================================
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(95, 8, f"Client : {nom_client.upper()}", ln=0)
        pdf.cell(95, 8, f"Émis par : {nom_caissiere.upper()}", ln=1, align="R")
        pdf.ln(4)
        
        # =====================================================================
        # 📦 4. DÉSIGNATION TECHNIQUE DU PRODUIT (IMEI / SÉRIE)
        # =====================================================================
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(190, 8, f"Désignation Article : {nom_article}", ln=1)
        
        # Insertion dynamique de la description unique selon l'appareil électronique
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(190, 8, f"Identifiant Unique / N° IMEI / Série : {desc_unique}", ln=1)
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(190, 8, f"Quantité facturée : {quantite} unité(s)", ln=1)
        pdf.ln(5)
        
        pdf.cell(190, 0, "--------------------------------------------------------------------------------", ln=1)
        pdf.ln(6)
        
        # =====================================================================
        # 📊 5. GRILLE FINANCIÈRE ET FISCALE ALIGNÉE À DROITE
        # =====================================================================
        pdf.cell(100, 8, "Montant Total Hors Taxes (HT) :", ln=0)
        pdf.cell(90, 8, f"{mnt_ht} FCFA", ln=1, align="R")
        
        pdf.cell(100, 8, "Taxe sur la Valeur Ajoutée (TVA) :", ln=0)
        pdf.cell(90, 8, f"{valeur_tva} FCFA", ln=1, align="R")
        
        # Net à payer mis en valeur en gras de niveau PGI
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(100, 10, "NET A PAYER (TTC) :", ln=0)
        pdf.cell(90, 10, f"{total_ttc} FCFA", ln=1, align="R")
        
        pdf.ln(12)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(190, 5, "Le matériel est garanti contre tout vice de fabrication sur présentation de ce reçu.", ln=1, align="C")
        pdf.cell(190, 5, "Merci pour votre confiance !", ln=1, align="C")
        
        # Sauvegarde sécurisée dans le dossier local du projet
        nom_magasin_propre = nom_boutique.replace(' ', '_').replace('/', '_').replace('\\', '_')
        dossier_pdf = os.path.dirname(os.path.abspath(__file__))  # Dossier kashflow_app
        nom_fichier = os.path.join(dossier_pdf, f"recu_{nom_magasin_propre}_F{num_facture}.pdf")
        pdf.output(nom_fichier)
        
        # 🟢 COLLE EXACTEMENT CE NOUVEAU BLOC À LA PLACE :
        # =====================================================================
        # 📂 CONFIGURATION DU DOSSIER REEL SUR LE BUREAU DU CLIENT (SÉRIE C)
        # =====================================================================
        import sys
        
        # Détection du dossier d'exécution réel (PC ou .exe compilé)
        if getattr(sys, 'frozen', False):
            dossier_reel_app = os.path.dirname(sys.executable)
        else:
            dossier_reel_app = os.path.dirname(os.path.abspath(__file__))
            
        # Création automatique du sous-dossier s'il n'existe pas
        dossier_factures = os.path.join(dossier_reel_app, "Factures_Emises")
        if not os.path.exists(dossier_factures):
            os.makedirs(dossier_factures)
            
        nom_magasin_propre = nom_boutique.replace(' ', '_').replace('/', '_').replace('\\', '_')
        nom_fichier = os.path.join(dossier_factures, f"recu_{nom_magasin_propre}_F{num_facture}.pdf")
        
        # Sauvegarde du PDF dans le sous-dossier du Bureau
        pdf.output(nom_fichier)
        
        # =====================================================================
        # 🖨️ IMPRESSION AUTOMATIQUE DIRECTE (RÈGLES DE SÉRIE C)
        # =====================================================================
        try:
            # os.startfile envoie l'ordre d'impression silencieux à l'imprimante par défaut de Windows
            os.startfile(nom_fichier, "print")
        except Exception as e:
            # Si aucune imprimante n'est branchée, le code ne crash pas, il écrit juste un avertissement
            print(f"[INFO IMPRIMANTE] : Aucune imprimante détectée ou configurée par défaut. {e}")
            
        return True
  
    except Exception as e:
        print(f"[ERREUR DESSINATEUR PDF V5.5] : {e}")
        return False
