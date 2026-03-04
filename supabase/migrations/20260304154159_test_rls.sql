-- ==============================================================================
-- TEST RLS : VALIDATION DES ACCÈS AGENTS ET CLIENTS
-- ==============================================================================
BEGIN; -- Début de la transaction (tout sera annulé à la fin)

-- 1. DÉSACTIVATION TEMPORAIRE DES CONTRAINTES (Pour faciliter le mock des données)
-- Cela évite de devoir créer de vrais utilisateurs dans auth.users pour ce test rapide
SET LOCAL session_replication_role = 'replica';

-- 2. INSERTION DES DONNÉES DE TEST (Mock)
-- Création de 2 agents et 1 client dans la table profiles
INSERT INTO public.profiles (id, role, firstname, lastname) VALUES
('c470f61d-13f5-4dbe-8b3c-7f08cc8e6d11', 'agent', 'John', 'Doe'),
('3df9e78c-dd21-40da-a7eb-6522f0599560', 'agent', 'Jane', 'Doe'),
('900f85e0-50f6-4db0-8826-834af2e86e69', 'client', 'Larry', 'Bird');

-- Création de 3 biens immobiliers dans la table properties
INSERT INTO public.properties (id, title, city, price, agent_id, is_published) VALUES
('af541147-09af-489f-8722-ab205f2e1f92', 'Villa Publiée (Agent John)', 'Paris', 500000, 'c470f61d-13f5-4dbe-8b3c-7f08cc8e6d11', true),
('0ed08be6-4541-4d83-ae20-e81777225949', 'Studio Caché (Agent John)', 'Lyon', 100000, 'c470f61d-13f5-4dbe-8b3c-7f08cc8e6d11', false),
('acb601da-874a-4237-9f34-d9105e1c195f', 'Maison Cachée (Agent Jane)', 'Marseille', 300000, '3df9e78c-dd21-40da-a7eb-6522f0599560', true);

-- Réactivation des contraintes
SET LOCAL session_replication_role = 'origin';

-- ==============================================================================
-- EXÉCUTION DES TESTS
-- ==============================================================================

-- On passe en mode "utilisateur connecté" (contourne le rôle postgres superuser)
SET LOCAL ROLE authenticated;

-- --- TEST 1 : SIMULATION DU CLIENT ---
-- On injecte l'ID du Client C dans le JWT simulé
SELECT set_config('request.jwt.claims', '{"sub": "900f85e0-50f6-4db0-8826-834af2e86e69", "role": "authenticated"}', true);

-- Affichage en console : Le client ne doit voir QUE la 'Villa Publiée (Agent A)'
SELECT '--- VUE CLIENT (Ne doit voir que la Villa Publiée) ---' AS etape_du_test;
SELECT id, title, is_published FROM public.properties;
-- Note: Dans le SQL Editor Supabase, les résultats d'un SELECT dans un bloc BEGIN non renvoyé explicitement 
-- peuvent être masqués. On utilise une table temporaire pour contourner ça si besoin, 
-- ou on exécute simplement les requêtes l'une après l'autre.

-- --- TEST 2 : SIMULATION DE L'AGENT A ---
-- On injecte l'ID de l'Agent A dans le JWT simulé
SELECT set_config('request.jwt.claims', '{"sub": "c470f61d-13f5-4dbe-8b3c-7f08cc8e6d11", "role": "authenticated"}', true);

-- Affichage en console : L'Agent A doit voir la 'Villa Publiée' (car publiée) 
-- ET le 'Studio Caché' (car c'est le sien). Il NE VOIT PAS la 'Maison Cachée (Agent B)'.
SELECT '--- VUE AGENT A (Doit voir Villa Publiée ET Studio Caché, mais pas la Maison de l''Agent B) ---' AS etape_du_test;
SELECT id, title, is_published, agent_id FROM public.properties;

ROLLBACK; -- Nettoyage : On annule toutes les insertions