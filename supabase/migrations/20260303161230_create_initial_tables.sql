-- Création de la table profiles
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('agent', 'client')),
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE public.properties (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL CHECK (length(title) >= 5),
    description TEXT,
    price NUMERIC(12, 2) NOT NULL CHECK (price > 0),
    city TEXT NOT NULL,
    agent_id UUID NOT NULL REFERENCES public.profiles(id),
    is_published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT now()
);