import xml.etree.ElementTree as Etree
import Constants
from database import products_collection, super_markets_collection
import requests
import os
from dotenv import load_dotenv

current_dir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(current_dir, './.env'))


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


def store_data(parsed_prices, parsed_promos, parsed_super_markets):
    if len(parsed_prices) > 0:
        products_collection.insert_many(parsed_prices)
    if len(parsed_super_markets) > 0:
        super_markets_collection.insert_many(parsed_super_markets)


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
    full_address = f"{address}" if city is None else f"{city} {address}"
    endpoint = os.getenv("GOOGLE_MAPS_URL")
    params = {'address': full_address, 'key': api_key}
    response = requests.get(endpoint, params=params)
    data = response.json()
    if data['status'] == 'OK':
        location = data['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None


def main():
    parsed_prices, parsed_promos, parsed_super_markets = parse_xml_data(Constants.XML_FILES_DIRECTORY)
    store_data(parsed_prices, parsed_promos, parsed_super_markets)


if __name__ == '__main__':
    main()
