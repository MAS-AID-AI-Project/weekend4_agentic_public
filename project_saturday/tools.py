"""
Tool implementations for Agentic AI exercises.
This file contains database wrappers and tool definitions that students will use
but don't need to see the implementation details of.
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional

# Global variable to store API key (set from notebook)
OPENROUTER_API_KEY = None


# ============================================================================
# Database Setup and Utilities
# ============================================================================

def setup_demo_database(db_path: str = ":memory:") -> sqlite3.Connection:
    """
    Create and populate a demo SQLite database with sample data.

    Args:
        db_path: Path to database file (default is in-memory)

    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create customers table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            registration_date TEXT
        )
    """)

    # Create products table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            price REAL,
            stock_quantity INTEGER,
            category TEXT
        )
    """)

    # Create sales table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INTEGER PRIMARY KEY,
            product_id INTEGER,
            customer_id INTEGER,
            quantity INTEGER,
            sale_date TEXT,
            FOREIGN KEY (product_id) REFERENCES products(product_id),
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        )
    """)

    # Insert sample customers
    sample_customers = [
        (1, "Alice Johnson", "alice@example.com", "555-0101", "2024-01-15"),
        (2, "Bob Smith", "bob@example.com", "555-0102", "2024-02-20"),
        (3, "Carol White", "carol@example.com", "555-0103", "2024-03-10"),
        (4, "David Brown", "david@example.com", "555-0104", "2024-04-05"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?, ?)",
        sample_customers
    )

    # Insert sample products
    sample_products = [
        (1, "Red Paper", "High-quality red colored paper, 500 sheets", 25.99, 150, "Office Supplies"),
        (2, "Blue Pen", "Smooth-writing blue ballpoint pen", 2.49, 500, "Writing Instruments"),
        (3, "Notebook", "Spiral-bound notebook, 200 pages", 8.99, 300, "Office Supplies"),
        (4, "Stapler", "Heavy-duty metal stapler", 15.99, 75, "Office Equipment"),
        (5, "Paper Clips", "Box of 100 paper clips", 3.99, 200, "Office Supplies"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?, ?, ?)",
        sample_products
    )

    # Insert sample sales (including Red Paper sales throughout 2025)
    sample_sales = [
        (1, 1, 1, 5, "2025-01-15"),
        (2, 1, 2, 10, "2025-02-10"),
        (3, 2, 1, 3, "2025-02-15"),
        (4, 1, 3, 8, "2025-03-20"),
        (5, 3, 2, 2, "2025-04-05"),
        (6, 1, 4, 15, "2025-05-12"),
        (7, 4, 1, 1, "2025-06-18"),
        (8, 1, 2, 12, "2025-07-22"),
        (9, 1, 3, 7, "2025-08-30"),
        (10, 5, 4, 20, "2025-09-14"),
        (11, 1, 1, 10, "2025-10-25"),
        (12, 1, 4, 6, "2025-11-08"),
        (13, 2, 3, 5, "2025-12-15"),
    ]
    cursor.executemany(
        "INSERT OR IGNORE INTO sales VALUES (?, ?, ?, ?, ?)",
        sample_sales
    )

    conn.commit()
    return conn


# ============================================================================
# Tool Definitions (Function Declarations for Gemini)
# ============================================================================

CUSTOMER_LOOKUP_TOOL_SCHEMA = {
    "name": "customer_lookup",
    "description": "Look up customer information by customer ID or email address",
    "parameters": {
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "integer",
                "description": "The unique customer ID"
            },
            "email": {
                "type": "string",
                "description": "The customer's email address"
            }
        }
    }
}

PRODUCT_INVENTORY_TOOL_SCHEMA = {
    "name": "product_inventory",
    "description": "Check product inventory, including stock levels and pricing",
    "parameters": {
        "type": "object",
        "properties": {
            "product_id": {
                "type": "integer",
                "description": "The unique product ID"
            },
            "product_name": {
                "type": "string",
                "description": "The product name (partial match supported)"
            },
            "category": {
                "type": "string",
                "description": "Filter by product category"
            }
        }
    }
}


# ============================================================================
# Tool Execution Functions
# ============================================================================

def execute_customer_lookup(
    conn: sqlite3.Connection,
    customer_id: Optional[int] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a customer lookup query.

    Args:
        conn: SQLite connection
        customer_id: Customer ID to look up
        email: Customer email to look up

    Returns:
        Dictionary with customer information or error
    """
    cursor = conn.cursor()

    try:
        if customer_id is not None:
            cursor.execute(
                "SELECT * FROM customers WHERE customer_id = ?",
                (customer_id,)
            )
        elif email is not None:
            cursor.execute(
                "SELECT * FROM customers WHERE email = ?",
                (email,)
            )
        else:
            return {"error": "Must provide either customer_id or email"}

        row = cursor.fetchone()

        if row:
            return {
                "customer_id": row[0],
                "name": row[1],
                "email": row[2],
                "phone": row[3],
                "registration_date": row[4]
            }
        else:
            return {"error": "Customer not found"}

    except Exception as e:
        return {"error": str(e)}


