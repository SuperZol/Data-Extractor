import os
import xml.etree.ElementTree as Etree
import Constants
from database import products_collection, super_markets_collection


def parsing(elements, element, store_id=None):
    items = []
    if elements is not None and element is not None:
        for child in elements:
            if child.tag == element:
                data = {}
                for sub_child in child:
                    key = sub_child.tag
                    value = sub_child.text.strip() if sub_child.text else None
                    data[key] = value
                if store_id is not None:
                    data["StoreId"] = store_id.text.strip()
                items.append(data)
    return items


def parse_prices(xml_tree):
    items_element = xml_tree.find('Items')
    products_element = xml_tree.find('Products')
    store_id = xml_tree.find('StoreId') if xml_tree.find('StoreId') is not None else xml_tree.find('StoreID')
    if items_element is not None:
        return parsing(items_element, 'Item', store_id)
    elif products_element is not None:
        return parsing(products_element, 'Product', store_id)


def parse_super_markets(xml_tree):
    stores_element = xml_tree.find('./SubChains/SubChain/Stores')
    branches_element = xml_tree.find('Branches')
    if stores_element is not None:
        return parsing(stores_element, 'Store')
    elif branches_element is not None:
        return parsing(branches_element, 'Branch')


def parse_promos(xml_tree):
    promotions_element = xml_tree.find('Promotions')
    sales_element = xml_tree.find('Sales')
    store_id = xml_tree.find('StoreId') if xml_tree.find('StoreId') is not None else xml_tree.find('StoreID')
    if promotions_element is not None:
        return parsing(promotions_element, 'Promotion', store_id)
    elif sales_element is not None:
        return parsing(sales_element, 'Sale', store_id)


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
                parsed_prices += parse_prices(xml_tree)
            if filename.startswith('PromoFull'):
                parsed_promos += parse_promos(xml_tree)
            if filename.startswith('Stores'):
                parsed_super_markets += parse_super_markets(xml_tree)
    return parsed_prices, parsed_promos, parsed_super_markets


def store_data(parsed_prices, parsed_promos, parsed_super_markets):
    if len(parsed_prices) > 0:
        products_collection.insert_many(parsed_prices)
    if len(parsed_super_markets) > 0:
        super_markets_collection.insert_many(parsed_super_markets)


def main():
    parsed_prices, parsed_promos, parsed_super_markets = parse_xml_data(Constants.XML_FILES_DIRECTORY)
    store_data(parsed_prices, parsed_promos, parsed_super_markets)


if __name__ == '__main__':
    main()
