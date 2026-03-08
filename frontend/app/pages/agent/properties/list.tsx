"use client";
import { useEffect, useState } from 'react';
import { supabase } from '@/utils/supabase';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function AgentDashboard() {
    const router = useRouter();
    const [properties, setProperties] = useState<any[]>([]);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        checkUserAndFetch();
    }, []);

    const checkUserAndFetch = async () => {
        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return router.push('/login');

        // Vérification du rôle (Redirection si non agent)
        const { data: profile } = await supabase.from('profiles').select('role').eq('id', user.id).single();
        if (profile?.role !== 'agent') {
            return router.push('/login');
        }

        // Le RLS garantit que l'agent ne reçoit que ses propres biens
        const { data, error } = await supabase.from('properties').select('*');
        if (error) setError(error.message);
        else setProperties(data || []);
    };

    const togglePublish = async (id: string, currentStatus: boolean) => {
        const { error } = await supabase.from('properties').update({ is_published: !currentStatus }).eq('id', id);
        if (error) setError(error.message);
        else checkUserAndFetch();
    };

    const deleteProperty = async (id: string) => {
        const { error } = await supabase.from('properties').delete().eq('id', id);
        if (error) setError(error.message);
        else checkUserAndFetch();
    };

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Mes Biens (Espace Agent)</h1>
                <Link href="/agent/properties/new" className="bg-blue-600 text-white px-4 py-2 rounded">Créer un bien</Link>
            </div>

            {error && <p className="text-red-500 mb-4">{error}</p>}

            <table className="w-full text-left border-collapse">
                <thead>
                    <tr className="border-b bg-gray-50">
                        <th className="p-2">Titre</th>
                        <th className="p-2">Ville</th>
                        <th className="p-2">Statut</th>
                        <th className="p-2">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {properties.map((p) => (
                        <tr key={p.id} className="border-b">
                            <td className="p-2">{p.title}</td>
                            <td className="p-2">{p.city}</td>
                            <td className="p-2">{p.is_published ? '🟢 Publié' : '🔴 Brouillon'}</td>
                            <td className="p-2 flex gap-2">
                                <button onClick={() => togglePublish(p.id, p.is_published)} className="text-blue-600 underline">
                                    {p.is_published ? 'Masquer' : 'Publier'}
                                </button>
                                <button onClick={() => deleteProperty(p.id)} className="text-red-600 underline">Supprimer</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}