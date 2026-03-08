"use client";
import { useEffect, useState } from 'react';
import { supabase } from '@/utils/supabase';
import Link from 'next/link';

export default function Home() {
    const [properties, setProperties] = useState<any[]>([]);
    const [cityFilter, setCityFilter] = useState('');
    const [error, setError] = useState<string | null>(null);

    const fetchProperties = async () => {
        try {
            let query = supabase.from('properties').select('*').eq('is_published', true);

            if (cityFilter) {
                query = query.ilike('city', `%${cityFilter}%`);
            }

            const { data, error } = await query;
            if (error) throw error;
            setProperties(data || []);
        } catch (err: any) {
            setError(err.message);
        }
    };

    useEffect(() => {
        fetchProperties();
    }, [cityFilter]);

    return (
        <div className="p-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Biens Immobiliers</h1>
                <Link href="/login" className="text-blue-600 underline">Espace Agent / Connexion</Link>
            </div>

            {error && <p className="text-red-500">{error}</p>}

            <input
                type="text"
                placeholder="Filtrer par ville..."
                value={cityFilter}
                onChange={(e) => setCityFilter(e.target.value)}
                className="border p-2 mb-6 w-full max-w-sm"
            />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {properties.map((p) => (
                    <div key={p.id} className="border p-4 rounded shadow">
                        <h2 className="text-xl font-bold">{p.title}</h2>
                        <p className="text-gray-600">{p.city}</p>
                        <p className="text-green-600 font-bold mt-2">{p.price} €</p>
                    </div>
                ))}
            </div>
        </div>
    );
}