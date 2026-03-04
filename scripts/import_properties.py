import csv
import os
from supabase import create_client, Client

from db_connect import get_supabase_client

supabase = get_supabase_client()

def validate_row(row: dict) -> tuple[bool, str]:
    """
    Valide une ligne du CSV selon les règles métier.
    Retourne (True, "") si valide, (False, "Raison") sinon.
    """
    title = row.get('title', '').strip()
    city = row.get('city', '').strip()
    price_str = row.get('price', '0')
    
    # 1. Validation du titre (non vide, >= 5 caractères)
    if len(title) < 5:
        return False, f"Titre trop court ou vide ('{title}')"
    
    # 2. Validation de la ville (non vide)
    if not city:
        return False, "La ville est vide"
    
    # 3. Validation du prix (doit être un nombre > 0)
    try:
        price = float(price_str)
        if price <= 0:
            return False, f"Prix invalide ou négatif ({price})"
    except ValueError:
        return False, f"Format de prix invalide ('{price_str}')"
        
    # Si toutes les vérifications passent
    return True, ""

def import_csv(filepath: str) -> None:
    """
    Lit le fichier CSV, valide chaque ligne et l'insère dans Supabase.
    """
    print(f"--- DÉBUT DE L'IMPORTATION : {filepath} ---")
    
    stats = {
        "total": 0,
        "inserted": 0,
        "rejected": 0
    }
    rejections = []

    try:
        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                stats["total"] += 1
                
                # 1. Validation métier
                is_valid, reason = validate_row(row)
                
                if not is_valid:
                    stats["rejected"] += 1
                    rejections.append(f"Ligne {stats['total']} rejetée : {reason}")
                    continue
                
                # 2. Préparation du payload (Cast des données)
                # Le CSV renvoie des chaînes de caractères, PostgreSQL s'attend à des types précis
                payload = {
                    "title": row['title'].strip(),
                    "price": float(row['price']),
                    "city": row['city'].strip(),
                    "agent_id": row['agent_id'].strip(),
                    "is_published": str(row.get('is_published', '')).strip().lower() in ['true', '1', 'yes']
                }
                
                # 3. Insertion via l'API Supabase
                try:
                    # Note technique : Supabase REST API intercepte l'insertion.
                    supabase.table('properties').insert(payload).execute()
                    stats["inserted"] += 1
                except Exception as e:
                    stats["rejected"] += 1
                    rejections.append(f"Ligne {stats['total']} rejetée (Erreur API) : {str(e)}")

    except FileNotFoundError:
        print(f"Erreur critique : Le fichier {filepath} est introuvable.")
        return

    # 4. Affichage du rapport final
    print("\n=== RAPPORT FINAL D'IMPORTATION ===")
    print(f"Lignes traitées : {stats['total']}")
    print(f"Lignes insérées : {stats['inserted']}")
    print(f"Lignes rejetées : {stats['rejected']}")
    
    if rejections:
        print("\n--- Détail des rejets ---")
        for r in rejections:
            print(f"- {r}")

if __name__ == "__main__":
    # Assurez-vous que le dossier 'data' et le fichier existent
    import_csv("data/biens.csv")