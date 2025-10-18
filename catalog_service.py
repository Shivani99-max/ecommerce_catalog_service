import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# Database connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1234',
    'database': 'products'
}

def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn


def build_get_products_query(name=None, category=None, price=None, is_active=None):
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE %s"
        params.append(f"%{name}%")  # Use wildcards for LIKE
    if category:
        query += " AND category LIKE %s"
        params.append(f"%{category}%")
    if price is not None:
        query += " AND price = %s"
        params.append(price)
    if is_active is not None:
        query += " AND is_active = %s"
        params.append(is_active)

    return query, params



# Create Product
@app.route('/products', methods=['POST'])
def create_product():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the last product_id
    cursor.execute("SELECT MAX(product_id) FROM Product")
    last_id = cursor.fetchone()[0]
    if last_id is None:
        new_id = 1
    else:
        new_id = last_id + 1

    # Insert new product with new_id
    cursor.execute(
        "INSERT INTO Product (product_id, sku, name, category, price, is_active) VALUES (%s, %s, %s, %s, %s, %s)",
        (new_id, data['sku'], data['name'], data['category'], data['price'], data.get('is_active', True))
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'message': 'Product created successfully', 'product_id': new_id}), 201




# ---- READ multiple Products ----
@app.route('/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    name = request.args.get('name')
    category = request.args.get('category')
    price = request.args.get('price')
    is_active = request.args.get('is_active')

    query,params = build_get_products_query(name, category, price, is_active)
   
    cursor.execute(query, params) 
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(products)
    

# ---- READ single Product ----
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Product WHERE product_id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    conn.close()
    if product:
        return jsonify(product)
    return jsonify({'message': 'Product not found'}), 404




# ---- UPDATE Product ----
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Product SET sku=%s, name=%s, category=%s, price=%s, is_active=%s WHERE product_id=%s",
        (data['sku'], data['name'], data['category'], data['price'], data.get('is_active', True), product_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Product updated successfully'})








# ---- DELETE Product ----
# Deletes single product using Product ID
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Product WHERE product_id = %s", (product_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': f'Product \'{product_id}\'deleted successfully'})




if __name__ == "__main__":
    app.run(debug=True)

