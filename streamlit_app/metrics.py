import re  # Importation pour les expressions régulières
import ast  # Pour analyser le code et calculer la complexité
import streamlit as st

def calculate_reusability_score(code):
    """
    Calcule le taux de réutilisabilité d'un code en pourcentage.
    
    Critères :
    - Nombre de fonctions/classes (modularité).
    - Réduction de la répétition du code (DRY).
    - Longueur moyenne des fonctions (cohésion).
    
    Args:
        code (str): Code source sous forme de chaîne de caractères.
    
    Returns:
        float: Taux de réutilisabilité en pourcentage.
    """
    # Détection des fonctions et classes
    functions = re.findall(r'def\s+\w+\(', code)  # Liste des fonctions
    classes = re.findall(r'class\s+\w+\(', code)  # Liste des classes
    
    # Nombre total de fonctions et classes
    modularity_score = len(functions) + len(classes)

    # Détection des lignes répétées (pour DRY)
    lines = code.split("\n")
    unique_lines = set([line.strip() for line in lines if line.strip()])  # Supprime les doublons
    repetition_score = len(unique_lines) / len(lines) if len(lines) > 0 else 1  # Échelle entre 0 et 1

    # Longueur moyenne des fonctions (indicateur de cohésion)
    function_lengths = [
        len(re.findall(r'\n', code[m.start():code.find("def ", m.start() + 1)]))
        for m in re.finditer(r'def\s+\w+\(', code)
    ]
    avg_function_length = sum(function_lengths) / len(function_lengths) if function_lengths else 0

    # Cohésion - On considère une bonne cohésion si les fonctions ont < 30 lignes
    cohesion_score = max(0, 1 - (avg_function_length / 30))

    # Pondération des scores (ajustable selon les besoins)
    reusability_score = (0.4 * modularity_score + 0.4 * repetition_score + 0.2 * cohesion_score) * 100
    
    return round(min(reusability_score, 100), 2)  # Limite à 100%

class ComplexityVisitor(ast.NodeVisitor):
    """
    Visiteur pour calculer la complexité cyclomatique à partir de l'arbre syntaxique du code.
    """
    def __init__(self):
        self.complexity = 0

    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_With(self, node):
        self.complexity += 1
        self.generic_visit(node)

    def visit_Try(self, node):
        self.complexity += len(node.handlers)
        if node.orelse:
            self.complexity += 1
        if node.finalbody:
            self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.complexity += 1
        self.generic_visit(node)

def calculate_code_complexity(code):
    """
    Calcule la complexité cyclomatique d'un code source donné.

    Args:
        code (str): Le code source en tant que chaîne de caractères.

    Returns:
        int: La complexité cyclomatique du code.
    """
    try:
        tree = ast.parse(code)
        visitor = ComplexityVisitor()
        visitor.visit(tree)
        return visitor.complexity
    except Exception as e:
        st.error(f"Erreur lors de l'analyse de la complexité : {e}")
        return -1

def detect_vulnerabilities(code):
    """
    Détecte les vulnérabilités courantes dans un code source.

    Args:
        code (str): Code source à analyser.

    Returns:
        list: Liste des vulnérabilités détectées avec des descriptions.
    """
    vulnerabilities = []

    # 1. Recherche d'injection SQL (requêtes non paramétrées)
    if re.search(r"(SELECT|INSERT|UPDATE|DELETE).*['\"].*\+.*", code, re.IGNORECASE):
        vulnerabilities.append("Injection SQL potentielle : Requêtes non paramétrées.")

    # 2. Vérification des données utilisateur non validées (eval, exec)
    if re.search(r"\beval\s*\(|\bexec\s*\(", code):
        vulnerabilities.append("Utilisation dangereuse d'eval() ou exec() sans validation.")

    # 3. Manipulation de fichiers sans validation des chemins
    if re.search(r"open\s*\(\s*[\"'].*[\"']\s*\)", code) and not re.search(r"os\.path\.join", code):
        vulnerabilities.append("Ouverture de fichiers avec des chemins non validés.")

    # 4. Utilisation de mots de passe ou clés en dur
    if re.search(r"(password|key|secret)\s*=\s*['\"].*['\"]", code, re.IGNORECASE):
        vulnerabilities.append("Mot de passe ou clé sensible trouvé en dur dans le code.")

    # 5. Absence d'utilisation de HTTPS dans les appels réseau
    if re.search(r"(http://)", code):
        vulnerabilities.append("Appels réseau non sécurisés (HTTP au lieu de HTTPS).")

    # 6. Appels système non sécurisés (os.system, subprocess sans arguments sécurisés)
    if re.search(r"os\.system\s*\(|subprocess\.\w+\s*\(", code):
        vulnerabilities.append("Appels système potentiellement non sécurisés.")

    # 7. Absence de gestion des erreurs
    if not re.search(r"try\s*:\s*\n.*except\s*:", code, re.DOTALL):
        vulnerabilities.append("Absence de gestion des exceptions pour le traitement des erreurs.")

    return vulnerabilities