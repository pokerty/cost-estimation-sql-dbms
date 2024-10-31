import json

class QEPNode:
    def __init__(self, query_plan, node_type, relation_name, startup_cost, total_cost, plan_rows, plan_width, actual_startup_time, actual_total_time, actual_rows, actual_loops, output, index_cond, filter, rows_removed, hash_cond, merge_cond, join_type, sort_method, sort_key, sort_space_used, hash_buckets, strategy, group_key, shared_hit_blocks, shared_read_blocks, shared_dirtied_blocks, shared_written_blocks, local_hit_blocks, local_read_blocks, local_dirtied_blocks, local_written_blocks, temp_read_blocks, temp_written_blocks):

        self.query_plan = query_plan
        self.node_type = node_type
        self.relation_name = relation_name
        self.startup_cost = startup_cost
        self.total_cost = total_cost
        self.plan_rows = plan_rows
        self.plan_width = plan_width
        self.actual_startup_time = actual_startup_time
        self.actual_total_time = actual_total_time
        self.actual_rows = actual_rows
        self.actual_loops = actual_loops
        self.output = output
        self.index_cond = index_cond
        self.filter = filter
        self.rows_removed = rows_removed
        self.hash_cond = hash_cond
        self.merge_cond = merge_cond
        self.join_type = join_type
        self.sort_method = sort_method
        self.sort_key = sort_key
        self.sort_space_used = sort_space_used
        self.hash_buckets = hash_buckets
        self.strategy = strategy
        self.group_key = group_key
        self.shared_hit_blocks = shared_hit_blocks
        self.shared_read_blocks = shared_read_blocks
        self.shared_dirtied_blocks = shared_dirtied_blocks
        self.shared_written_blocks = shared_written_blocks
        self.local_hit_blocks = local_hit_blocks
        self.local_read_blocks = local_read_blocks
        self.local_dirtied_blocks = local_dirtied_blocks
        self.local_written_blocks = local_written_blocks
        self.temp_read_blocks = temp_read_blocks
        self.temp_written_blocks = temp_written_blocks
        self.children = []  # List of child nodes


def analyze_and_explain(qep):
    """
    This function takes a Query Execution Plan (QEP) and returns an explanation of 
    the cost estimates associated with that QEP.
    """
    # Parse the QEP into a structured format (such as a dictionary or custom object)
    qep = parse_qep(qep)
    
    graph = build_graph(qep)

    # Analyze the parsed QEP
    explanation = analyze_graph(graph)

    return explanation


def parse_qep(qep):
    """
    Parses the QEP into a more structured format for analysis.
    """
    # Get values from json
    json_portion = qep[0][0]
    json_string = json.dumps(json_portion, indent=2)
    qep_json = json.loads(json_string)
    return qep_json


def build_graph(qep):
    """
    Creates QEP graph using parsed QEP statement for traversal.
    """
    def create_node(plan):

        # Attributes not necessarily found in every operation
        if "Relation Name" in plan:
            relation_name = plan["Relation Name"]
        else: 
            relation_name = None


        if "Output" in plan:
            output = plan["Output"]
        else: 
            output = None


        if "Index Cond" in plan:
            index_cond = plan["Index Cond"]
        else:
            index_cond = None


        if "Filter" in plan:
            filter = plan["Filter"]
        else:
            filter = None


        if "Rows Removed by Filter" in plan:
            rows_removed = plan["Rows Removed by Filter"]
        else: 
            rows_removed = None


        if "Hash Cond" in plan:
            hash_cond = plan["Hash Cond"]
        else:
            hash_cond = None


        if "Merge Cond" in plan:
            merge_cond = plan["Merge Cond"]
        else: 
            merge_cond = None


        if "Join Type" in plan:
            join_type = plan["Join Type"]
        else: 
            join_type = None


        if "Sort Method" in plan:
            sort_method = plan["Sort Method"]
        else:
            sort_method = None


        if "Sort Key" in plan:
            sort_key = plan["Sort Key"]
        else:
            sort_key = None


        if "Sort Space Used" in plan:
            sort_space_used = plan["Sort Space Used"]
        else:
            sort_space_used = None


        if "Hash Buckets" in plan:
            hash_buckets = plan["Hash Buckets"]
        else:
            hash_buckets = None


        if "Strategy" in plan:
            strategy = plan["Strategy"]
        else:
            strategy = None


        if "Group Key" in plan:
            group_key = plan["Group Key"]
        else: 
            group_key = None

        
    
        return QEPNode(
            query_plan = plan,
            node_type = plan["Node Type"],
            relation_name = relation_name,
            startup_cost = plan["Startup Cost"],
            total_cost = plan["Total Cost"],
            plan_rows = plan["Plan Rows"],
            plan_width = plan["Plan Width"],
            actual_startup_time = plan["Actual Startup Time"],
            actual_total_time = plan["Actual Total Time"],
            actual_rows = plan["Actual Rows"],
            actual_loops = plan["Actual Loops"],
            output = output,
            index_cond = index_cond,
            filter = filter,
            rows_removed = rows_removed,
            hash_cond = hash_cond,
            merge_cond = merge_cond,
            join_type = join_type,
            sort_method = sort_method,
            sort_key = sort_key,
            sort_space_used = sort_space_used,
            hash_buckets = hash_buckets, 
            strategy = strategy,
            group_key = group_key,
            shared_hit_blocks = plan["Shared Hit Blocks"],
            shared_read_blocks = plan["Shared Read Blocks"],
            shared_dirtied_blocks = plan["Shared Dirtied Blocks"],
            shared_written_blocks = plan["Shared Written Blocks"],
            local_hit_blocks = plan["Local Hit Blocks"],
            local_read_blocks = plan["Local Read Blocks"],
            local_dirtied_blocks = plan["Local Dirtied Blocks"],
            local_written_blocks = plan["Local Written Blocks"],
            temp_read_blocks = plan["Temp Read Blocks"],
            temp_written_blocks = plan["Temp Written Blocks"],
        )

    def add_subplans(parent_node, subplans):
        for subplan in subplans:
            child_node = create_node(subplan)
            parent_node.children.append(child_node)
            add_subplans(child_node, subplan.get("Plans", []))

    root_node = create_node(qep[0]["Plan"])
    add_subplans(root_node, qep[0]["Plan"].get("Plans", []))
    return root_node

