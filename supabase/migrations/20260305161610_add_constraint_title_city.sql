ALTER TABLE public.properties
ADD CONSTRAINT properties_title_city_key UNIQUE (title, city);