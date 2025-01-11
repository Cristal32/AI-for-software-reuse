import streamlit as st
from api import refactor_code  , get_recommendation
from snippet import load_snippets, save_snippets
from metrics import calculate_reusability_score, calculate_code_complexity, detect_vulnerabilities
import re

# Chemin du fichier JSON
SNIPPETS_FILE = "snippets.json"

# Charger les snippets
snippets = load_snippets(SNIPPETS_FILE)

def extract_code(text):
    """
    Extrait le code entre les symboles ``` et l'affiche.

    Args:
        text (str): Le texte contenant le code à extraire.

    Returns:
        str: Le code extrait ou un message indiquant qu'aucun code n'a été trouvé.
    """
    matches = re.findall(r'```(?:.*?)\n(.*?)\n```', text, re.DOTALL)
    if matches:
        return matches[0].strip()  # Retourne le premier bloc de code trouvé et le nettoie des espaces
    else:
        return "Aucun code trouvé entre les symboles ```."

# Set the page layout to wide
st.set_page_config(page_title="Refactoring Automatisé", layout="wide")

def main():
    st.title("Refactoring Automatisé pour la Réutilisabilité")

    st.header("Refactoriser votre code")

    st.subheader("Code Source")
    original_code = st.text_area("Entrez le code ici:", height=400, key="input_code")


    if st.button("Refactoriser"):
        if original_code:
            with st.spinner("Refactoring en cours..."):
                refactored_code = refactor_code(original_code)
                if refactored_code:
                    st.success("Refactoring réussi!", icon="✅")
                    # refactored_code_placeholder.code(refactored_code, language='python')
                    extracted_code = extract_code(refactored_code)
                    
                    if extracted_code != "Aucun code trouvé entre les symboles ```.":                        
                        # Calcul des taux de réutilisabilité
                        original_reusability = calculate_reusability_score(original_code)
                        refactored_reusability = calculate_reusability_score(extracted_code)
                        # Calcul de la complexité des deux versions
                        original_complexity = calculate_code_complexity(original_code)
                        refactored_complexity = calculate_code_complexity(extracted_code)

                        st.subheader("Code Refactorisé")
                        st.code(extracted_code, language='python')

                        st.subheader("Taux de réutilisabilité")
                        st.write(f"**Code original :** {original_reusability}%")
                        st.write(f"**Code refactorisé :** {refactored_reusability}%")

                        st.subheader("Analyse de la complexité")
                        st.write(f"**Complexité du code original** : {original_complexity}")
                        st.write(f"**Complexité du code refactorisé** : {refactored_complexity}")

                         # Analyse des vulnérabilités dans le code refactorisé
                        vulnerabilities_refactored = detect_vulnerabilities(extracted_code)
                        st.subheader("Vulnérabilités dans le code refactorisé")
                        if vulnerabilities_refactored:
                            for vuln in vulnerabilities_refactored:
                                st.write(f"- {vuln}")
                        else:
                            st.write("Aucune vulnérabilité détectée dans le code refactorisé.")
                    else:
                        st.error("Aucun code entre les backticks trouvé dans le code refactorisé.")
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
