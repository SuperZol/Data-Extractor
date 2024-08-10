import os
import xml.etree.ElementTree as Etree
import constants
import requests
from dotenv import load_dotenv
from pymongo import MongoClient, errors as pymongo_errors

current_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(current_dir, './.env'))

mongoURI = os.getenv('MONGO_URI')
client = MongoClient(mongoURI,
                     maxPoolSize=50,
                     waitQueueTimeoutMS=60000,
                     connectTimeoutMS=60000,
                     socketTimeoutMS=60000
                     )

db = client[os.getenv('MONGODB_DATABASE')]
products_collection = db[os.getenv('MONGODB_PRODUCTS_COLLECTION')]
super_markets_collection = db[os.getenv('MONGODB_SUPER_MARKETS_COLLECTION')]


def get_category(product_name):
    for key, value_list in constants.CATEGORIES.items():
        for value in value_list:
            if value in product_name:
                return key
    return "כללי"


def parsing(elements, element, supermarket, store_id=None):
    items = []
    flag = False
    if elements is not None and element is not None:
        for child in elements:
            if child.tag == element:
                data = {}
                for sub_child in child:
                    key = sub_child.tag
                    value = sub_child.text.strip() if sub_child.text else None
                    if key == "StoreID":
                        data["StoreId"] = value
                    else:
                        data[key] = value
                    if key == "Address" and "co." in value:
                        flag = True
                    if key == "ItemName":
                        data["Category"] = get_category(value)
                if store_id is not None:
                    data["StoreId"] = store_id.text.strip()

                if flag:
                    data["Latitude"] = -1
                    data["Longitude"] = -1
                data["StoreName"] = supermarket
                items.append(data)
    return items


def parse_prices(xml_tree, supermarket):
    items_element = xml_tree.find('Items')
    products_element = xml_tree.find('Products')
    store_id = xml_tree.find('StoreId') if xml_tree.find('StoreId') is not None else xml_tree.find('StoreID')
    if items_element is not None:
        return parsing(items_element, 'Item', supermarket, store_id)
    elif products_element is not None:
        return parsing(products_element, 'Product', supermarket, store_id)


def parse_super_markets(xml_tree, supermarket):
    stores_element = xml_tree.find('./SubChains/SubChain/Stores')
    branches_element = xml_tree.find('Branches')
    if stores_element is not None:
        return parsing(stores_element, 'Store', supermarket)
    elif branches_element is not None:
        return parsing(branches_element, 'Branch', supermarket)


def parse_promos(xml_tree, supermarket):
    promotions_element = xml_tree.find('Promotions')
    sales_element = xml_tree.find('Sales')
    store_id = xml_tree.find('StoreId') if xml_tree.find('StoreId') is not None else xml_tree.find('StoreID')
    if promotions_element is not None:
        return parsing(promotions_element, 'Promotion', supermarket, store_id)
    elif sales_element is not None:
        return parsing(sales_element, 'Sale', supermarket, store_id)


def parse_xml_data(xml_files_directory):
    parsed_prices = []
    parsed_promos = []
    parsed_super_markets = []
    for supermarket in os.listdir(xml_files_directory):
        supermarket_path = os.path.join(xml_files_directory, supermarket)
        for filename in os.listdir(supermarket_path):
            xml_file_path = os.path.join(supermarket_path, filename)
            xml_tree = Etree.parse(xml_file_path)
            if filename.startswith('PriceFull'):
                parsed_prices += parse_prices(xml_tree, supermarket)
            if filename.startswith('PromoFull'):
                parsed_promos += parse_promos(xml_tree, supermarket)
            if filename.startswith('Stores'):
                parsed_super_markets += parse_super_markets(xml_tree, supermarket)
    add_lat_lng(parsed_super_markets)
    return parsed_prices, parsed_promos, parsed_super_markets


def add_lat_lng(parsed_super_markets):
    for store in parsed_super_markets:
        store_lat = store.get('Latitude')
        store_lng = store.get('Longitude')
        if store_lat is None or store_lng is None:
            city = store.get('City')
            address = store.get('Address')
            if address:
                api_key = os.getenv("GOOGLE_MAPS_API_KEY")
                store_lat, store_lng = geocode_address(address, city, api_key)
                store['Latitude'] = store_lat
                store['Longitude'] = store_lng
            else:
                continue


def geocode_address(address: str, city: str, api_key: str):
    full_address = f"{city} {address}" if city else address
    endpoint = os.getenv("GOOGLE_MAPS_URL")
    params = {'address': full_address, 'key': api_key}
    try:
        response = requests.get(endpoint, params=params)
        data = response.json()
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
    except requests.RequestException as e:
        print(f"Error fetching geocode data: {e}")
    return None, None


def delete_in_batches(collection, batch_size):
    total_deleted = 0
    while True:
        try:
            documents = list(collection.find().limit(batch_size))
            if not documents:
                break  # Exit if there are no more documents to delete

            ids_to_delete = [doc['_id'] for doc in documents]
            collection.delete_many({'_id': {'$in': ids_to_delete}})
            total_deleted += len(ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} documents, total deleted: {total_deleted}")
        except pymongo_errors.PyMongoError as e:
            print(f"An error occurred during deletion: {e}")


def store_data(parsed_prices, parsed_promos, parsed_super_markets):
    delete_in_batches(products_collection, batch_size=70000)
    delete_in_batches(super_markets_collection, batch_size=80000)

    batch_size = 80000
    if parsed_prices:
        bulk_insert(products_collection, parsed_prices, batch_size)

    if parsed_super_markets:
        bulk_insert(super_markets_collection, parsed_super_markets, batch_size)


def bulk_insert(collection, data, batch_size):
    try:
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            try:
                collection.insert_many(batch, ordered=False)
            except pymongo_errors.BulkWriteError as e:
                print(f"Encountered {len(e.details['writeErrors'])} errors during insertion.")
            except pymongo_errors.AutoReconnect:
                print(f"Reconnecting and retrying batch {i // batch_size + 1}")
                collection.insert_many(batch, ordered=False)
    except pymongo_errors.PyMongoError as e:
        print(f"An error occurred during bulk insertion: {e}")


def main():
    parsed_prices, parsed_promos, parsed_super_markets = parse_xml_data(constants.XML_FILES_DIRECTORY)
    store_data(parsed_prices, parsed_promos, parsed_super_markets)


if __name__ == '__main__':
    main()