def analyze_graph(graph):
    """
    Analyzes the parsed QEP and returns an explanation of the cost computations.
    Utilizes DFS algorithm with a LIFO Stack for traversal
    """
    explanation = ""

    # Total values for tallying
    total_plan_rows = 0
    total_actual_time = 0
    total_actual_rows = 0
    total_shared_hit_blocks = 0
    total_shared_read_blocks = 0
    stack = [graph]

    # Create a stack for explanations to reverse the order because DFS starts from root
    explain_stack = []
    step_count = 1

    # Create a temp stack to get the total estimated cost from the root node
    tempstack = stack.copy()
    temp_node = tempstack.pop()
    total_total_cost = temp_node.total_cost
    total_actual_total_time = temp_node.actual_total_time
    total_total_actual_rows = temp_node.actual_rows
    total_total_estimated_rows = temp_node.plan_rows


    # DFS
    while stack:
        cur = stack.pop()
        # Scan Methods
        if cur.node_type == 'Seq Scan':
            explanation += f"A Sequential Scan is performed on the relation {cur.relation_name}. "

        elif cur.node_type == 'Sample Scan':
            explanation += f"A Sample Scan is performed on the relation {cur.relation_name} "   

        elif cur.node_type == 'Index Scan':
            explanation += f"An Index Scan is performed on the relation {cur.relation_name}. "

        elif cur.node_type == 'Index Only Scan':
            explanation += f"An Index Only Scan is performed on the relation {cur.relation_name}. "


        elif cur.node_type == 'Bitmap Heap Scan':
            explanation += f"A Bitmap Heap Scan is performed on the relation {cur.relation_name}. "

        elif cur.node_type == 'Bitmap Index Scan':
            explanation += f"A Bitmap Index Scan is performed on the relation {cur.relation_name}. "

        elif cur.node_type == 'BitmapAnd':
            explanation += f"A BitmapAnd Operation is performed on the relation {cur.relation_name}. "

        elif cur.node_type == 'BitmapOr':
            explanation += f"A BitmapOr Operation is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Tid Scan':
            explanation += f"A Tid Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Tid Range Scan':
            explanation += f"A Tid Range Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Subquery Scan':
            explanation += f"A Subquery Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Function Scan':
            explanation += f"A Function Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Table Function Scan':
            explanation += f"A Table Function Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Values Scan':
            explanation += f"A Values Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'CTE_Scan':
            explanation += f"A CTE_Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Named Tuplestore Scan':
            explanation += f"A Named Tuplestore Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Worktable Scan':
            explanation += f"A Worktable Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Foreign Scan':
            explanation += f"A Foreign Scan is performed on the relation {cur.relation_name}. "
                
        elif cur.node_type == 'Custom Scan':
            explanation += f"A Custom Scan is performed on the relation {cur.relation_name}. "
                

        # Caching methods
        elif cur.node_type == 'Materialize':
            explanation += f"The result of the child operation is stored in memory with a Materialize Operation. "
            
        elif cur.node_type == 'Memoize':
            explanation += f"The results of lookups is stored in the cache with a Memoize Operation. "

        # Join methods
        elif cur.node_type == 'Hash Join':
            explanation += f"The two relations are combined with a {cur.join_type} Hash Join Operation on the condition {cur.hash_cond}. "
        elif cur.node_type == 'Merge Join':
            explanation += f"The two relations are combined with a {cur.join_type} Merge Join Operation on the condition {cur.merge_cond}. "
        elif cur.node_type == 'Nested Loop':
            explanation += f"The two relations are combined with a {cur.join_type} Nested Loop Join Operation. "

        # Sort methods
        elif cur.node_type == 'Sort':
            explanation += f"The relation is sorted using {cur.sort_method} on key {cur.sort_key}. {cur.sort_space_used}kb of space is used for this sort. "
        elif cur.node_type == 'Incremental Sort':
            explanation += f"The relation is incrementally sorted using {cur.sort_method} on key {cur.sort_key}. {cur.sort_space_used}kb of space is used for this sort. "

        # Hash 
        elif cur.node_type == 'Hash':
            explanation += f"A Hash table is created from the previous relation, with {cur.hash_buckets} buckets. "

        # Limit
        elif cur.node_type == 'Limit':
            explanation += f"A Limit of {cur.plan_rows} is put in place to the number of rows to be scanned. "

        # Group
        elif cur.node_type == 'Group':
            explanation += f"The rows are grouped together based on key {cur.group_key} "

        # Aggregate 
        elif cur.node_type == 'Aggregate':
            explanation += f"The rows are combined together with a {cur.strategy} Aggregate Operation. "

        # Union
        elif cur.node_type == 'Append':
            explanation += f"The relations are combined with a Append Operation. "
        elif cur.node_type == 'Merge Append':
            explanation += f"The relations are combined with a Merge Append Operation. "
        elif cur.node_type == 'Recursive Union':
            explanation += f"The relations are combined Recursively with a Union Operation. "

        # Parallelization
        elif cur.node_type == 'Gather':
            explanation += f"The output of parallel workers are combined with the Gather operation without preserving the sort order. "
        elif cur.node_type == 'Gather Merge':
            explanation += f"The output of parallel workers are combined with the Gather Merge operation while preserving the sort order. "

        # Additional attributes
        if cur.index_cond:
                explanation += f"The scan has the index condition {cur.index_cond}. "

        if cur.filter:
            explanation += f"The filter {cur.filter} is then applied to it and {cur.rows_removed} rows are removed. "

        explanation += f"\n"


        # Push child nodes onto the stack (in reverse order)
        # Calculate startup cost of mother nodes by subtracting cost of child nodes (because each node's total cost is an aggregate)
        startup_cost = cur.startup_cost
        for child in reversed(cur.children):
            stack.append(child)
            # print(f"\n{cur.node_type}{startup_cost}\n")
            startup_cost -= child.startup_cost
            # print(child.startup_cost)

        # Estimated Cost
        explanation += f"This operation has an estimated startup cost of {startup_cost:.2f}, an estimated total cost of {cur.total_cost}, {cur.plan_rows} planned rows of an estimated {cur.plan_width}bytes. "

        if cur.startup_cost == 0.0:
            explanation += f"The cost could not be estimated because postgres estimates it to be extremely low as resources are reused from previous operations. "

        # Actual Cost
        explanation += f"The actual startup time of the operation was {cur.actual_startup_time}, the actual total time was {cur.actual_total_time}ms, with {cur.actual_rows} actual rows and {cur.actual_loops} actual loops. "

        # Compare rows 
        if cur.plan_rows >= cur.actual_rows:
            explanation += f"The planner estimates a worse case scenario with more rows. "
        else: 
            explanation += f"More rows are used than what the planner planned for, this could be due to repeated scanning due to errors. "

        # Block hits
        explanation += f"There were {cur.shared_hit_blocks} shared block hits(cache hits), and {cur.shared_read_blocks} shared block reads(cache misses). "

        # Next line char
        explanation += f"\n\n"


        # Total Cost and rows
        total_plan_rows += cur.plan_rows
        total_actual_time += cur.actual_total_time
        total_actual_rows += cur.actual_rows
        total_shared_hit_blocks += cur.shared_hit_blocks
        total_shared_read_blocks += cur.shared_read_blocks

        # Add explanation to stack for future reversal and clear it
        explain_stack.append(explanation)
        explanation = ""
        
        
    # Pop explanations out of stack to reverse the order after DFS Traversal
    while explain_stack:
        explanation += f"Step {step_count}: "
        cur = explain_stack.pop()
        explanation += cur
        step_count = step_count+1



    explanation += f"\n\nThe estimated total cost of all the operations is {total_total_cost:.2f} and {total_total_estimated_rows} planned rows. The actual run took {total_actual_total_time:.2f}ms to run, with {total_total_actual_rows} actual rows. The total number of shared block hits is {total_shared_hit_blocks}, with {total_shared_read_blocks} shared block misses. "

    return explanation









