DO $$
    DECLARE t_row valid_tests%rowtype; table_count BIGINT = (SELECT count(*) FROM valid_tests); count BIGINT = 1; isMixedHot bool = false;
    BEGIN
        RAISE NOTICE 'Start migration';
        FOR t_row in SELECT * FROM valid_tests LOOP
            IF mod(count, 1000) = 0 THEN
                RAISE NOTICE  'update row %/%', count, table_count;
            END IF;
            isMixedHot := t_row.pure_hot = false AND (t_row.infrastructure = 'HOT' OR t_row.isp = 'Hot-Net internet services Ltd.');
            UPDATE valid_tests SET mixed_hot = isMixedHot WHERE id = t_row.id AND valid_tests.pure_hot != true;
            count := count+1;
        END LOOP;
        RAISE NOTICE 'Finished migration';
    END
$$ LANGUAGE plpgsql;

