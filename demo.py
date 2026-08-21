# nom_client = input("entrez le nom du client !!:")
# ht = float(input("entrez le montant hors taxe !!:"))
# montan_tva = ht * 0.20 
# montan_ttc = ht + montan_tva
# print(f" le client {nom_client} doit payer un total de {montan_ttc} eurros")


#montant_facture = float(input("entrer le montant de la facture !!"))
# if montant_facture < 5000 :
#     print("ce client a droit a une reduction de 10%")
# else:
#     print("pas de reduction pour ce montant!")
# print("fin du code")


# score_client = int (input("entrez le score du client !:"))
# if score_client >= 90:
#     statut = "client VIP"
# elif score_client >= 70:
#     statut = "client fidel"
# else : 
#     statut = "client standard"
# print(f"{statut}") 



# nom_client = input("entrez le nom du client !!:")
# ht = float(input("entrez le montant hors taxe !!:"))
# montan_tva = ht * 0.20 
# montan_ttc = ht + montan_tva
# print(f" le client {nom_client} doit payer un total de {montan_ttc} euros")
# if montan_ttc >= 5000 :
#   remise = montan_ttc * 0.05 
#   montan_ttc -= remise
#   print(f"le client {nom_client} doit payer un total de {montan_ttc} euro")
#   print(f"il a beneficier d'une remise de 5% ")
# else :
#   print(f" le client {nom_client} doit payer un total de {montan_ttc} euros")


# compteur = 1 
# while compteur <= 3:
#     print(f"traitement du dossier numero {compteur}")
#     compteur += 1 
# print(f"tous les dossiers ont ete traité")


# for i in range(3) :
#     print(f"tentative de connexion au serveur...(essai{i+1})") 


# compteur = 1 
# while compteur <= 3:
#     nom_client = input("entrez le nom du client !!:")
#     ht = float(input("entrez le montant hors taxe !!:"))
#     montan_tva = ht * 0.20 
#     montan_ttc = ht + montan_tva
#     # print(f" le client {nom_client} doit payer un total de {montan_ttc} euros")
#     if montan_ttc >= 5000 :
#       remise = montan_ttc * 0.05 
#       montan_ttc -= remise
#       print(f"le client {nom_client} doit payer un total de {montan_ttc} euro")
#       print(f"il a beneficier d'une remise de 5% ")
#     else :
#       print(f" le client {nom_client} doit payer un total de {montan_ttc} euros")
#     compteur += 1
# print(f"session de facturation terminée!!")



# def calcul_tva(montan_ht):
#     tva = montan_ht * 0.20
#     return tva
# facture_1 = int(input("entrer la facture 1 !:"))
# tva_facture_1 = calcul_tva(facture_1)
# print(f"la tva pour un montant de {facture_1} est de: {tva_facture_1}")



# def calculer_facture(montant_ht):
#     montant_ttc = montant_ht + (montant_ht * 0.2)
#     if montant_ttc >= 5000 :
#         remise = montant_ttc * 0.05
#         montant_ttc -= remise
#         print(f"vous avez beneficier d'une remise de 5%")
#     return montant_ttc 

# compteur = 1
# while compteur <= 3:
#     nom_client = input("entrez le nom du client !:")
#     mt_ht = float(input("entrez le montant hors taxe!:"))
#     ttc_finale = calculer_facture(mt_ht)
#     print(f"le client {nom_client} doit payer {ttc_finale} euros ")
#     compteur += 1



                                    # les listes ou tableau

# facture_du_jour = [1200 , 450 , 6000 , 80]
# print(facture_du_jour)
# facture_du_jour.append(3100)
# print(facture_du_jour)

# for montant in facture_du_jour :
#     print(f"analyse du montant : {montant}€")

#exo

# def calculer_facture(montant_ht):
#     montant_ttc = montant_ht + (montant_ht * 0.2)
#     if montant_ttc >= 5000 :
#         remise = montant_ttc * 0.05
#         montant_ttc -= remise
#         print(f"vous avez beneficier d'une remise de 5%")
#     return montant_ttc 

# liste_achats = [1500, 6000 ,350 ,8000]

# for montant in liste_achats :
#     ttc_final = calculer_facture(montant)
#     print(f"le prix finale est {ttc_final}")


                                  # les dictionaires 

# client_data = { 
#     "nom": "serges",
#     "montant_ht": 4500,
#     "est_vide" : True
# }
# print(client_data["nom"])
# print(client_data["montant_ht"])


# base_client = [
#     {"nom":"serges" , "montant_ht":5000},
#     {"nom":"john" , "montant_ht":1500},
#     {"nom":"marc" , "montant_ht" :6000}
# ]

# for client in base_client :
#     print(f"le client {client["nom"]} a un montan hors taxe de {client["montant_ht"]}")

                 # exo

# def calculer_facture(montant_ht):
#     montant_ttc = montant_ht + (montant_ht * 0.2)
#     if montant_ttc >= 5000 :
#         remise = montant_ttc * 0.05
#         montant_ttc -= remise
#         print(f"vous avez beneficier d'une remise de 5%")
#     return montant_ttc 


# base_client = [
#     {"nom": "serges" , "montant_ht":5000},
#     {"nom":"john" , "montant_ht":1500},
#     {"nom":"marc" , "montant_ht" :6000}
# ]

# for client in base_client :
#     mt_ht = client["montant_ht"]
#     ttc_finale = calculer_facture(mt_ht)
#     print(f"le client {client["nom"]} doit paye un total de {ttc_finale} euro")


                                              # la gestion des erreurs et exceptions

# saisie = input("entrez votre montant:")

