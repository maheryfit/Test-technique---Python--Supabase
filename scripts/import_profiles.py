from db_connect import get_supabase_client
# Récupération du client (Assurez-vous qu'il utilise bien la SERVICE_ROLE KEY !)
supabase = get_supabase_client()

# Les données des profils avec emails et mots de passe obligatoires pour l'Auth
PROFILES_TO_CREATE = [
    {"email": "agent.john@test.com", "password": "Password123!", "role": "agent", "firstname": "John", "lastname": "Doe"},
    {"email": "agent.jane@test.com", "password": "Password123!", "role": "agent", "firstname": "Jane", "lastname": "Doe"},
    {"email": "client.larry@test.com", "password": "Password123!", "role": "client", "firstname": "Larry", "lastname": "Bird"}
]

def seed_profiles() -> None:
    print("--- CRÉATION DES PROFILS DANS SUPABASE ---")
    
    for user in PROFILES_TO_CREATE:
        try:            
            # 1. On crée d'abord le compte dans l'authentification pour avoir un vrai ID
            auth_response = supabase.auth.admin.create_user({
                "email": user["email"],
                "password": user["password"],
                "email_confirm": True
            })
            
            vrai_id_supabase = auth_response.user.id
            
            # 2. On insère dans public.profiles avec ce VRAI ID
            supabase.table('profiles').insert({
                "id": vrai_id_supabase,
                "role": user["role"],
                "firstname": user["firstname"],
                "lastname": user["lastname"]
            }).execute()
            
            print(f"✅ {user['firstname']} créé avec succès (Nouvel ID : {vrai_id_supabase})")
            
        except Exception as e:
            print(f"❌ Erreur pour {user['firstname']} : {str(e)}")
            
if __name__ == "__main__":
    seed_profiles()