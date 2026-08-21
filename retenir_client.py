liste_client = [
    {"nom": "anatole" , "nombre_achat":20 , "nombre_jour_inactif": 5 , "note_client" : 3},
    {"nom": "serges" , "nombre_achat":7 , "nombre_jour_inactif": 3 , "note_client" : 1.5},
    {"nom": "deric" , "nombre_achat":15 , "nombre_jour_inactif": 13 , "note_client" : 2.4}
]

def analyser_fidelite(liste_client):
    note_global = 0
    nbre_clients = 0
    for clients in liste_client : 
        try:
            nbre__achat = int(clients["nombre_achat"])
            nbre_jour_inactif = int(clients["nombre_jour_inactif"])
            note = float(clients["note_client"])

            if nbre__achat > 10 and note >= 4.0 :
                print(f"[TOP] le client: {clients["nom"]} est un ambassadeur tres fidele.")
            if nbre_jour_inactif >= 30 or note < 2.5 :
                print(f"[ALERTE CRITIQUE] le client: {clients["nom"]} risque de nous quitter !")
            
            nbre_clients += 1
            note_global += note
            note_moy_global = note_global/nbre_clients
        
        except ValueError:
            print(f"veuiller entrez les donnnées corects !!")
    return f"la note moyenne de satisfaction globale est : {note_moy_global:.2f} points"

client1 = analyser_fidelite(liste_client)
print(client1)