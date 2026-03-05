import os
from collections import defaultdict
from supabase import create_client, Client
from db_connect import get_supabase_client
from datetime import datetime, timedelta, timezone

# Initialisation du client (La service_role key permet de tout lire sans être bloqué par le RLS)
supabase: Client = get_supabase_client()

def audit_database() -> None:
    print("--- 🔍 DÉBUT DE L'AUDIT DE LA BASE DE DONNÉES ---")
    
    try:
        # 1. Récupération de toutes les données avec leur date de création
        print("Téléchargement des données...")
        response = supabase.table('properties').select('*').execute()
        properties = response.data
        
        if not properties:
            print("Aucun bien immobilier n'a été trouvé dans la base.")
            return

        # 2. Préparation pour le calcul des 30 jours
        # On utilise timezone.utc car PostgreSQL stocke les dates en UTC (TIMESTAMPTZ)
        maintenant = datetime.now(timezone.utc)
        limite_30_jours = maintenant - timedelta(days=30)
        
        # 3. Initialisation des compteurs et listes d'anomalies
        stats: dict = {
            "total": len(properties),
            "publies": 0,
            "orphelins": [], # Pour les biens non publiés > 30 jours
            "prix_invalide": [],
            "titre_trop_court": []
        }
        
        groupes_doublons = defaultdict(list)
        
        # 4. Analyse itérative (Un seul passage = O(n) = Très performant)
        for p in properties:
            titre = p.get('title', '')
            ville = p.get('city', '')
            is_published = p.get('is_published', False)
            created_at_str = p.get('created_at')
            price = p.get('price', 0)
            
            # --- A. Statistiques globales ---
            if is_published:
                stats["publies"] += 1
                
            # --- B. Recherche des doublons ---
            cle_doublon = (str(titre).strip().lower(), str(ville).strip().lower())
            groupes_doublons[cle_doublon].append(p['id'])
            
            # --- C. Calcul des jours écoulés depuis la création ---
            jours_ecoules = 0
            if created_at_str:
                try:
                    # Supabase renvoie les dates au format ISO 8601
                    # On remplace le 'Z' par '+00:00' pour compatibilité avec fromisoformat
                    date_creation = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    jours_ecoules = (maintenant - date_creation).days
                    
                    # Recherche des données orphelines (> 30 jours et non publié)
                    if not is_published and date_creation < limite_30_jours:
                        stats["orphelins"].append((p['id'], titre, jours_ecoules))
                except ValueError:
                    print(f"⚠️ Impossible de parser la date pour le bien {p['id']}")

            # --- D. Recherche des données dont le prix est manquant ou négatif ---
            if not price or price <= 0:
                stats["prix_invalide"].append((p['id'], titre, jours_ecoules))
            
            # --- E. Recherche des données dont le titre est trop court ---
            if len(titre) < 5:
                stats["titre_trop_court"].append((p['id'], titre, jours_ecoules))


        # Filtrage pour ne garder que les vrais doublons (plus d'une occurrence)
        vrais_doublons = {cle: ids for cle, ids in groupes_doublons.items() if len(ids) > 1}

        # 5. Affichage du Rapport d'Audit
        print("\n=== 📊 RAPPORT D'AUDIT QUALITÉ ===")
        print(f"Total des annonces en base : {stats['total']}")
        print(f"  - Publiées     : {stats['publies']}")
        print(f"  - Non publiées : {stats['total'] - stats['publies']}")
        
        print("\n=== ⚠️ ANALYSE DES ANOMALIES ===")
        
        # Affichage des doublons
        if vrais_doublons:
            print(f"\n❌ {len(vrais_doublons)} groupe(s) de DOUBLONS détecté(s) :")
            for (t, v), ids in vrais_doublons.items():
                print(f"  -> '{t.title()}' à {v.title()} apparaît {len(ids)} fois.")
        else:
            print("\n✅ Aucun doublon détecté.")
            
        # Affichage des données orphelines (Le fameux point manquant !)
        if stats["orphelins"]:
            print(f"\n👻 {len(stats['orphelins'])} bien(s) ORPHELIN(S) (Non publié depuis > 30 jours) :")
            for id_bien, titre, jours in stats["orphelins"]:
                print(f"  -> [{jours} jours] '{titre}' (ID: {id_bien})")
        else:
            print("\n✅ Aucune donnée orpheline détectée (> 30 jours).")

        # Affichage des données dont le prix est manquant ou négatif
        if stats["prix_invalide"]:
            print(f"\n👻 {len(stats['prix_invalide'])} bien(s) avec un prix invalide :")
            for id_bien, titre, jours in stats["prix_invalide"]:
                print(f"  -> [{jours} jours] '{titre}' (ID: {id_bien})")
        else:
            print("\n✅ Aucune donnée avec un prix invalide.")

        # Affichage des données dont le prix est manquant ou négatif
        if stats["titre_trop_court"]:
            print(f"\n👻 {len(stats['titre_trop_court'])} bien(s) avec un titre trop court :")
            for id_bien, titre, jours in stats["titre_trop_court"]:
                print(f"  -> [{jours} jours] '{titre}' (ID: {id_bien})")
        else:
            print("\n✅ Aucune donnée avec un titre trop court.")

        # 6. RÉSUMÉ GLOBAL (% Propres vs Anomalies)
        # On regroupe tous les IDs impliqués dans une anomalie (Doublons + Orphelins)
        ids_anomalies = set()
        
        # Ajout des IDs des doublons
        for ids in vrais_doublons.values():
            ids_anomalies.update(ids)
            
        # Ajout des IDs des orphelins
        for orphelin in stats["orphelins"]:
            id_bien = orphelin[0] # L'ID est le premier élément du tuple
            ids_anomalies.add(id_bien)
            
        # Calculs des KPIs
        total_anomalies_uniques = len(ids_anomalies)
        biens_propres = stats['total'] - total_anomalies_uniques
        
        pct_propres = (biens_propres / stats['total']) * 100 if stats['total'] > 0 else 0
        pct_anomalies = (total_anomalies_uniques / stats['total']) * 100 if stats['total'] > 0 else 0

        print("\n=== 📈 RÉSUMÉ GLOBAL (KPI) ===")
        print(f"✅ Biens propres : {biens_propres} ({pct_propres:.1f}%)")
        print(f"⚠️ Anomalies     : {total_anomalies_uniques} ({pct_anomalies:.1f}%)")
    
    except Exception as e:
        print(f"❌ Erreur critique lors de l'audit : {str(e)}")

if __name__ == "__main__":
    audit_database()