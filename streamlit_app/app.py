import streamlit as st
from api import refactor_code  # Importer la fonction de l'API

def main():
    st.title("Refactoring Automatisé pour la Réutilisabilité")

    st.header("Soumettez votre code existant")
    original_code = st.text_area("Code Source", height=300)

    if st.button("Refactoriser"):
        if original_code:
            with st.spinner("Refactoring en cours..."):
                refactored_code = refactor_code(original_code)
                if refactored_code:
                    st.success("Refactoring réussi!")
                    st.subheader("Code Refactorisé")
                    st.code(refactored_code, language='python')
                else:
                    st.error("Échec du refactoring.")
        else:
            st.warning("Veuillez entrer du code avant de soumettre.")

if __name__ == "__main__":
    main()
