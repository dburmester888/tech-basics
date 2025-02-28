# Importing Streamlit
import streamlit as st
# Importing OpenCV and Numpy for Barcode Detection
import cv2
import numpy as np
# Importing OpenFoodFacts API for Data
import openfoodfacts

# Get an API connection
api = openfoodfacts.API(user_agent="veganscan/1.0")

# Main Title
st.title("VEGANSCAN")
st.header("IS IT VEGAN OR NOT?")
st.divider()

# Create state if it not exists
if 'remember_list' not in st.session_state:
    st.session_state['remember_list'] = []


# Camera Element
def input_elements():
    barcode = None
    image_input = st.camera_input("Scan a Barcode")

    if image_input is not None:
        # Read barcode from camera image
        bytes_data = image_input.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.barcode.BarcodeDetector()
        barcode, _, _ = detector.detectAndDecode(cv2_img)

    return barcode


# Transform API Response
def transform_data(data):
    name = "Unknown"
    brand = "Unknonn"
    vegetarian_text = ""
    vegan_text = ""

    if "product_name" in data:
        name = data["product_name"].replace("&quot;", "\"").replace("&amp;", "&").replace("apos;", "'")

    if "brands" in data:
        brand = data["brands"].replace("&quot;", "\"").replace("&amp;", "&").replace("apos;", "'")

    if "ingredients_analysis_tags" in data:
        # Vegetarian
        if "en:vegetarian" in data["ingredients_analysis_tags"]:
            vegetarian_text = f":green[Vegetarian]"
        elif "en:maybe-vegetarian" in data["ingredients_analysis_tags"]:
            vegetarian_text = f":orange[MAYBE Vegetarian]"
        else:
            vegetarian_text = f":red[NOT Vegetarian]"

        # Vegan
        if "en:vegan" in data["ingredients_analysis_tags"]:
            vegan_text = f":green[Vegan]"
        elif "en:maybe-vegan" in data["ingredients_analysis_tags"]:
            vegan_text = f":orange[MAYBE Vegan]"
        else:
            vegan_text = f":red[NOT Vegan]"

    return [name, brand, vegetarian_text, vegan_text]


# Format API Response for List
def format_info_for_list(name, brand, vegetarian_text, vegan_text):
    result = brand + " - " + name
    missing_data = False

    if vegetarian_text != "":
        result += " - " + vegetarian_text
    else:
        missing_data = True

    if vegan_text != "":
        result += " - " + vegan_text
    else:
        missing_data = True

    # Add info about missing data if needed
    if missing_data:
        result += f" - :red[MISSING DATA]"
    return result


# List Functions
def clear_list():
    del st.session_state['remember_list']


def remove_entry(index):
    st.session_state['remember_list'].pop(index)


# Main Layout
col_left, col_right = st.columns(2)
# Scanner
with col_left:
    barcode = input_elements()

    if barcode is not None:

        if barcode == "":
            st.write(f":red[No Barcode detected]")

        else:
            # Barcode erkannt
            # Evtl. erstzen durch Webanfrage
            data = api.product.get(barcode)

            name, brand, vegetarian_text, vegan_text = transform_data(data)

            # Name und EAN
            st.subheader("Product Info:")
            st.text("Name:" + name)
            st.text("Brand: " + brand)
            st.text("EAN: " + barcode)

            if vegetarian_text == "":
                st.write("Vegetarian: No Data")
            else:
                st.write(vegetarian_text)
            if vegan_text == "":
                st.write("Vegan: No Data")
            else:
                st.write(vegan_text)
                # Speicherung
            if st.button("Add to List", type="primary"):
                st.session_state['remember_list'].append(format_info_for_list(name, brand, vegetarian_text, vegan_text))

# List
with col_right:
    st.subheader("You remembered:")

    if len(st.session_state['remember_list']) == 0:
        st.write("Nothing yet")  # No entries
    else:
        # Create a Button for each entry to delete it by usings its index in the list
        position = 0
        for entry in st.session_state['remember_list']:
            st.button(entry, type="secondary", on_click=remove_entry, args=[position], key="list" + str(position))
            position += 1
        st.write("Tap an item to remove it")

        # Clear List Button
        st.button("Clear List", type="primary", on_click=clear_list)

