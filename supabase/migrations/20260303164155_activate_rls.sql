-- Activation du RLS (si ce n'est pas déjà fait)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Règle SELECT : Utilisateur connecté 
CREATE POLICY "Voir son propre profil"
ON public.profiles
FOR SELECT
USING ( (select auth.uid()) = id);

-- Règle UPDATE : Utilisateur connecté 
CREATE POLICY "Modifier son propre profil"
ON public.profiles
FOR UPDATE
TO authenticated
USING ( (select auth.uid()) = id)
WITH CHECK ( (select auth.uid()) = id);

ALTER TABLE public.properties ENABLE ROW LEVEL SECURITY;

-- Règle SELECT 2 : Les agents voient tous leurs biens 
CREATE POLICY "Lecture de ses propres biens (Agent)"
ON public.properties
FOR SELECT
TO authenticated
USING (agent_id = (select auth.uid()));

-- Règle INSERT : Agent uniquement [cite: 29]
CREATE POLICY "Insertion de ses propres biens"
ON public.properties
FOR INSERT
TO authenticated
WITH CHECK (agent_id = (select auth.uid()));

-- Règle UPDATE : Agent (ses biens) [cite: 29]
CREATE POLICY "Modification de ses propres biens"
ON public.properties
FOR UPDATE
TO authenticated
USING (agent_id = (select auth.uid()))
WITH CHECK (agent_id = (select auth.uid()));

-- Règle DELETE : Agent (ses biens) [cite: 29]
CREATE POLICY "Suppression de ses propres biens"
ON public.properties
FOR DELETE
TO authenticated
USING (agent_id = (select auth.uid()));
