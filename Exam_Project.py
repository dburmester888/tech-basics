# Importing library 
import cv2
import streamlit as st
import openfoodfacts
import json
import numpy as np

api = openfoodfacts.API(user_agent="MyAwesomeApp/1.0")
   
# Seitentitel
st.title("VEGANSCAN")
st.header("IS IT VEGAN OR NOT?")
st.divider()

# Aufteilung
col_left, col_right = st.columns(2)

# Speicherung
remember = []

# Scannerseite
with col_left:
    # Kamera
    image = st.camera_input("Scan a Barcode") 

    # Bild aufgenommen
    if image is not None:

        # Barcode auslesen
        bytes_data = image.getvalue()
        cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
        detector = cv2.barcode.BarcodeDetector()
        barcode, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

        # Kein Barcode erkannt
        if barcode == "":
            st.write(f":red[No Barcode detected]")
        
        else:
            # Barcode erkannt
            # Evtl. erstzen durch Webanfrage
            data = api.product.get(barcode)
            data_obj = json.dumps(data)

            # Name und EAN
            st.subheader("Product Info:")
            st.text("Product: " + data["product_name"])
            st.text("EAN: " + barcode)

            # Vegetarisch
            if "en:vegetarian" in data["ingredients_analysis_tags"]:
                st.write(f"Vegetarian: :green[YES]")
            elif "en:maybe-vegetarian" in data["ingredients_analysis_tags"]:
                st.write(f"Vegetarian: :orange[MAYBE (not validated)]")
            else:
                st.write(f"Vegetarian: :red[NO]")

            # Vegan
            if "en:vegan" in data["ingredients_analysis_tags"]:
                st.write(f"Vegan: :green[YES]")
            elif "en:maybe-vegan" in data["ingredients_analysis_tags"]:
                st.write(f"Vegan: :orange[MAYBE (not validated)]")
            else:
                st.write(f"Vegan: :red[NO]")

            # Speicherung
            if st.button("Add to List", type="primary" ):
                remember.append(data["product_name"])

# Speicherliste
with col_right:
    st.subheader("You remembered:")

    if len(remember) == 0 : 
        st.write("Nothing yet")

    else:
        for entry in remember:
            st.write(entry)