liste_parcel = [
    {"id": "zone_A" , "longueur_m":120 , "largueur_m": 80, "production_kg": 4500} ,
    {"id": "zone_B" , "longueur_m":100 , "largueur_m": 40, "production_kg": 500} ,
    {"id": "zone_C" , "longueur_m":80 , "largueur_m": 50, "production_kg": 7200} ,
]

def analyse_rendement(liste_parcel):
    superficie_total_ha = 0
    production_total_t = 0

    for zone in liste_parcel :
        try:
            longueur = float(zone["longueur_m"])
            largueur = float(zone["largueur_m"])
            Production_kg = float(zone["production_kg"])

            superficie_ha = (longueur * largueur)/10000 
            production_t = Production_kg * 1000

            rendement_parcelle = production_t / superficie_ha
            superficie_total_ha += superficie_ha
            production_total_t += production_t
            print(f" {zone['id']} | superficie : {superficie_ha}ha | rendement : {rendement_parcelle } t/ha") 
            
            if rendement_parcelle < 4 :
                print(f" [ATTENTION] rendement trop faible pour la {zone['id']} !")
            
        except Exception : 
            print(f"donnée corumpu pour la zone {zone['id']}")
            continue

    rendement_moy_global = production_t /superficie_total_ha
    return rendement_moy_global

coperative1 = analyse_rendement(liste_parcel)
print("\n ==== BILLAN GLOBAL DE LA COOPERATIVE ====")
print(f"rendement moyen global : {coperative1:.2f} t/ha")