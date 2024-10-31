# List of queries user can select from dropdown list
query_dict = {
    "Query 1": ("""\
        SELECT s.s_name, n.n_name
        FROM public.supplier s
        INNER JOIN public.nation n ON s.s_nationkey = n.n_nationkey;
    """),
    "Query 2":( """\
        SELECT p_name, p_retailprice
        FROM public.part
        WHERE p_retailprice > 950;
    """),
    "Query 3": ("""\
        SELECT AVG(s_acctbal) AS avg_acctbal
        FROM public.supplier;
    """),
    "Query 4": ("""\
        SELECT p_name, p_retailprice
        FROM public.part
        ORDER BY p_retailprice DESC
        LIMIT 10;
    """),
    "Query 5": ("""\
        SELECT p.p_name, s.s_name, l.l_quantity
        FROM public.part p
        INNER JOIN public.lineitem l ON p.p_partkey = l.l_partkey
        INNER JOIN public.supplier s ON l.l_suppkey = s.s_suppkey
        WHERE l.l_shipdate BETWEEN '1994-01-01' AND '1995-01-01'
        AND p.p_size > 20
        AND s.s_acctbal > 5000
        ORDER BY l.l_quantity DESC;
    """),
    "Query 6": ("""\
        SELECT n_name, o_year, SUM(amount) AS sum_profit
        FROM (
            SELECT n_name, DATE_PART('YEAR', o_orderdate) AS o_year, l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity AS amount
            FROM part, supplier, lineitem, partsupp, orders, nation
            WHERE s_suppkey = l_suppkey
                AND ps_suppkey = l_suppkey
                AND ps_partkey = l_partkey
                AND p_partkey = l_partkey
                AND o_orderkey = l_orderkey
                AND s_nationkey = n_nationkey
                AND p_name LIKE '%green%'
                AND s_acctbal > 10
                AND ps_supplycost > 100
        ) AS profit
        GROUP BY n_name, o_year
        ORDER BY n_name, o_year DESC;
    """),
    "Query 7": ("""\
        SELECT c_custkey, c_name, SUM(l_extendedprice * (1 - l_discount)) as revenue, c_acctbal, n_name, c_address, c_phone, c_comment
        FROM customer, orders, lineitem, nation
        WHERE c_custkey = o_custkey
            AND l_orderkey = o_orderkey
            AND o_orderdate >= '1993-10-01'
            AND o_orderdate < '1994-01-01'
            AND c_nationkey = n_nationkey
            AND c_acctbal > 10
            AND l_extendedprice > 100
        GROUP BY c_custkey, c_name, c_acctbal, c_phone, n_name, c_address, c_comment
        ORDER BY revenue desc;
    """),
    "Query 8": ("""\
        SELECT o_orderpriority, count(*) as order_count
        FROM orders
        WHERE o_totalprice > 100 AND EXISTS (
            SELECT *
            FROM lineitem
            WHERE l_orderkey = o_orderkey AND l_extendedprice > 100
            )
        GROUP BY o_orderpriority
        ORDER BY o_orderpriority;
    """),
    "Query 9": ("""\
        SELECT l_orderkey, sum(l_extendedprice * (1 - l_discount)) as revenue, o_orderdate, o_shippriority
        FROM customer, orders, lineitem
        WHERE c_mktsegment = 'BUILDING'
            AND c_custkey = o_custkey
            AND l_orderkey = o_orderkey
            AND o_totalprice > 10
            AND l_extendedprice > 10
        GROUP By l_orderkey, o_orderdate, o_shippriority
        ORDER BY revenue desc, o_orderdate;
    """),
    "Query 10": ("""\
        SELECT l_returnflag, l_linestatus, SUM(l_quantity) as sum_qty, SUM(l_extendedprice) as sum_base_price, SUM(l_extendedprice * (1 - l_discount)) as sum_disc_price, SUM(l_extendedprice * (1 - l_discount) * (1 + l_tax)) as sum_charge, AVG(l_quantity) as avg_qty, AVG(l_extendedprice) as avg_price, AVG(l_discount) as avg_disc, COUNT(*) as count_order
        FROM lineitem
        WHERE l_extendedprice > 100
        GROUP BY l_returnflag, l_linestatus
        ORDER BY l_returnflag, l_linestatus;
    """),
    "Query 11": ("""\
        SELECT o_year, SUM(CASE WHEN nation = 'BRAZIL' THEN volume ELSE 0 END) / SUM(volume) as mkt_share
        FROM (
            SELECT DATE_PART('YEAR',o_orderdate) as o_year, l_extendedprice * (1 - l_discount) as volume, n2.n_name as nation
            FROM part, supplier, lineitem, orders, customer, nation n1, nation n2, region
            WHERE p_partkey = l_partkey
            AND s_suppkey = l_suppkey
            AND l_orderkey = o_orderkey
            AND o_custkey = c_custkey
            AND c_nationkey = n1.n_nationkey
            AND n1.n_regionkey = r_regionkey
            AND r_name = 'AMERICA'
            AND s_nationkey = n2.n_nationkey
            AND o_orderdate between '1995-01-01' and '1996-12-31'
            AND p_type = 'ECONOMY ANODIZED STEEL'
            AND s_acctbal > 10
            AND l_extendedprice > 100
      ) as all_nations
        GROUP BY o_year
        ORDER BY o_year;
    """),
    "Query 12": ("""\
        SELECT n_name, sum(l_extendedprice * (1 - l_discount)) as revenue
        FROM customer, orders, lineitem, supplier, nation, region
        WHERE c_custkey = o_custkey
            AND l_orderkey = o_orderkey
            AND l_suppkey = s_suppkey
            AND c_nationkey = s_nationkey
            AND s_nationkey = n_nationkey
            AND n_regionkey = r_regionkey
            AND r_name = 'ASIA'
            AND o_orderdate >= '1994-01-01'
            AND o_orderdate < '1995-01-01'
            AND c_acctbal > 10
            AND s_acctbal > 20
        GROUP BY n_name
        ORDER BY revenue DESC;
    """),
    "Query 13": ("""\
        SELECT sum(l_extendedprice * l_discount) as revenue
        FROM lineitem
        WHERE l_extendedprice > 100;
    """),
    "Query 14": ("""\
        SELECT supp_nation, cust_nation, l_year, sum(volume) as revenue
        FROM (
            SELECT n1.n_name as supp_nation, n2.n_name as cust_nation, DATE_PART('YEAR', l_shipdate) as l_year, l_extendedprice * (1 - l_discount) as volume
            FROM supplier, lineitem, orders, customer, nation n1, nation n2
            WHERE s_suppkey = l_suppkey
                AND o_orderkey = l_orderkey
                AND c_custkey = o_custkey
                AND s_nationkey = n1.n_nationkey
                AND c_nationkey = n2.n_nationkey
                AND (
                    (n1.n_name = 'FRANCE' AND n2.n_name = 'GERMANY')
                    OR (n1.n_name = 'GERMANY' AND n2.n_name = 'FRANCE')
                )
                AND l_shipdate BETWEEN '1995-01-01' AND '1996-12-31'
                AND o_totalprice > 100
                AND c_acctbal > 10
        ) as shipping
        GROUP BY supp_nation, cust_nation, l_year
        ORDER BY supp_nation, cust_nation, l_year;
    """),
    "Query 15": ("""\
        SELECT ps_partkey, sum(ps_supplycost * ps_availqty) as value
        FROM partsupp, supplier, nation
        WHERE ps_suppkey = s_suppkey
            AND s_nationkey = n_nationkey
            AND n_name = 'GERMANY'
            AND ps_supplycost > 20
            AND s_acctbal > 10
        GROUP BY ps_partkey
        HAVING sum(ps_supplycost * ps_availqty) > (
            SELECT sum(ps_supplycost * ps_availqty) * 0.0001000000
            FROM partsupp, supplier, nation
            WHERE ps_suppkey = s_suppkey
                AND s_nationkey = n_nationkey
                AND n_name = 'GERMANY'
        )
        ORDER BY value DESC;
    """),
}
