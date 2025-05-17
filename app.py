from flask import render_template, request, jsonify
import os

from domain.scrape_content import *

app = Flask(__name__)

@app.route('/', methods=['GET'])
def enrich_site_data():
    message = "Catalog Attribute Enricher"
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision)


@app.route('/get_product_data', methods=['POST'])
def get_product_data():
    """Gets data about a single product with URL as the input"""
    data = request.get_json()
    product_url = data.get('website_url')
    user_prompt = data.get('user_prompt')

    if not product_url:
        return jsonify({"error": "website_url is required"}), 400

    product_raw_json = reconcile_product(product_url, user_prompt)
    return jsonify(product_raw_json)


@app.route('/get_image_data', methods=['POST'])
def get_image_data():
    """Gets data about a single product image with URL as the input"""
    data = request.get_json()
    image_url = data.get('website_url')

    if not image_url:
        return jsonify({"error": "website_url is required"}), 400

    product_raw_json = get_product_image_data(image_url)
    return jsonify(product_raw_json)


@app.route('/export_json_ld', methods=['POST'])
def json_ld_creator():
    """Gets data about a single product with URL as the input"""
    data = request.get_json()
    product_url = data.get('website_url')
    user_prompt = data.get('user_prompt')

    if not product_url:
        return jsonify({"error": "website_url is required"}), 400

    product_raw_json = export_json_ld(product_url, user_prompt)
    print(jsonify(product_raw_json))
    return jsonify(product_raw_json)


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')