def execute_product_inventory(
    conn: sqlite3.Connection,
    product_id: Optional[int] = None,
    product_name: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute a product inventory query.

    Args:
        conn: SQLite connection
        product_id: Product ID to look up
        product_name: Product name to search (partial match)
        category: Category to filter by

    Returns:
        Dictionary with product information or list of products
    """
    cursor = conn.cursor()

    try:
        if product_id is not None:
            cursor.execute(
                "SELECT * FROM products WHERE product_id = ?",
                (product_id,)
            )
            row = cursor.fetchone()

            if row:
                return {
                    "product_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "stock_quantity": row[4],
                    "category": row[5]
                }
            else:
                return {"error": "Product not found"}

        else:
            query = "SELECT * FROM products WHERE 1=1"
            params = []

            if product_name:
                # Use GLOB for case-sensitive matching (to demonstrate robustness issues)
                query += " AND name GLOB ?"
                params.append(f"*{product_name}*")

            if category:
                query += " AND category = ?"
                params.append(category)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append({
                    "product_id": row[0],
                    "name": row[1],
                    "description": row[2],
                    "price": row[3],
                    "stock_quantity": row[4],
                    "category": row[5]
                })

            return {"products": products, "count": len(products)}

    except Exception as e:
        return {"error": str(e)}


def execute_sales_query(
    conn: sqlite3.Connection,
    product_name: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Query sales data for a specific product.

    Args:
        conn: SQLite connection
        product_name: Name of the product
        start_date: Start date (YYYY-MM-DD format)
        end_date: End date (YYYY-MM-DD format)

    Returns:
        Dictionary with sales data
    """
    cursor = conn.cursor()

    try:
        query = """
            SELECT s.sale_date, s.quantity, p.name
            FROM sales s
            JOIN products p ON s.product_id = p.product_id
            WHERE p.name LIKE ?
        """
        params = [f"%{product_name}%"]

        if start_date:
            query += " AND s.sale_date >= ?"
            params.append(start_date)

        if end_date:
            query += " AND s.sale_date <= ?"
            params.append(end_date)

        query += " ORDER BY s.sale_date"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        sales_data = []
        total_quantity = 0

        for row in rows:
            sales_data.append({
                "date": row[0],
                "quantity": row[1],
                "product": row[2]
            })
            total_quantity += row[1]

        return {
            "sales": sales_data,
            "total_quantity": total_quantity,
            "count": len(sales_data)
        }

    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# Tool Registry and Dispatcher
# ============================================================================

TOOL_REGISTRY = {
    "customer_lookup": {
        "schema": CUSTOMER_LOOKUP_TOOL_SCHEMA,
        "executor": execute_customer_lookup
    },
    "product_inventory": {
        "schema": PRODUCT_INVENTORY_TOOL_SCHEMA,
        "executor": execute_product_inventory
    }
}


def get_all_tool_schemas() -> List[Dict[str, Any]]:
    """
    Get all tool schemas for Gemini API.

    Returns:
        List of tool schema dictionaries
    """
    return [tool["schema"] for tool in TOOL_REGISTRY.values()]


def get_openai_function_declarations():
    """
    Get function declarations in the format OpenAI/OpenRouter expects.

    Returns:
        List of function declaration objects for OpenAI tool calling
    """
    declarations = []
    for tool in TOOL_REGISTRY.values():
        schema = tool["schema"]
        declarations.append({
            "type": "function",
            "function": {
                "name": schema["name"],
                "description": schema["description"],
                "parameters": schema["parameters"]
            }
        })
    return declarations


# Keep for backwards compatibility
def get_gemini_function_declarations():
    """
    Deprecated: Use get_openai_function_declarations() instead.
    This function now returns OpenAI-compatible format for use with OpenRouter.
    """
    return get_openai_function_declarations()


def execute_tool(
    conn: sqlite3.Connection,
    tool_name: str,
    tool_input: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Execute a tool by name with given input.

    Args:
        conn: Database connection
        tool_name: Name of the tool to execute
        tool_input: Dictionary of tool parameters

    Returns:
        Tool execution result
    """
    if tool_name not in TOOL_REGISTRY:
        return {"error": f"Unknown tool: {tool_name}"}

    executor = TOOL_REGISTRY[tool_name]["executor"]
    return executor(conn, **tool_input)


# ============================================================================
# Schema Verification Functions (Hidden from Students)
# ============================================================================

def verify_sales_chart_schema(schema: Dict[str, Any]) -> None:
    """
    Verify the sales chart schema is correctly completed.
    Students call this with: tools.verify_sales_chart_schema(sales_chart_schema)
    """
    errors = []

    # Check product_category type
    try:
        if schema["parameters"]["properties"]["product_category"]["type"] != "string":
            errors.append("❌ product_category type is incorrect. Hint: Product names are text.")
    except KeyError:
        errors.append("❌ product_category type is missing or incorrectly placed")

    # Check time_period_months maximum constraint
    try:
        if "maximum" not in schema["parameters"]["properties"]["time_period_months"]:
            errors.append("❌ time_period_months is missing a constraint. Hint: We want to limit how many months.")
        elif schema["parameters"]["properties"]["time_period_months"]["maximum"] != 12:
            errors.append("❌ time_period_months constraint value is incorrect. Hint: Check the business rules.")
    except KeyError:
        errors.append("❌ time_period_months constraint is missing or incorrectly placed")

    # Check limit_rows type
    try:
        if schema["parameters"]["properties"]["limit_rows"]["type"] != "integer":
            errors.append("❌ limit_rows type is incorrect. Hint: Row counts must be whole numbers.")
    except KeyError:
        errors.append("❌ limit_rows type is missing or incorrectly placed")

    # Check required field
    try:
        if "required" not in schema["parameters"]:
            errors.append("❌ Missing 'required' field in parameters. Hint: Look at the available constraints.")
        elif "product_category" not in schema["parameters"]["required"]:
            errors.append("❌ The required field is missing a critical property. Hint: Check business rule #3.")
    except KeyError:
        errors.append("❌ Required field is missing or incorrectly placed")

    # Print results
    print("\n" + "="*60)
    print("📊 Sales Chart Schema Verification Results")
    print("="*60)

    if not errors:
        print("\n🎉 Perfect! Your schema is complete and correct!")
        print("\n💡 Key Insight: These constraints prevent the AI from making")
        print("   expensive or dangerous database queries. This is critical")
        print("   for production systems!")
    else:
        print(f"\n❌ Found {len(errors)} issue(s):\n")
        for error in errors:
            print(error)
        print(f"\n⚠️  Review the hints above and try again!")

    print("="*60 + "\n")


def verify_support_ticket_schema(schema: Dict[str, Any]) -> None:
    """
    Verify the support ticket schema is correctly completed.
    Students call this with: tools.verify_support_ticket_schema(support_ticket_schema)
    """
    errors = []

    # Check priority enum
    try:
        if "enum" not in schema["parameters"]["properties"]["priority"]:
            errors.append("❌ priority is missing a constraint. Hint: We need to restrict it to specific choices.")
        elif schema["parameters"]["properties"]["priority"]["enum"] != ["low", "medium", "high"]:
            errors.append("❌ priority constraint values are incorrect. Hint: Check the available options.")
    except KeyError:
        errors.append("❌ priority constraint is missing or incorrectly placed")

    # Check issue_summary description
    try:
        if "description" not in schema["parameters"]["properties"]["issue_summary"]:
            errors.append("❌ issue_summary is missing a field. Hint: We need to explain what this field is for.")
        elif not isinstance(schema["parameters"]["properties"]["issue_summary"]["description"], str) or len(schema["parameters"]["properties"]["issue_summary"]["description"]) < 10:
            errors.append("❌ issue_summary field value is too short or invalid. Hint: It should be a meaningful explanation.")
    except KeyError:
        errors.append("❌ issue_summary is missing or incorrectly placed")

    # Check required fields
    try:
        if "required" not in schema["parameters"]:
            errors.append("❌ Missing 'required' field in parameters. Hint: Look at the available constraints.")
        else:
            required = schema["parameters"]["required"]
            if "priority" not in required or "issue_summary" not in required:
                errors.append("❌ The required array is incomplete. Hint: Both fields should be mandatory.")
    except KeyError:
        errors.append("❌ Required field is missing or incorrectly placed")

    # Print results
    print("\n" + "="*60)
    print("🎫 Support Ticket Schema Verification Results")
    print("="*60)

    if not errors:
        print("\n🎉 Excellent! Your schema is complete and correct!")
        print("\n💡 Key Insight: Enums and required fields prevent the AI from")
        print("   generating invalid data. This ensures tickets are properly")
        print("   routed to the right human agents!")
    else:
        print(f"\n❌ Found {len(errors)} issue(s):\n")
        for error in errors:
            print(error)
        print(f"\n⚠️  Review the hints above and try again!")

    print("="*60 + "\n")


# ============================================================================
# Part 3: Dashboard Builder Tools
# ============================================================================

def get_db_schema_description() -> str:
    """
    Returns a human-readable description of the database schema.
    This is provided to the LLM to help it understand what queries are possible.
    """
    return """
DATABASE SCHEMA:

TABLE: customers
- customer_id (INTEGER, PRIMARY KEY): Unique identifier for each customer
- name (TEXT): Customer's full name
- email (TEXT): Customer's email address
- phone (TEXT): Customer's phone number
- registration_date (TEXT): Date when customer registered (YYYY-MM-DD format)

TABLE: products
- product_id (INTEGER, PRIMARY KEY): Unique identifier for each product
- name (TEXT): Product name (e.g., "Red Paper", "Blue Pen")
- description (TEXT): Detailed product description
- price (REAL): Price per unit in dollars
- stock_quantity (INTEGER): Current stock level
- category (TEXT): Product category (e.g., "Office Supplies", "Writing Instruments")

TABLE: sales
- sale_id (INTEGER, PRIMARY KEY): Unique identifier for each sale
- product_id (INTEGER, FOREIGN KEY -> products): Which product was sold
- customer_id (INTEGER, FOREIGN KEY -> customers): Who bought it
- quantity (INTEGER): Number of units sold
- sale_date (TEXT): Date of sale (YYYY-MM-DD format)

RELATIONSHIPS:
- sales.product_id references products.product_id
- sales.customer_id references customers.customer_id
"""


def execute_sql_query(conn: sqlite3.Connection, query: str) -> Dict[str, Any]:
    """
    Execute a SQL query and return results as a dictionary.
    This is the "robust query tool" that Part 2 would have refined.
    """
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [description[0] for description in cursor.description] if cursor.description else []
        rows = cursor.fetchall()
        return {
            "success": True,
            "columns": columns,
            "rows": [list(row) for row in rows],
            "row_count": len(rows)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "columns": [],
            "rows": [],
            "row_count": 0
        }


def nl_to_sql(user_query: str, schema_description: str = None) -> str:
    """
    Converts natural language to SQL using the LLM (black box from Part 2).
    Uses OpenRouter API.
    """
    from openai import OpenAI

    if OPENROUTER_API_KEY is None:
        raise ValueError("OPENROUTER_API_KEY not set. Please set tools.OPENROUTER_API_KEY in your notebook.")

    if schema_description is None:
        schema_description = get_db_schema_description()

    prompt = f"""You are a SQL expert. Convert the following natural language query into a valid SQLite query.

{schema_description}

IMPORTANT RULES:
1. Only return the SQL query, nothing else
2. Use proper SQL syntax for SQLite
3. Use appropriate JOINs when data from multiple tables is needed
4. For date filtering, use date comparisons with the YYYY-MM-DD format
5. Always use table aliases for clarity in JOINs

User Query: {user_query}

SQL Query:"""

    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[{"role": "user", "content": prompt}]
    )

    sql = response.choices[0].message.content.strip()
    if sql.startswith("```sql"):
        sql = sql[6:]
    if sql.startswith("```"):
        sql = sql[3:]
    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


# ============================================================================
# Data Transformation Functions
# ============================================================================

def transform_for_bar_chart(query_result: Dict[str, Any],
                            label_column: str,
                            value_column: str) -> Dict[str, Any]:
    """Transform SQL query results into format suitable for a bar chart."""
    if not query_result.get("success", False):
        return {"error": query_result.get("error", "Query failed")}

    columns = query_result["columns"]
    rows = query_result["rows"]

    try:
        label_idx = columns.index(label_column)
        value_idx = columns.index(value_column)
    except ValueError as e:
        return {"error": f"Column not found: {e}"}

    return {
        "chart_type": "bar",
        "labels": [row[label_idx] for row in rows],
        "values": [row[value_idx] for row in rows],
        "label_column": label_column,
        "value_column": value_column
    }


def transform_for_line_chart(query_result: Dict[str, Any],
                             x_column: str,
                             y_column: str,
                             series_column: str = None) -> Dict[str, Any]:
    """Transform SQL query results into format suitable for a line chart."""
    if not query_result.get("success", False):
        return {"error": query_result.get("error", "Query failed")}

    columns = query_result["columns"]
    rows = query_result["rows"]

    try:
        x_idx = columns.index(x_column)
        y_idx = columns.index(y_column)
        series_idx = columns.index(series_column) if series_column else None
    except ValueError as e:
        return {"error": f"Column not found: {e}"}

    if series_column:
        series_data = {}
        for row in rows:
            series_name = row[series_idx]
            if series_name not in series_data:
                series_data[series_name] = {"x": [], "y": []}
            series_data[series_name]["x"].append(row[x_idx])
            series_data[series_name]["y"].append(row[y_idx])

        return {
            "chart_type": "line",
            "series": series_data,
            "x_column": x_column,
            "y_column": y_column
        }
    else:
        return {
            "chart_type": "line",
            "x": [row[x_idx] for row in rows],
            "y": [row[y_idx] for row in rows],
            "x_column": x_column,
            "y_column": y_column
        }


def transform_for_pie_chart(query_result: Dict[str, Any],
                            label_column: str,
                            value_column: str) -> Dict[str, Any]:
    """Transform SQL query results into format suitable for a pie chart."""
    if not query_result.get("success", False):
        return {"error": query_result.get("error", "Query failed")}

    columns = query_result["columns"]
    rows = query_result["rows"]

    try:
        label_idx = columns.index(label_column)
        value_idx = columns.index(value_column)
    except ValueError as e:
        return {"error": f"Column not found: {e}"}

    labels = [row[label_idx] for row in rows]
    values = [row[value_idx] for row in rows]
    total = sum(values)
    percentages = [round(v / total * 100, 1) if total > 0 else 0 for v in values]

    return {
        "chart_type": "pie",
        "labels": labels,
        "values": values,
        "percentages": percentages,
        "total": total
    }


# ============================================================================
# Dashboard Visualization Tool
# ============================================================================

def generate_dashboard_html(chart_data: Dict[str, Any], title: str = "Dashboard") -> str:
    """Generate an interactive HTML dashboard from transformed chart data."""
    import random

    if "error" in chart_data:
        return f"""
        <div style="padding: 20px; background: #fee; border: 2px solid #c00; border-radius: 10px;">
            <h3 style="color: #c00;">Error</h3>
            <p>{chart_data['error']}</p>
        </div>
        """

    chart_type = chart_data.get("chart_type", "bar")
    chart_id = f"chart_{random.randint(10000, 99999)}"

    if chart_type == "bar":
        return _generate_bar_chart_html(chart_data, title, chart_id)
    elif chart_type == "line":
        return _generate_line_chart_html(chart_data, title, chart_id)
    elif chart_type == "pie":
        return _generate_pie_chart_html(chart_data, title, chart_id)
    else:
        return f"<p>Unknown chart type: {chart_type}</p>"


def _generate_bar_chart_html(data: Dict, title: str, chart_id: str) -> str:
    """Generate HTML for a bar chart."""
    labels = data["labels"]
    values = data["values"]
    max_val = max(values) if values else 1

    bars_html = ""
    for i, (label, value) in enumerate(zip(labels, values)):
        width_pct = (value / max_val) * 100
        color = f"hsl({(i * 47) % 360}, 70%, 50%)"
        bars_html += f"""
        <div style="display: flex; align-items: center; margin: 10px 0;">
            <div style="width: 150px; text-align: right; padding-right: 10px; font-weight: 500; color: #333; font-size: 13px;">
                {label}
            </div>
            <div style="flex: 1; background: #eee; border-radius: 5px; overflow: hidden;">
                <div style="width: {width_pct}%; background: {color}; padding: 8px 12px; color: white;
                            font-weight: bold; border-radius: 5px; transition: width 0.5s ease; min-width: 40px;">
                    {value:,.0f}
                </div>
            </div>
        </div>
        """

    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div style="background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="margin: 0 0 20px 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                📊 {title}
            </h2>
            <div style="padding: 10px 0;">
                {bars_html}
            </div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee;
                        font-size: 12px; color: #666;">
                Data columns: {data.get('label_column', 'N/A')} → {data.get('value_column', 'N/A')}
            </div>
        </div>
    </div>
    """


def _generate_line_chart_html(data: Dict, title: str, chart_id: str) -> str:
    """Generate HTML for a line chart using SVG."""
    import math

    if "series" in data:
        all_y = []
        for series_data in data["series"].values():
            all_y.extend(series_data["y"])
    else:
        all_y = data["y"]

    if not all_y:
        return "<p>No data to display</p>"

    min_y, max_y = min(all_y), max(all_y)
    y_range = max_y - min_y if max_y != min_y else 1

    width, height = 600, 300
    padding = 60

    svg_content = f'<svg width="{width}" height="{height}" style="background: white;">'
    svg_content += '<g stroke="#eee" stroke-width="1">'

    for i in range(5):
        y = padding + (height - 2 * padding) * i / 4
        svg_content += f'<line x1="{padding}" y1="{y}" x2="{width - padding}" y2="{y}"/>'

    svg_content += "</g>"

    if "series" in data:
        colors = ["#667eea", "#f093fb", "#4facfe", "#43e97b", "#fa709a"]
        legend_items = []

        for idx, (series_name, series_data) in enumerate(data["series"].items()):
            color = colors[idx % len(colors)]
            x_vals = series_data["x"]
            y_vals = series_data["y"]

            if len(x_vals) > 1:
                points = []
                for i, (x, y) in enumerate(zip(x_vals, y_vals)):
                    px = padding + (width - 2 * padding) * i / (len(x_vals) - 1)
                    py = height - padding - (height - 2 * padding) * (y - min_y) / y_range
                    points.append(f"{px},{py}")

                svg_content += f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>'
                for point in points:
                    px, py = point.split(",")
                    svg_content += f'<circle cx="{px}" cy="{py}" r="5" fill="{color}"/>'

            legend_items.append(f'<span style="color: {color};">● {series_name}</span>')
        legend_html = " &nbsp; ".join(legend_items)
    else:
        x_vals = data["x"]
        y_vals = data["y"]
        if len(x_vals) > 1:
            points = []
            for i, (x, y) in enumerate(zip(x_vals, y_vals)):
                px = padding + (width - 2 * padding) * i / (len(x_vals) - 1)
                py = height - padding - (height - 2 * padding) * (y - min_y) / y_range
                points.append(f"{px},{py}")

            svg_content += f'<polyline points="{" ".join(points)}" fill="none" stroke="#667eea" stroke-width="3"/>'
            for point in points:
                px, py = point.split(",")
                svg_content += f'<circle cx="{px}" cy="{py}" r="5" fill="#667eea"/>'
        legend_html = ""

    svg_content += f'''
        <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#333" stroke-width="2"/>
        <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#333" stroke-width="2"/>
    '''

    # Y-axis labels
    for i in range(5):
        y = padding + (height - 2 * padding) * i / 4
        val = max_y - (max_y - min_y) * i / 4
        svg_content += f'<text x="{padding - 10}" y="{y + 4}" text-anchor="end" font-size="11" fill="#666">{val:,.0f}</text>'

    # X-axis labels
    x_labels = data.get("x", [])
    if "series" in data and data["series"]:
        # Get x labels from the first series
        first_series = list(data["series"].values())[0]
        x_labels = first_series.get("x", [])

    if x_labels:
        num_labels = len(x_labels)
        # Show all labels if 6 or fewer, otherwise show subset
        if num_labels <= 6:
            label_indices = range(num_labels)
        else:
            # Show first, last, and evenly spaced labels in between
            step = max(1, (num_labels - 1) // 5)
            label_indices = list(range(0, num_labels, step))
            if (num_labels - 1) not in label_indices:
                label_indices.append(num_labels - 1)

        for i in label_indices:
            if num_labels > 1:
                px = padding + (width - 2 * padding) * i / (num_labels - 1)
            else:
                px = padding + (width - 2 * padding) / 2
            label_text = str(x_labels[i])
            # Truncate long labels
            if len(label_text) > 10:
                label_text = label_text[:8] + ".."
            svg_content += f'<text x="{px}" y="{height - padding + 20}" text-anchor="middle" font-size="10" fill="#666">{label_text}</text>'

    svg_content += "</svg>"

    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div style="background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="margin: 0 0 20px 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                📈 {title}
            </h2>
            <div style="text-align: center;">{svg_content}</div>
            {f'<div style="text-align: center; margin-top: 10px;">{legend_html}</div>' if legend_html else ''}
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #666;">
                X-axis: {data.get('x_column', 'N/A')} | Y-axis: {data.get('y_column', 'N/A')}
            </div>
        </div>
    </div>
    """


def _generate_pie_chart_html(data: Dict, title: str, chart_id: str) -> str:
    """Generate HTML for a pie chart using SVG."""
    import math

    labels = data["labels"]
    values = data["values"]
    percentages = data["percentages"]
    total = data["total"]

    cx, cy, r = 150, 150, 120
    colors = ["#667eea", "#f093fb", "#4facfe", "#43e97b", "#fa709a", "#ffecd2", "#fcb69f", "#a1c4fd"]

    svg_content = '<svg width="300" height="300" style="background: white;">'
    start_angle = 0
    legend_items = []

    for i, (label, value, pct) in enumerate(zip(labels, values, percentages)):
        if total == 0:
            continue

        angle = (value / total) * 360
        end_angle = start_angle + angle

        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(end_angle - 90)

        x1 = cx + r * math.cos(start_rad)
        y1 = cy + r * math.sin(start_rad)
        x2 = cx + r * math.cos(end_rad)
        y2 = cy + r * math.sin(end_rad)

        large_arc = 1 if angle > 180 else 0
        color = colors[i % len(colors)]

        svg_content += f'<path d="M {cx} {cy} L {x1} {y1} A {r} {r} 0 {large_arc} 1 {x2} {y2} Z" fill="{color}" stroke="white" stroke-width="2"/>'
        legend_items.append(f'''
        <div style="display: flex; align-items: center; margin: 5px 0;">
            <div style="width: 16px; height: 16px; background: {color}; border-radius: 3px; margin-right: 8px;"></div>
            <span style="color: #333;">{label}: {pct}% ({value:,.0f})</span>
        </div>
        ''')

        start_angle = end_angle

    svg_content += "</svg>"
    legend_html = "".join(legend_items)

    return f"""
    <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 25px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 15px; margin: 20px 0; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
        <div style="background: white; border-radius: 12px; padding: 25px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
            <h2 style="margin: 0 0 20px 0; color: #333; border-bottom: 2px solid #667eea; padding-bottom: 10px;">
                🥧 {title}
            </h2>
            <div style="display: flex; align-items: center; justify-content: space-around; flex-wrap: wrap;">
                <div>{svg_content}</div>
                <div style="padding: 20px;">{legend_html}</div>
            </div>
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #eee; font-size: 12px; color: #666; text-align: center;">
                Total: {total:,.0f}
            </div>
        </div>
    </div>
    """


def display_dashboard(chart_data: Dict[str, Any], title: str = "Dashboard"):
    """Display an interactive dashboard in the notebook."""
    from IPython.display import HTML, display
    html = generate_dashboard_html(chart_data, title)
    display(HTML(html))


# ============================================================================
# Part 3: Schema Feasibility Exercise Verification
# ============================================================================

def verify_schema_feasibility(student_answers: Dict[str, str]) -> None:
    """
    Verify student answers for the "What Can We Ask?" schema feasibility exercise.
    Students call this with: tools.verify_schema_feasibility(scenarios)
    """
    correct_answers = {
        "1. Show total sales revenue per product": {
            "answer": "POSSIBLE",
            "hint": "You can JOIN sales with products, then multiply quantity x price and SUM it up."
        },
        "2. Show which customer bought the most items": {
            "answer": "POSSIBLE",
            "hint": "JOIN sales with customers, SUM the quantity, GROUP BY customer, ORDER BY total."
        },
        "3. Show sales trends over time (monthly)": {
            "answer": "POSSIBLE",
            "hint": "Use strftime() to extract month from sale_date, then GROUP BY month."
        },
        "4. Show customer satisfaction ratings": {
            "answer": "IMPOSSIBLE",
            "hint": "Look at the schema carefully - is there any table with ratings or feedback?"
        },
        "5. Show inventory levels by category": {
            "answer": "POSSIBLE",
            "hint": "The products table has both stock_quantity and category columns."
        },
        "6. Show profit margins per product": {
            "answer": "IMPOSSIBLE",
            "hint": "To calculate profit, you need both selling price AND cost price. What's missing?"
        },
        "7. Show sales by customer registration month": {
            "answer": "POSSIBLE",
            "hint": "JOIN customers with sales, GROUP BY registration month using strftime()."
        },
    }

    results = []
    correct_count = 0
    total = len(correct_answers)

    print("\n" + "="*70)
    print("📊 Schema Feasibility Exercise - Results")
    print("="*70)

    for question, correct_data in correct_answers.items():
        student_answer = student_answers.get(question, "???").upper().strip()
        correct_answer = correct_data["answer"]
        hint = correct_data["hint"]

        if student_answer == "???":
            status = "⏳"
            message = "Not answered yet"
            results.append((question, status, message, hint))
        elif student_answer == correct_answer:
            status = "✅"
            message = f"Correct! ({correct_answer})"
            correct_count += 1
            results.append((question, status, message, None))
        else:
            status = "❌"
            message = f"Incorrect (you said: {student_answer})"
            results.append((question, status, message, hint))

    for question, status, message, hint in results:
        print(f"\n{status} {question}")
        print(f"   {message}")
        if hint:
            print(f"   💡 Hint: {hint}")

    print("\n" + "-"*70)
    print(f"Score: {correct_count}/{total} correct")

    if correct_count == total:
        print("\n🎉 Perfect! You understand schema feasibility analysis!")
        print("\n💡 Key Insight: Always verify that the underlying data exists")
        print("   before promising a dashboard to stakeholders!")
    elif correct_count >= total - 2:
        print("\n👍 Great job! Review the hints for the ones you missed.")
    else:
        print("\n📚 Take another look at the schema and think about what data")
        print("   would be needed to answer each question.")

    print("="*70 + "\n")


def verify_agent_vs_deterministic(student_answers: Dict[str, str]) -> None:
    """
    Verify student answers for the Agent vs Deterministic pipeline exercise.
    Students call this with: tools.verify_agent_vs_deterministic(design_choices)
    """
    correct_answers = {
        "1. Deterministic pipelines are faster because they don't need LLM calls for orchestration": {
            "answer": "VALID",
            "explanation": "Each LLM call adds latency (often 1-3 seconds). If you can avoid orchestration calls, you save time."
        },
        "2. Deterministic pipelines are cheaper because they use fewer LLM API calls": {
            "answer": "VALID",
            "explanation": "Each LLM call costs money. Our pipeline only calls the LLM once (for NL→SQL). An Agent would call it multiple times to decide each step."
        },
        "3. Our pipeline steps always happen in the same order, so an Agent would add unnecessary complexity": {
            "answer": "VALID",
            "explanation": "When the flow is predictable (NL->SQL->Transform->Display), deterministic code is simpler and more reliable."
        },
        "4. Agents can't work with databases - only deterministic code can": {
            "answer": "MISCONCEPTION",
            "explanation": "Agents CAN use database tools! In Part 1, we saw Gemini decide to call customer_lookup. The issue is whether they SHOULD for this use case."
        },
        "5. Deterministic pipelines are easier to debug and test": {
            "answer": "VALID",
            "explanation": "With fixed steps, you can unit test each function. Agents are harder to test because their behavior varies."
        },
        "6. An Agent would be useful if users asked open-ended questions like 'What insights can you find about sales?'": {
            "answer": "VALID",
            "explanation": "Open-ended requests require judgment: which chart type? What grouping? Compare what? An Agent could explore the data and decide the best visualization approach."
        },
    }

    results = []
    correct_count = 0
    total = len(correct_answers)

    print("\n" + "="*70)
    print("🤖 Agent vs Deterministic Pipeline - Results")
    print("="*70)

    for statement, correct_data in correct_answers.items():
        student_answer = student_answers.get(statement, "???").upper().strip()
        correct_answer = correct_data["answer"]
        explanation = correct_data["explanation"]

        if student_answer == "???":
            status = "⏳"
            message = "Not answered yet"
            results.append((statement, status, message, explanation, False))
        elif student_answer == correct_answer:
            status = "✅"
            message = f"Correct! ({correct_answer})"
            correct_count += 1
            results.append((statement, status, message, explanation, True))
        else:
            status = "❌"
            message = f"Incorrect (you said: {student_answer}, correct: {correct_answer})"
            results.append((statement, status, message, explanation, False))

    for statement, status, message, explanation, is_correct in results:
        print(f"\n{status} {statement}")
        print(f"   {message}")
        print(f"   💡 {explanation}")

    print("\n" + "-"*70)
    print(f"Score: {correct_count}/{total} correct")

    if correct_count == total:
        print("\n🎉 Excellent! You understand when to use Agents vs Deterministic pipelines!")
    elif correct_count >= total - 2:
        print("\n👍 Good understanding! Review the explanations for nuance.")
    else:
        print("\n📚 Key insight: Use Agents when you need FLEXIBILITY in the workflow.")
        print("   Use Deterministic pipelines when the steps are PREDICTABLE.")

    print("\n" + "="*70)
    print("💡 DESIGN PRINCIPLE: Start simple (deterministic), add Agents only when needed!")
    print("="*70 + "\n")
