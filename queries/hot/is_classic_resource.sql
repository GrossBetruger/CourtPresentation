DO $$
    DECLARE t_row valid_tests%rowtype; table_count BIGINT = (SELECT count(*) FROM valid_tests); count BIGINT = 1; isClassicResource bool = false;
    BEGIN
        RAISE NOTICE 'Start migration';
        FOR t_row in SELECT * FROM valid_tests LOOP
            IF mod(count, 1000) = 0 THEN
                RAISE NOTICE  'update row %/%', count, table_count;
            END IF;
            isClassicResource := is_classic_resource(t_row.file_name);
            UPDATE valid_tests SET is_classic_resource = isClassicResource WHERE id = t_row.id;
            count := count+1;
        END LOOP;
        RAISE NOTICE 'Finished migration';
    END
$$ LANGUAGE plpgsql;