# try:
#     montant = float(saisie)
#     print(f"la valeur saisie est : {montant} €")
# except ValueError :
#     print("erreur : vous devez saisie un nombre valide! , la valeur par defaut sera 0")
#     montant = 0
# print("le programe continue de tourné")

#exo

# def calculer_facture(montant_ht):
#     montant_ttc = montant_ht + (montant_ht * 0.2)
#     if montant_ttc >= 5000 :
#         remise = montant_ttc * 0.05
#         montant_ttc -= remise
#         print(f"vous avez beneficier d'une remise de 5%")
#     return montant_ttc 

# base_client = [
#     {"nom": "serges" , "montant_ht":5000},
#     {"nom":"john" , "montant_ht":"rien"},
#     {"nom":"marc" , "montant_ht" :6000}
# ]

# for client in base_client :
#     try:
#         montant = float (client["montant_ht"])
#         v = calculer_facture(montant)
#         print (f"le client doit payer {v} €")
#     except ValueError :
#        print(f"impossible de calculer la facture de {client["nom"]} : montant invalide ")

  






                     #POO

       #les class

# class client : 
#     def __init__(self, nom_recu , montant_recu) :
#         self.nom = nom_recu
#         self.montant_ht = montant_recu

#     def afficher_details(self):
#         print(f"client d'entreprise : {self.nom} (montant : {self.montant_ht})")

# client_a = client("serges" , 5000)
# client_b = client("marc" , 6000)

# client_a.afficher_details()
# client_b.afficher_details()
        
      #exo

# class client :
#     def __init__(self , nom_client , montant_ht) :
#         self.nom = nom_client 
#         self.montant = montant_ht

#     def calculer_ttc(self):
#         montant_ttc = self.montant + (self.montant * 0.2) 
#         if montant_ttc >= 5000 :
#             remise = montant_ttc * 0.05 
#             montant_ttc -= remise
#             print(f"tu a optenu une remise de 5%")
#             print(f"ton nouveau solde a payer est {montant_ttc}")     
#             return montant_ttc

# nouveau_client = client("serges",5000)
# nouveau_client.calculer_ttc()



                                     # les fichiers 
  #ecrire (sauvegarder)

# with open ("facture.txt" , "w") as fichier:
#     fichier.write("facturede serges : 5700 euros \n")
#     fichier.write("facture de marc : 7200 euros\n")
# print("les dossiers ont été sauvegardeés dans facture.txt !")


# with open ("facture.txt" , "r") as fichier:
#     contenu = fichier.read()
#     print("----lecture du fichier de sauvegarde----")
#     print(contenu)
    
       #exo


# class client :
#     def __init__(self , nom_client , montant_ht) :
#         self.nom = nom_client 
#         self.montant = montant_ht
    
#     def calculer_ttc(self):
#         montant_ttc = self.montant + (self.montant * 0.2) 
#         if montant_ttc >= 5000 :
#             remise = montant_ttc * 0.05 
#             montant_ttc -= remise
#         with open("rapport.txt" , "a") as fichier :
#             fichier.write(f"client: {self.nom} | total : {montant_ttc} euros \n")
#         return montant_ttc

# t1 = client("serges" , 5000)
# t2 = client ("marc" , 2000)

# t1.calculer_ttc()
# t2.calculer_ttc() 

 
        # les MODUL(paquet)



# import random
# import os

# numero_facture = random.randint(1000 , 9999)
# print(f"le numero de la facture genrer est : #{numero_facture}")
# print(f"dossier de travail : {os.getcwd()}") # le dossier dans le quel python travail


  # exo

# import json
# import os

# entreprise_client = {
#       "nom": "tech solution",
#       "statut": "VIP" ,
#       "chiffre_affaire_ht":15000
# }
 
# texte_json = json.dumps(entreprise_client)
# print(texte_json)

# with open("client.json" , "w") as fichier :
#     fichier.write( texte_json)


# import sqlite3

#  # connexion(creer un fichier entreprise.db dans notre dossier)
# connexion = sqlite3.connect("entreprise.db")
# curseur = connexion.cursor()

# curseur.execute("""
# CREATE TABLE IF NOT EXISTS clients(
#                 id INTEGER PRIMARY KEY AUTOINCREMENT ,
#                 nom TEXT ,
#                 montant_ht REAL
# )
# """)

# curseur.execute("INSERT INTO clients(nom , montant_ht) VALUES ('tech solution' , 15000)")

# # sauvegarde des modification et fermeture
# connexion.commit()
# connexion.close()

# print("base de données créée et client enregistrer avec succés !")




           #creation d'une api web avec FastApi

from fastapi import FastAPI

app = FastAPI()

#on creer une route (une adresse url) accessible sur notre serveur
#le signe "/" represente l'adresse d'acceuil, la racine
@app.get("/")
def repondre_accueil():
    # notre api renvois un dictionaire , FastApi le convertira automatiquement en json
    return {"message":"bienvenue sur l'api de facturation de mon entreprise !!"}

#une nouvelle route qui prend un parametre dynamique dans l'url: {montant_ht}
@app.get("/calculer/{montant_ht}")
def calculer_api(montant_ht: float):
    montant_ttc = montant_ht + (montant_ht * 0.20)
    if montant_ttc >= 5000 :
         remise = montant_ttc * 0.05
         montant_ttc -= remise
         statut_remise = "remise de 5% appliquée"
    else:
        statut_remise = "aucune remise "
    # on renvoi le resulta au format json
    return {
        "montant_initial_ht" : montant_ht , 
        "montant_final_ttc" : montant_ttc,
        "statut" : statut_remise
    }

    