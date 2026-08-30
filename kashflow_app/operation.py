# =====================================================================
# MODULE CALCULS ET DESIGN : operation.py (Version 5.0)
# =====================================================================
from fpdf import FPDF

# Taux officiel de TVA en vigueur au Cameroun (19.25%)
TAUX_TVA = 19.25 / 100

def calcule_des_elements_facture(prix_unitaire_ht, quantite):
    """Effectue les calculs financiers de la vente."""
    try:
        prix = float(prix_unitaire_ht)
        qt = int(quantite)
        if prix <= 0 or qt <= 0:
            return None
            
        montant_ht = prix * qt
        valeur_tva = montant_ht * TAUX_TVA
        montant_ttc = montant_ht + valeur_tva
        
        return {
            "montant_ht": round(montant_ht, 2),
            "valeur_tva": round(valeur_tva, 2),
            "total_ttc": round(montant_ttc, 2)
        }
    except Exception:
        return None

def generer_recu_pdf(nom_boutique, num_facture, nom_client, nom_article, imei_appareil, quantite, mnt_ht, valeur_tva, total_ttc):
    """Génère le reçu officiel au format PDF avec numéro IMEI de l'appareil et filigrane."""
    try:
        pdf = FPDF(orientation="P", unit="mm", format="A4")
        pdf.add_page()
        
        # 1. FILIGRANE DE SÉCURITÉ ANTI-FRAUDE (Gris très discret en arrière-plan)
        pdf.set_font("Helvetica", "B", 30)
        pdf.set_text_color(242, 242, 242) 
        pdf.text(x=20, y=140, txt=f"{nom_boutique.upper()} - PIÈCE COMPTABLE")
        
        # Réinitialisation de la couleur du texte en noir normal
        pdf.set_text_color(0, 0, 0)
        
        # 2. EN-TÊTE DYNAMIQUE DU MAGASIN
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(190, 10, f"{nom_boutique.upper()}", ln=1, align="C")
        
        pdf.set_font("Helvetica", "B", 11)
        # On formate l'identifiant de la facture sur 4 chiffres minimum (ex: Facture N°0008)
        pdf.cell(190, 8, f"FACTURE N°{str(num_facture).zfill(4)}", ln=1, align="C")
        pdf.ln(5)
        
        pdf.cell(190, 0, "--------------------------------------------------", ln=1, align="C")
        pdf.ln(10)
        
        # 3. INFORMATIONS DE LA TRANSACTION ET DE LA GARANTIE
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(190, 8, f"Client : {nom_client}", ln=1)
        pdf.cell(190, 8, f"Article vendu : {nom_article}", ln=1)
        
        # EXCLUSIVITÉ V5.0 : Insertion de l'IMEI indispensable pour le SAV
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(190, 8, f"N° IMEI Appareil : {imei_appareil}", ln=1)
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(190, 8, f"Quantité : {quantite}", ln=1)
        pdf.ln(5)
        
        pdf.cell(190, 0, "--------------------------------------------------", ln=1)
        pdf.ln(5)
        
        # 4. BLOC DES CALCULS FINANCIERS ALIGNÉS À DROITE
        pdf.cell(100, 8, "Montant Total Hors Taxes (HT) :", ln=0)
        pdf.cell(90, 8, f"{mnt_ht} FCFA", ln=1, align="R")
        
        pdf.cell(100, 8, "TVA Calculée (19.25%) :", ln=0)
        pdf.cell(90, 8, f"{valeur_tva} FCFA", ln=1, align="R")
        
        # Net à Payer mis en évidence en gras
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(100, 10, "NET À PAYER (TTC) :", ln=0)
        pdf.cell(90, 10, f"{total_ttc} FCFA", ln=1, align="R")
        
        pdf.ln(15)
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(190, 5, f"Le matériel est garanti contre tout défaut de fabrication. Merci pour votre confiance !", ln=1, align="C")
        
        # Génération du nom de fichier unique basé sur le magasin et le numéro de facture
        nom_magasin_propre = nom_boutique.replace(' ', '_')
        nom_fichier = f"kashflow_app/recu_{nom_magasin_propre}_F{num_facture}.pdf"
        pdf.output(nom_fichier)
        return True
    except Exception as e:
        print(f"[ERREUR COMPILATION PDF] : {e}")
        return False
  