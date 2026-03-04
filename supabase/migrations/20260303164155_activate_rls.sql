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

-- Règle SELECT
CREATE POLICY "Lecture des biens selon le role"
ON public.properties
FOR SELECT
-- On ne met pas "TO authenticated" ici, car cette règle doit aussi gérer les visiteurs anonymes (auth.uid() IS NULL)
USING (
    -- CAS 1 : Visiteur anonyme OU Client connecté -> Voit uniquement les biens publiés
    (
        is_published = true 
        AND (
            auth.uid() IS NULL 
            OR (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'client'
        )
    )
    OR
    -- CAS 2 : Agent connecté -> Voit uniquement ses propres biens
    (
        agent_id = (select auth.uid())
        AND (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'agent'
    )
);

-- Règle INSERT : Agent uniquement 
CREATE POLICY "Insertion de ses propres biens"
ON public.properties
FOR INSERT
TO authenticated
WITH CHECK (
    agent_id = (select auth.uid())
    AND (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'agent'
);

-- Règle UPDATE : Agent (ses biens) 
CREATE POLICY "Modification de ses propres biens"
ON public.properties
FOR UPDATE
TO authenticated
USING (
    agent_id = (select auth.uid())
    AND (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'agent'
)
WITH CHECK (
    agent_id = (select auth.uid())
    AND (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'agent'
);

-- Règle DELETE : Agent (ses biens) 
CREATE POLICY "Suppression de ses propres biens"
ON public.properties
FOR DELETE
TO authenticated
USING (
    agent_id = (select auth.uid())
    AND (SELECT role FROM public.profiles WHERE id = (select auth.uid())) = 'agent'
);
