# profil_client = {
#     "nom_client": "serges" ,
#     "revenu_mensuel": 3000,
#     "historique_credit": 1 ,   # 1 s'il a deja eut des impayer et 0 sinon
#     "age_client":23
# }


nom = input("entrer le nom du client !:")
revenu_client= input("entrez le revenu mensuel du client:")
historique_client = int(input("le client a-t-il des impayer !? (0 pour NON , 1 pour OUI) :"))
age = input("entrez l'arge du client :")

# on range les donne saisie dans le dictionaire
profil_client = {
    "nom_client": nom,
    "revenu_mensuel": revenu_client,
    "historique_credit": historique_client,
    "age_client": age
}


def evaluer_profil(profil_client):
        
        score = 0 
        try: 
            revenu = float(profil_client["revenu_mensuel"])
            if revenu > 2000 :
                score += 50
            elif revenu >= 1000 and revenu <= 2000 :
                score += 30
            else :
                score += 10
        except ValueError:
            print("veuiller entrez vos revenu sur forme de chiffre !!!")
            return 0
        
        historique = profil_client["historique_credit"]
        if historique ==1 :
              score -= 40
        else :
          score += 20
             
        try :
            age = int(profil_client["age_client"])
            if age >= 25 and age <= 60 :
               score += 10 
        except ValueError :
            print(f"veuiller entrer un age valide !!")
            return 0

        if  score <= 30 :
             print(f"le credit est refusé")
        else :
             pret_max = (revenu * 0.33) * 24
             print(f"nous pouvons vous faire un pret maximum de :{pret_max}")
        return score

client1 = evaluer_profil(profil_client)
print(client1)
