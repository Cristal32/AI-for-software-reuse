import streamlit as st
from api import refactor_code  , get_recommendation
from snippet import load_snippets, save_snippets

# Chemin du fichier JSON
SNIPPETS_FILE = "snippets.json"

# Charger les snippets
snippets = load_snippets(SNIPPETS_FILE)

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

    st.sidebar.title("Snippets de Code")
    for snippet in snippets:
        st.sidebar.write(f"**{snippet['description']}**")
        st.sidebar.code(snippet['code'])

    st.header("Réutilisation de snippets")

    # Ajouter un nouveau snippet
    with st.form("add_snippet_form"):
        st.write("Ajouter un nouveau snippet")
        new_code = st.text_area("Code")
        new_description = st.text_input("Description")
        new_tags = st.text_input("Tags (séparés par des virgules)")
        submitted = st.form_submit_button("Ajouter")

        if submitted:
            new_snippet = {
                "id": len(snippets) + 1,
                "code": new_code,
                "description": new_description,
                "tags": [tag.strip() for tag in new_tags.split(",")]
            }
            snippets.append(new_snippet)
            save_snippets(SNIPPETS_FILE, snippets)
            st.success("Snippet ajouté avec succès !")

    # Recommander un snippet
    input_code = st.text_area("Entrer le code pour obtenir une recommandation")
    if st.button("Recommander un snippet"):
        if input_code:
            # Get recommendation from the Llama API
            recommended_code = get_recommendation(input_code, snippets)
            
            if recommended_code:
                st.write("Snippet recommandé :")
                st.code(recommended_code)
            else:
                st.write("Aucune recommandation n'a pu être trouvée.")
        else:
            st.warning("Veuillez entrer un code pour obtenir une recommandation.")

if __name__ == "__main__":
    main()
