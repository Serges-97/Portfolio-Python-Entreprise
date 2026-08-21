# detail_client = [
#     {"nom": "serges" , "index_precedent": "moi" , "index_actuel": 300},
#     {"nom": "junior" , "index_precedent": 2000 , "index_actuel": 400},
#     {"nom": "marie" , "index_precedent": 2400 , "index_actuel": 4000}
# ]

nom_client  = input("nom du client :")
index_prec = float(input("entrez l'index precedent :"))
index_act = float(input("entrez l'index actuel : "))

detail_client = [
    {"nom": nom_client , "index_precedent": index_prec , "index_actuel": index_act}
]

def calcul_facture_palier(detail_client):
    print("=== RAPPORT DE FACTURATION ELECTRICITE ====")
    for clients in detail_client:
        try:
            ancien_index = float(clients["index_precedent"])
            nouveau_index = float (clients["index_actuel"])

            consomation = nouveau_index-ancien_index
            if consomation <= 0 :
                print(f"[ERREUR DU COMPTEUR] client : {clients["nom"]} index actuel inferieur a index precedent. releve impossible ")
                continue

            montant_facture = 0
            if consomation <= 100 :
                montant_facture = consomation * 50 
            elif consomation <= 200 :
                montant_facture = 100 * 50 + ((consomation - 100) * 75)
            else :
                montant_facture = 100 * 50 + (100 * 75) + ((consomation - 200) * 120)
                pass
            print(f"client : {clients["nom"]} | consomation : {consomation} kWh | a payer: {montant_facture} FCFA")
        except ValueError :
            print(f"entrez les valeur au bon formats !!")

client1 = calcul_facture_palier(detail_client)
print(client1)