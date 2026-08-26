from fpdf import FPDF

# definition du taux officiel de la tva au cameroun dans une variable globale (19.25%)
taux_tva = 19.25 / 100

def calcule_des_elements_facture(prix_unitaire_ht , quantite):
     try:
        prix = float(prix_unitaire_ht)
        qt = int(quantite)

        if prix < 0 or qt < 0:
            print("[ERREUR] le prix unitaire et la quantite doivent etre superieur a zero")
            return None

        montant_ht = prix * qt
        valeur_tva = montant_ht * taux_tva
        montant_ttc = montant_ht + valeur_tva

        # on arrondit a 2 decimales pour eviter les chiffres infinie
        # on range tout dans un dictionnaire propre pour le renvoyer au programme principal
        return{
            "montant_ht" : round(montant_ht , 2) , 
            "valeur_tva" : round(valeur_tva , 2) ,
            "total_ttc":round(montant_ttc , 2)
        }
          
     except Exception as e:
         print (f"[ERREUR MOTEUR] echec du calcul financier. raison:{e}")
         return None

     # ecriture de la fonction qui nous permet de generer un pdf de la facture 

def generer_recu_pdf(nom_client , nom_article , quantite , montant_ht , valeur_tva , total_ttc):
    try:

        # on initialise une page blanche au format portait (p) et  millimetres (mm) 
        pdf = FPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()

        #configuration de la police d'ecriture du pdf (nom de la police , style de la police , taille de la police)
        pdf.set_font("Arial", size=12) # ou pdf.set_font("helvetica", "B" ,16)

        #dessin de l'entete de la boutique (largueur , hauteur , texte , bordure , saut de ligne , alignement)
        pdf.cell(190 , 10 ,"BOUTIQUE DE BIENS ET SERVICE - REçU OFFICIEL" , ln = 1 , align="C")
        pdf.ln(5) # petit espace vertical  de 5mm

        #ligne de separation esthetique 
        pdf.cell (190 , 0 , "_" * 50, ln=1 , align="C")
        pdf.ln(10) 

        # information textuel sur le client et la transaction
        pdf.set_font("helvetica" , "", 12)
        pdf.cell(190 , 8 , f"client : {nom_client}" , ln= 1)
        pdf.cell(190 , 8 , f"article : {nom_article}" , ln= 1)
        pdf.cell(190 , 8 , f"quantité : {quantite}" , ln= 1)
        pdf.ln(5)

        pdf.cell (190 , 0 , "_" * 50, ln=1 )
        pdf.ln(5)

        # detail financiere claires
        pdf.cell(100 , 8 , f"Montant Total Hors Taxes (HT) :" , ln= 0)
        pdf.cell(90 , 8 , f"{montant_ht} FCFA" , ln= 1,align="R" )

        pdf.cell(100 , 8 , "TVA calculéé (19.25%):" , ln= 0)
        pdf.cell(90 , 8 , f"{valeur_tva} FCFA" , ln= 1 , align="R")

        # passage en gras pour le net a payer
        pdf.set_font("helvetica" , "B", 13)
        pdf.cell(100 , 10 , "NET A PAYER (TTC):" , ln= 0)
        pdf.cell(90 , 10 , f"{total_ttc} FCFA" , ln= 1 , align="R")

        pdf.ln(15)
        pdf.set_font("helvetica" , "I" ,10)
        pdf.cell(90 , 5, "Merci pour votre confiance ! A bientot." ,ln=1 , align="C")

        # on genere un nom de fichier unique basé sur le client et on l'enregistre sur le disque dur( dans le dossier courant)
        nom_fichier = f"kashflow_app/reçu_{nom_client.replace(' ' , '_')}.pdf"
        pdf.output(nom_fichier)

        print(f"fichier pdf generer avec Succues : {nom_fichier}")
        return True
    except Exception as e:
        print(f"[ERRURE PDF] Impossible de generer le document : {e}")
        return False
        
              