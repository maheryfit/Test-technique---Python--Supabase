"use client";
import { useState } from 'react';
import { supabase } from '@/utils/supabase';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
    const router = useRouter();
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [firstname, setFirstname] = useState('');
    const [lastname, setLastname] = useState('');
    const [role, setRole] = useState('client');
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setMessage(null);

        try {
            if (isLogin) {
                // Connexion
                const { error } = await supabase.auth.signInWithPassword({ email, password });
                if (error) throw error;
                router.push('/');
            } else {
                // Inscription
                const { data, error: signUpError } = await supabase.auth.signUp({ email, password });
                if (signUpError) throw signUpError;

                // Création du profil lié (Note : nécessite une politique RLS d'INSERT sur profiles, ou un trigger SQL)
                if (data.user) {
                    const { error: profileError } = await supabase.from('profiles').insert([
                        { id: data.user.id, firstname, lastname, role }
                    ]);
                    if (profileError) throw profileError;
                }
                setMessage("Compte créé avec succès ! Vous pouvez vous connecter.");
                setIsLogin(true);
            }
        } catch (err: any) {
            setError(err.message); // Affichage de l'erreur utilisateur exigé
        }
    };

    return (
        <div className="p-8 max-w-md mx-auto">
            <h1 className="text-2xl font-bold mb-4">{isLogin ? 'Connexion' : 'Créer un compte'}</h1>
            {error && <div className="bg-red-100 text-red-700 p-2 mb-4 rounded">{error}</div>}
            {message && <div className="bg-green-100 text-green-700 p-2 mb-4 rounded">{message}</div>}

            <form onSubmit={handleAuth} className="flex flex-col gap-4">
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="border p-2" required />
                <input type="password" placeholder="Mot de passe" value={password} onChange={(e) => setPassword(e.target.value)} className="border p-2" required />

                {!isLogin && (
                    <>
                        <input type="text" placeholder="Prénom" value={firstname} onChange={(e) => setFirstname(e.target.value)} className="border p-2" required />
                        <input type="text" placeholder="Nom" value={lastname} onChange={(e) => setLastname(e.target.value)} className="border p-2" required />
                        <select value={role} onChange={(e) => setRole(e.target.value)} className="border p-2">
                            <option value="client">Client</option>
                            <option value="agent">Agent Immobilier</option>
                        </select>
                    </>
                )}

                <button type="submit" className="bg-blue-600 text-white p-2 rounded">
                    {isLogin ? 'Se connecter' : 'S\'inscrire'}
                </button>
            </form>
            <button onClick={() => setIsLogin(!isLogin)} className="mt-4 text-blue-600 underline">
                {isLogin ? "Pas encore de compte ? S'inscrire" : "Déjà un compte ? Se connecter"}
            </button>
        </div>
    );
}