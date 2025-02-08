import * as vscode from 'vscode';
import axios from 'axios';

// Clé d'API OpenAI (il est conseillé de la stocker dans un fichier .env ou similaire)
const OPENAI_API_KEY = '';

// Fonction pour générer le code à partir du commentaire
async function generateCodeFromComment(comment: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.openai.com/v1/chat/completions',
            {
                model: 'gpt-3.5-turbo',
                messages: [{
                    role: 'user',
                    content: `Generate Java code for: ${comment}. Only provide the code, no explanations.`
                }],
                max_tokens: 500,
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${OPENAI_API_KEY}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content.trim();
    } catch (error) {
        vscode.window.showErrorMessage('Erreur lors de la génération du code');
        return '';
    }
}

// Fonction pour générer des suggestions de code après un point
async function generateCodeSuggestion(codeContext: string): Promise<string> {
    try {
        const response = await axios.post(
            'https://api.openai.com/v1/chat/completions',
            {
                model: 'gpt-3.5-turbo',
                messages: [{
                    role: 'user',
                    content: `Given the following Java code context, provide code suggestions that make sense after the point (.) in this code: "${codeContext}". Make sure the suggestions are relevant to the object's methods and the current context.`
                }],
                max_tokens: 150,
                temperature: 0.7,
            },
            {
                headers: {
                    'Authorization': `Bearer ${OPENAI_API_KEY}`,
                    'Content-Type': 'application/json',
                },
            }
        );

        return response.data.choices[0].message.content.trim();
    } catch (error) {
        vscode.window.showErrorMessage('Erreur lors de la génération de la suggestion de code');
        return '';
    }
}

// Provider pour les suggestions de code
class CodeSuggestionProvider implements vscode.CompletionItemProvider {
    private debounceTimeout: NodeJS.Timeout | null = null;

    public async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): Promise<vscode.CompletionItem[]> {
        const lineText = document.lineAt(position.line).text;
        const wordBeforeCursor = lineText.substring(0, position.character);

        // Si le curseur est après un point (.)
        if (wordBeforeCursor.endsWith('.')) {
            // Analyser le contexte avant le point
            const contextBeforeDot = lineText.substring(0, position.character - 1).trim();

            // Vérification pour éviter les requêtes répétées
            if (this.debounceTimeout) {
                clearTimeout(this.debounceTimeout);  // Annuler l'appel précédent
            }

            // Utiliser un délai (debounce) pour éviter d'envoyer une requête à chaque caractère
            this.debounceTimeout = setTimeout(async () => {
                const generatedCode = await generateCodeSuggestion(contextBeforeDot);

                if (generatedCode) {
                    const completionItem = new vscode.CompletionItem(generatedCode, vscode.CompletionItemKind.Snippet);
                    completionItem.insertText = generatedCode;
                    completionItem.documentation = new vscode.MarkdownString(generatedCode);
                    return [completionItem];
                }
                return [];
            }, 300); // 300 ms de délai pour limiter la fréquence des requêtes
        }

        // Retourner une liste vide si aucune suggestion n'est générée
        return [];
    }
}

// Fonction d'activation de l'extension
export function activate(context: vscode.ExtensionContext) {
    // Enregistrer le provider pour les suggestions de code
    const codeSuggestionProvider = new CodeSuggestionProvider();
    context.subscriptions.push(
        vscode.languages.registerCompletionItemProvider('java', codeSuggestionProvider, '.')
    );

    // Enregistrer la commande pour générer du code à partir des commentaires
    let disposable = vscode.commands.registerCommand('extension.generateCode', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showInformationMessage('Ouvrez un fichier Java');
            return;
        }

        const position = editor.selection.active;
        const line = editor.document.lineAt(position.line);

        if (!line.text.trim().startsWith('//') && !line.text.trim().startsWith('/*')) {
            vscode.window.showInformationMessage('Placez le curseur sur un commentaire');
            return;
        }

        const commentText = line.text.trim().replace(/^\/\/|\/\*|\*\//g, '').trim();
        
        const generatedCode = await generateCodeFromComment(commentText);
        
        if (generatedCode) {
            await editor.edit(editBuilder => {
                const insertPosition = new vscode.Position(position.line + 1, 0);
                editBuilder.insert(insertPosition, '\n' + generatedCode + '\n');
            });

            await vscode.commands.executeCommand('editor.action.formatDocument');
        }
    });

    // Créer un bouton dans la barre d'état avec une priorité élevée
    let myStatusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        1000
    );
    myStatusBarItem.text = "$(code) Générer Code";
    myStatusBarItem.tooltip = "Cliquez pour générer du code à partir du commentaire";
    myStatusBarItem.command = 'extension.generateCode';
    myStatusBarItem.show();

    // Ajouter la commande et le bouton à la liste des subscriptions
    context.subscriptions.push(disposable, myStatusBarItem);
}

// Fonction de désactivation de l'extension
export function deactivate() {
    // Nettoyage si nécessaire
}
