const vscode = require('vscode');
function activate(ctx) {
  const panelFor = () => vscode.window.createWebviewPanel(
      'mlirIr', 'MLIR / LLVM IR', vscode.ViewColumn.Beside, {});
  ctx.subscriptions.push(vscode.commands.registerCommand(
    'mlirLldb.showIr', async () => {
      const s = vscode.debug.activeDebugSession;
      if (!s) { vscode.window.showWarningMessage('No debug session'); return; }
      const sel = vscode.window.activeTextEditor.document.getText(
          vscode.window.activeTextEditor.selection);
      const r = await s.customRequest('mlirIr', { local: sel.trim() });
      const p = panelFor();
      p.webview.html = `<pre>${r.provenance !== 'real'
        ? `<b style="color:#c00">[${r.provenance}]</b>\n` : ''}${r.opName}
--- MLIR ---
${r.mlir}
--- LLVM IR ---
${r.llvmIr}</pre>`;
    }));
}
exports.activate = activate;