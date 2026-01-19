import * as vscode from 'vscode';
import axios from 'axios';
import { ChatProvider } from './chat-provider';

// Esta função é chamada quando sua extensão é ativada
export function activate(context: vscode.ExtensionContext) {
    console.log('Automação Linux Code Agent está ativa!');

    const chatProvider = new ChatProvider(context.extensionUri);

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(ChatProvider.viewType, chatProvider));

    // O comando deve bater com o que está no package.json
    let disposable = vscode.commands.registerCommand('linux-code-agent.executeTask', async () => {

        // 1. Captura o objetivo do usuário (Input Box)
        const objective = await vscode.window.showInputBox({
            placeHolder: 'Ex: Criar uma API REST básica em Python',
            prompt: 'Qual tarefa você quer que o Agent execute?'
        });

        if (!objective) {
            return; // Usuário cancelou
        }

        // 2. Feedback visual de carregamento
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Enviando tarefa para o Agent...",
            cancellable: false
        }, async (progress) => {
            
            try {
                // 3. Monta o Payload conforme o schema TaskBase do backend
                // Referência: app/schemas/task_base.py
                const payload = {
                    objective: objective,
                    context: {
                        // Podemos adicionar mais contexto do editor aqui no futuro
                        source: "vscode-extension"
                    }
                };

                // 4. Faz a chamada POST para o Backend (Porta 8000)
                // Referência: app/main.py
                const response = await axios.post('http://localhost:8000/tasks', payload);

                // 5. Sucesso! Mostra o ID da task criada
                const taskId = (response.data as any).id;
                vscode.window.showInformationMessage(`Tarefa criada com sucesso! ID: ${taskId}`);
                
            } catch (error: any) {
                // Tratamento de erro caso o backend esteja offline
                if (axios.isAxiosError(error)) {
                    vscode.window.showErrorMessage(`Erro ao conectar com o Agent: ${error.message}`);
                } else {
                    vscode.window.showErrorMessage('Erro inesperado ao criar tarefa.');
                }
            }
        });
    });

    context.subscriptions.push(disposable);
}

export function deactivate() {}