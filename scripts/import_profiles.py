from db_connect import get_supabase_client
import csv

supabase = get_supabase_client()

# Nos données de test
USERS_TO_CREATE = [
    {
        "email": "agent.john@test.com",
        "password": "Password123!",
        "role": "agent",
        "firstname": "John",
        "lastname": "Doe"
    },
    {
        "email": "agent.jane@test.com",
        "password": "Password123!",
        "role": "agent",
        "firstname": "Jane",
        "lastname": "Smith"
    },
    {
        "email": "client.larry@test.com",
        "password": "Password123!",
        "role": "client",
        "firstname": "Larry",
        "lastname": "Bird"
    }
]

def seed_profiles() -> dict:
    print("--- DÉBUT DE LA CRÉATION DES PROFILS ---")
    generated_ids = {}

    for u in USERS_TO_CREATE:
        print(f"Création de l'utilisateur : {u['email']}...")
        try:
            # 1. Création dans auth.users (GoTrue)
            auth_response = supabase.auth.admin.create_user({
                "email": u["email"],
                "password": u["password"],
                "email_confirm": True # Auto-valide l'email pour le test
            })
            
            new_user_id = auth_response.user.id
            generated_ids[u["firstname"]] = new_user_id
            
            # 2. Création du profil lié dans public.profiles
            profile_payload = {
                "id": new_user_id,
                "role": u["role"],
                "firstname": u["firstname"],
                "lastname": u["lastname"]
            }
            supabase.table('profiles').insert(profile_payload).execute()
            
            print(f"✅ Succès ! ID généré : {new_user_id}")
            
        except Exception as e:
            # Si l'utilisateur existe déjà, l'API renverra une erreur
            print(f"❌ Erreur pour {u['email']} : {str(e)}")

    return generated_ids

if __name__ == "__main__":
    ids = seed_profiles()
    
    print("\n=== RÉSUMÉ DES UUIDs GÉNÉRÉS (À copier dans votre CSV) ===")
    for name, uid in ids.items():
        if name in ["John", "Jane"]: # On n'affiche que les agents pour le CSV
            print(f"Agent {name} : {uid}")