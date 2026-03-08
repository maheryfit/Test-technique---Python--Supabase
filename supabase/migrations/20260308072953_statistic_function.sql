-- 1. Fonction pour les statistiques par ville
CREATE OR REPLACE FUNCTION get_city_stats()
RETURNS TABLE (
    city_name TEXT, 
    total_properties BIGINT, 
    avg_price NUMERIC, 
    min_price NUMERIC, 
    max_price NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        city::TEXT as city_name,
        COUNT(id) as total_properties,
        ROUND(AVG(price)::numeric, 2) as avg_price,
        MIN(price)::numeric as min_price,
        MAX(price)::numeric as max_price
    FROM public.properties
    WHERE is_published = true
    GROUP BY city
    ORDER BY total_properties DESC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 2. Fonction pour le Top 3 des agents
CREATE OR REPLACE FUNCTION get_top_agents()
RETURNS TABLE (
    agent_name TEXT, 
    total_properties BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (prof.firstname || ' ' || prof.lastname)::TEXT as agent_name,
        COUNT(prop.id) as total_properties
    FROM public.properties prop
    JOIN public.profiles prof ON prop.agent_id = prof.id
    WHERE prop.is_published = true
    GROUP BY prof.id, prof.firstname, prof.lastname
    ORDER BY total_properties DESC
    LIMIT 3;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. BONUS : Fonction pour l'évolution mensuelle (6 derniers mois)
CREATE OR REPLACE FUNCTION get_monthly_evolution()
RETURNS TABLE (
    publication_month TEXT, 
    total_published BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        to_char(created_at, 'YYYY-MM')::TEXT as publication_month,
        COUNT(id) as total_published
    FROM public.properties
    WHERE is_published = true 
      AND created_at >= NOW() - INTERVAL '6 months'
    GROUP BY publication_month
    ORDER BY publication_month ASC;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;