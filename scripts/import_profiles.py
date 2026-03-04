import csv
import os
supabase = get_supabase_client()

# 1. Vos anciens IDs (ceux que vous vouliez forcer et qui sont dans le CSV)
OLD_IDS = {
    "John": "c470f61d-13f5-4dbe-8b3c-7f08cc8e6d11",
    "Jane": "3df9e78c-dd21-40da-a7eb-6522f0599560"
}

# 2. Les données de vos profils
PROFILES_TO_CREATE = [
    {"email": "john.doe@test.com", "password": "Password123!", "role": "agent", "firstname": "John", "lastname": "Doe"},
    {"email": "jane.doe@test.com", "password": "Password123!", "role": "agent", "firstname": "Jane", "lastname": "Doe"},
    {"email": "larry.bird@test.com", "password": "Password123!", "role": "client", "firstname": "Larry", "lastname": "Bird"}
]

def seed_profiles_and_update_csv() -> None:
    new_ids = {}
    
    print("--- 1. CRÉATION DES PROFILS DANS SUPABASE ---")
    for user in PROFILES_TO_CREATE:
        try:
            # Création dans auth.users (Génère l'UUID sécurisé)
            res = supabase.auth.admin.create_user({
                "email": user["email"],
                "password": user["password"],
                "email_confirm": True
            })
            new_id = res.user.id
            new_ids[user["firstname"]] = new_id
            
            # Insertion dans public.profiles
            supabase.table('profiles').insert({
                "id": new_id,
                "role": user["role"],
                "firstname": user["firstname"],
                "lastname": user["lastname"]
            }).execute()
            
            print(f"✅ {user['firstname']} créé avec succès (Nouvel ID : {new_id})")
        except Exception as e:
            print(f"❌ Erreur pour {user['firstname']} : {str(e)}")
            
    # --- 2. MISE À JOUR AUTOMATIQUE DU CSV ---
    csv_path = "data/biens.csv"
    if not os.path.exists(csv_path):
        print(f"\n⚠️ Le fichier {csv_path} n'existe pas encore. L'auto-remplacement est ignoré.")
        return

    print("\n--- 2. MISE À JOUR AUTOMATIQUE DE biens.csv ---")
    try:
        # Lecture du fichier
        with open(csv_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        # Remplacement dynamique
        if "John" in new_ids:
            content = content.replace(OLD_IDS["John"], new_ids["John"])
        if "Jane" in new_ids:
            content = content.replace(OLD_IDS["Jane"], new_ids["Jane"])
            
        # Écriture du fichier mis à jour
        with open(csv_path, 'w', encoding='utf-8') as file:
            file.write(content)
            
        print(f"✅ Le fichier {csv_path} a été mis à jour avec les nouveaux UUIDs !")
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du CSV : {str(e)}")

if __name__ == "__main__":
    seed_profiles_and_update_csv()