import streamlit as st
from api import refactor_code  

# Set the page layout to wide
st.set_page_config(page_title="Refactoring Automatisé", layout="wide")

def main():
    st.title("Refactoring Automatisé pour la Réutilisabilité")

    st.header("Refactoriser votre code")

    # Create two columns with custom width ratios
    col1, col2 = st.columns([3, 3]) 

    with col1:
        st.subheader("Code Source")
        original_code = st.text_area("Entrez le code ici:", height=400, key="input_code")

    with col2:
        st.subheader("Code Refactorisé")
        refactored_code_placeholder = st.empty()

    if st.button("Refactoriser"):
        if original_code:
            with st.spinner("Refactoring en cours..."):
                refactored_code = refactor_code(original_code)
                if refactored_code:
                    st.success("Refactoring réussi!", icon="✅")
                    refactored_code_placeholder.code(refactored_code, language='python')
                else:
                    st.error("Échec du refactoring.")
        else:
            st.warning("Veuillez entrer du code avant de soumettre.")

if __name__ == "__main__":
    main()
