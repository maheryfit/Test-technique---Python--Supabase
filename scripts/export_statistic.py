import os
import csv
from supabase import create_client, Client
from db_connect import get_supabase_client
from datetime import datetime, timedelta, timezone

supabase: Client = get_supabase_client()
CSV_PATH = "data/rapport_stats.csv"

def generate_report():
    print("--- 📊 GÉNÉRATION DU RAPPORT STATISTIQUE ---")
    
    try:
        # 1. Appels RPC (Exécution SQL côté serveur)
        print("Interrogation de la base de données via RPC...")
        
        city_stats_response = supabase.rpc('get_city_stats').execute()
        top_agents_response = supabase.rpc('get_top_agents').execute()
        monthly_evo_response = supabase.rpc('get_monthly_evolution').execute()

        city_stats = city_stats_response.data
        top_agents = top_agents_response.data
        monthly_evo = monthly_evo_response.data

        # 2. Affichage en Console
        print("\n=== 🏙️  STATISTIQUES PAR VILLE ===")
        for stat in city_stats:
            print(f"- {stat['city_name'].upper()} : {stat['total_properties']} biens | "
                  f"Moy: {stat['avg_price']}€ | Min: {stat['min_price']}€ | Max: {stat['max_price']}€")

        print("\n=== 🏆 TOP 3 VILLES ===")
        # On prend simplement les 3 premiers de city_stats car le SQL les a déjà triés par DESC
        for stat in city_stats[:3]:
            print(f"🥇 {stat['city_name']} avec {stat['total_properties']} biens")

        print("\n=== 🕵️  TOP 3 AGENTS ===")
        for agent in top_agents:
            print(f"⭐ {agent['agent_name']} : {agent['total_properties']} biens publiés")

        print("\n=== 📅 ÉVOLUTION MENSUELLE (6 derniers mois) ===")
        for month_data in monthly_evo:
            print(f"🗓️ {month_data['publication_month']} : {month_data['total_published']} nouvelles publications")

        # 3. Export CSV
        print(f"\n💾 Exportation des données vers {CSV_PATH}...")
        
        with open(CSV_PATH, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Section Villes
            writer.writerow(["--- STATISTIQUES PAR VILLE ---"])
            writer.writerow(["Ville", "Nombre de biens", "Prix Moyen", "Prix Min", "Prix Max"])
            for stat in city_stats:
                writer.writerow([stat['city_name'], stat['total_properties'], stat['avg_price'], stat['min_price'], stat['max_price']])
                
            writer.writerow([]) # Ligne vide
            
            # Section Agents
            writer.writerow(["--- TOP 3 AGENTS ---"])
            writer.writerow(["Nom de l'agent", "Biens publiés"])
            for agent in top_agents:
                writer.writerow([agent['agent_name'], agent['total_properties']])
                
            writer.writerow([])
            
            # Section Évolution
            writer.writerow(["--- EVOLUTION MENSUELLE ---"])
            writer.writerow(["Mois", "Nouvelles publications"])
            for month_data in monthly_evo:
                writer.writerow([month_data['publication_month'], month_data['total_published']])

        print(f"✅ Rapport généré avec succès dans : {CSV_PATH}")

    except Exception as e:
        print(f"❌ Erreur lors de la génération du rapport : {str(e)}")

if __name__ == "__main__":
    generate_report()