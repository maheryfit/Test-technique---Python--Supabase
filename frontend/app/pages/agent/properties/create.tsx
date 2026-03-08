"use client";
import { useState } from 'react';
import { supabase } from '@/utils/supabase';
import { useRouter } from 'next/navigation';

export default function NewProperty() {
    const router = useRouter();
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [price, setPrice] = useState('');
    const [city, setCity] = useState('');
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);

        const { data: { user } } = await supabase.auth.getUser();
        if (!user) return router.push('/login');

        const { error: insertError } = await supabase.from('properties').insert([
            {
                title,
                description,
                price: parseFloat(price),
                city,
                agent_id: user.id // Obligatoire selon la contrainte SQL
            }
        ]);

        if (insertError) {
            setError(insertError.message);
        } else {
            router.push('/agent/properties');
        }
    };

    return (
        <div className="p-8 max-w-lg mx-auto">
            <h1 className="text-2xl font-bold mb-4">Créer une nouvelle annonce</h1>

            {error && <div className="bg-red-100 text-red-700 p-2 mb-4 rounded">{error}</div>}

            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                <input type="text" placeholder="Titre (min 5 caractères)" value={title} onChange={(e) => setTitle(e.target.value)} className="border p-2" required minLength={5} />
                <textarea placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} className="border p-2" rows={4} />
                <input type="number" placeholder="Prix (€)" value={price} onChange={(e) => setPrice(e.target.value)} className="border p-2" required min="1" />
                <input type="text" placeholder="Ville" value={city} onChange={(e) => setCity(e.target.value)} className="border p-2" required />

                <div className="flex gap-2">
                    <button type="submit" className="bg-blue-600 text-white p-2 rounded flex-1">Enregistrer le bien</button>
                    <button type="button" onClick={() => router.back()} className="bg-gray-300 p-2 rounded flex-1">Annuler</button>
                </div>
            </form>
        </div>
    );
}