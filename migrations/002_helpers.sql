-- Create an idempotent monthly partition
CREATE OR REPLACE FUNCTION create_month_partition(p_month_start DATE)
RETURNS VOID LANGUAGE plpgsql AS $$
DECLARE
    p_month_end DATE := (p_month_start + INTERVAL '1 month')::date;
    part_name TEXT := 'sales_' || to_char(p_month_start, 'YYYY_MM');
    ddl TEXT;
BEGIN
    PERFORM 1
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE c.relname = part_name AND n.nspname = 'public';

    IF NOT FOUND THEN
        ddl := format(
          'CREATE TABLE IF NOT EXISTS %I PARTITION OF sales
           FOR VALUES FROM (%L) TO (%L);',
          part_name, p_month_start, p_month_end
        );
        EXECUTE ddl;

        -- Added index per partition to speed up queries and cover filters and sorts
        EXECUTE format('CREATE INDEX IF NOT EXISTS %I_prod_date ON %I (product_id, sale_date);', part_name || '_idx1', part_name);
        EXECUTE format('CREATE INDEX IF NOT EXISTS %I_region_date ON %I (region_id, sale_date);', part_name || '_idx2', part_name);
        EXECUTE format('CREATE INDEX IF NOT EXISTS %I_date ON %I (sale_date);', part_name || '_idx3', part_name);
    END IF;
END $$;
