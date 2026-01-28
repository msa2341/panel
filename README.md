# panel

## Formatação Automática de Código / Automatic Code Formatting

Para manter o código bem formatado, você pode usar o `autopep8`:

### Instalar autopep8
```bash
pip install autopep8
```

### Formatar automaticamente o código
```bash
autopep8 --in-place --aggressive --aggressive shoko.py
```

### Verificar se o código compila sem erros
```bash
python3 -m py_compile shoko.py
```

### Configuração do Editor
Este projeto inclui um arquivo `.editorconfig` para manter a consistência de formatação. Muitos editores suportam EditorConfig automaticamente.
