from flask import Flask, render_template, request
import os

from domain.scrape_content import *

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def enrich_site_data():
    message = "Catalog Attribute Enricher"
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    product_raw_json = None
    if request.method == 'POST':
        product_url = request.form.get('website_url')
        product_raw_json = reconcile_product(product_url)

    return render_template('index.html',
        message=message,
        Service=service,
        Revision=revision,
        product_raw_json=product_raw_json)


if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')